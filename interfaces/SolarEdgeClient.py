import pandas as pd
import solaredge


class SolarEdgeClient:

    def __init__(self,cfg,monitorID):

        self.siteID = monitorID
        key         = cfg.get("solaredge","key")

        self.client =  solaredge.Solaredge(key)

    def getProductionData(self, start, end):
        siteEnergy=self.client.get_energy_details_dataframe(site_id=self.siteID,start_time=start,end_time=end,time_unit="HOUR")
        siteEnergy.reset_index(level=0, inplace=True)
        siteEnergy.date=pd.to_datetime(siteEnergy.date)
        return siteEnergy