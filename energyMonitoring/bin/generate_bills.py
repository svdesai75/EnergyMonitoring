from energyMonitoring.connectionModel import *
from energyMonitoring import logger
import argparse
import re
import numpy as np
import pandas as pd

logger.log_level = "info"


class BillGenerator:
    def __init__(self, units):

        self.units = units

        self.cost_category_patterns = dict()
        self.cost_category_patterns["energy"] = ["^Energy Charge [A-Z,a-z]*_[A-Z,a-z]"]
        self.cost_category_patterns["refund"] = ["^Refund as requested"]
        self.cost_category_patterns["incentives"] = ["^AC Rewards Annual Incen"]

        self.bill_line_items = units[0].utilityBilling.handler.download_line_items()

        billing_start = self.bill_line_items.bill_start_date.min()
        billing_end = self.bill_line_items.bill_end_date.max()

        logger.info("Downloading generation data")
        self.generation_data = units[0].generationMonitor.handler.batch_download(billing_start, billing_end, "HOUR")

        logger.info("Downloading consumption data")
        self.consumption_data = None
        for unit in units:
            consumption_data = unit.consumptionMonitor.handler.batch_download(billing_start, billing_end, "HOUR")
            consumption_data["unit_name"] = unit.unitName
            if self.consumption_data is None:
                self.consumption_data = consumption_data
            else:
                self.consumption_data = self.consumption_data.append(consumption_data, ignore_index=True)

    def transform_line_items(self, row):
        category_costs = {k: 0 for k in self.cost_category_patterns.keys()}
        category_costs["flat"] = 0

        for f in row.index:
            if not f.endswith("_cost"):
                continue

            cost_category = "flat"
            for k in self.cost_category_patterns.keys():
                match = any([re.match(p, f) for p in self.cost_category_patterns[k]])
                if match:
                    cost_category = k
                    break

            value = row[f]
            if not np.isnan(value):
                category_costs[cost_category] += value

        results = dict()
        results["start_date"] = row["bill_start_date"]
        results["end_date"] = row["bill_end_date"]
        results["total_energy"] = row["bill_volume"]
        results["total"] = row["bill_total"]
        for k in category_costs.keys():
            results_key = f'{k}_cost'
            results[results_key] = category_costs[k]

        results = pd.DataFrame([results])
        results["effective_rate"] = results.eval("energy_cost/total_energy")

        return results.iloc[0]

    def summarize_device_data(self, row, unit):

        offset = pd.Timedelta(13, 'H')
        period_start = row.start_date + offset
        period_end = row.end_date + offset

        results = dict()
        results["unit_name"] = unit.unitName
        results["start_date"] = row.start_date
        results["billing_fraction"] = unit.billingFraction

        consumption_query = "start >= @period_start and end <= @period_end and unit_name == @unit.unitName"
        consumption = self.consumption_data.query(consumption_query).consumptionEnergy.sum() * unit.consumptionFraction
        results["consumption"] = consumption

        generation_query = "@period_start  <= date < @period_end"
        generation = self.generation_data.query(generation_query).Production.sum() * unit.generationFraction
        results["generation"] = generation
        results["device_net"] = consumption - generation
        return pd.Series(results)

    def calc_unit_data(self, unit):

        bill_summary = pd.concat([self.bill_line_items.apply(self.transform_line_items, axis=1)])
        device_data = bill_summary.apply(lambda x: self.summarize_device_data(x, unit), axis=1)
        unit_data = bill_summary.merge(device_data, on="start_date")

        return unit_data


def generate_bills(property_id):
    db_engine = create_db_engine()
    session = db_connect(db_engine)

    units = session.query(RentalUnit).filter(RentalUnit.propertyID == property_id)
    bill_generator = BillGenerator(units)

    unit_data = pd.concat([bill_generator.calc_unit_data(unit) for unit in units])
    correction_factor = unit_data.groupby("start_date"). \
        agg(total_energy=("total_energy", "max"),
            device_net=("device_net", "sum")). \
        eval("total_energy/device_net").\
        reset_index()
    correction_factor.columns = ['start_date', 'correction_factor']

    unit_bill_expression = "billing_fraction * (flat_cost+ incentives_cost) + unit_energy_cost"
    unit_data = unit_data.merge(correction_factor, on="start_date").\
        assign(unit_energy=lambda x: x.eval("correction_factor * device_net"),
               unit_energy_cost=lambda x: x.eval("unit_energy * effective_rate"),
               unit_total_cost=lambda x: x.eval(unit_bill_expression))
    return unit_data


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="generate electricity bills for all units in a property")
    parser.add_argument("-p", "--property", help="property to generate bills for")
    args = parser.parse_args()

    bills = generate_bills(args.property)
    print(bills)
