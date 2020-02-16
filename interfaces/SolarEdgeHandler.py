import pandas as pd
import solaredge
import logger


class SolarEdgeHandler:

    def __init__(self, cfg, monitor_id, time_zone, activation_time):

        self.site_id = monitor_id
        self.activationTime = activation_time

        key         = cfg.get("solaredge", "key")

        self.client =  solaredge.Solaredge(key)

        # thus far, there appears to be no need to make use of this, but we at least ensure the field is there
        # in case this turns out not to be the case
        self.timeZone = time_zone

    def download(self, start, end, time_unit):

        logger.debug("Fetching production data")
        logger.debug(self.site_id)
        logger.debug("{} to {}".format(start.isoformat(), end.isoformat()))

        valid_granularities=['QUARTER_OF_AN_HOUR', 'HOUR', 'DAY', 'WEEK', 'MONTH', 'YEAR']
        if time_unit not in valid_granularities:
            raise Exception('Invalid time_unit {}'.format(time_unit))

        site_energy = self.client.get_energy_details_dataframe(site_id=self.site_id,
                                                               start_time=start,
                                                               end_time=end,
                                                               time_unit=time_unit)
        site_energy.reset_index(level=0, inplace=True)
        site_energy.date = pd.to_datetime(site_energy.date)
        site_energy.Production *= (1/1000.)  # convert Wh -> kWH
        return site_energy
