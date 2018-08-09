import pandas as pd
import solaredge
import logger


class SolarEdgeClient:

    def __init__(self,cfg,monitorID):

        self.siteID = monitorID
        key         = cfg.get("solaredge","key")

        self.client =  solaredge.Solaredge(key)

    def getProductionData(self, start, end, timeUnit):

        logger.debug("Fetching production data")
        logger.debug(self.siteID)
        logger.debug("%s to %s" %(start.isoformat(),end.isoformat()))

        validGranularities=['QUARTER_OF_AN_HOUR', 'HOUR', 'DAY', 'WEEK', 'MONTH', 'YEAR']
        if timeUnit not in validGranularities:
            raise Exception('Invalid time_unit %s' % timeUnit)

        siteEnergy=self.client.get_energy_details_dataframe(site_id=self.siteID, start_time=start, end_time=end, time_unit=timeUnit)
        siteEnergy.reset_index(level=0, inplace=True)
        siteEnergy.date=pd.to_datetime(siteEnergy.date)
        siteEnergy.Production *= (1/1000.) #convert Wh -> kWH
        return siteEnergy