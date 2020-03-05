import pandas as pd
import solaredge
import logger


class SolarEdgeHandler:

    def __init__(self, cfg, monitor_id, time_zone, activation_time):

        self.site_id = monitor_id
        self.activationTime = activation_time

        key         = cfg.get("solaredge", "key")

        self.client = solaredge.Solaredge(key)

        # thus far, there appears to be no need to make use of this, but we at least ensure the field is there
        # in case this turns out not to be the case
        self.time_zone = time_zone
        self.query_period = pd.Timedelta(31, 'D')

    def download(self, start, end, time_unit):

        logger.debug("Fetching production data")
        logger.debug(self.site_id)
        logger.debug("{} to {}".format(start.isoformat(), end.isoformat()))

        valid_time_units = ['QUARTER_OF_AN_HOUR', 'HOUR', 'DAY', 'WEEK', 'MONTH', 'YEAR']
        if time_unit not in valid_time_units:
            raise Exception('Invalid time_unit {}'.format(time_unit))

        site_energy = self.client.get_energy_details_dataframe(site_id=self.site_id,
                                                               start_time=start,
                                                               end_time=end,
                                                               time_unit=time_unit)
        site_energy.reset_index(level=0, inplace=True)
        site_energy.date = pd.to_datetime(site_energy.date)
        site_energy.Production *= (1/1000.)  # convert Wh -> kWH
        return site_energy

    def batch_download(self, start, end, time_unit):

        out_df = None
        query_start = start
        while query_start < end:
            query_end = min(query_start + self.query_period, end)
            tmp_df = self.download(query_start, query_end, time_unit)
            if out_df is None:
                out_df = tmp_df
            else:
                out_df = out_df.append(tmp_df, ignore_index=True)

            query_start = query_end

        return out_df
