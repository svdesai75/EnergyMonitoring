import pandas as pd
import solaredge
import logger


class SolarEdgeClient:

    def __init__(self,cfg,monitorID,timeZone):

        self.siteID = monitorID
        key         = cfg.get("solaredge","key")

        self.client =  solaredge.Solaredge(key)

        #thus far, there appears to be no need to make use of this, but we at least ensure the field is there
        # in case this turns out not to be the case
        self.timeZone=timeZone

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