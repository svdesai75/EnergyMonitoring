#!/usr/bin/env python
from energyMonitorConfig import *
import pandas as pd

import neurio
import solaredge

#TODO make consistent granularity specifiers

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

class NeurioClient:

    def __init__(self,cfg,monitorID):

        self.monitorID=monitorID

        clientID=cfg.get("neurio","clientID")
        secret=cfg.get("neurio","secret")

        tp = neurio.TokenProvider(key=clientID, secret=secret)
        self.client=neurio.Client(token_provider=tp)

    def fetchConsumptionData(self, start, end, granularity):

        raw=self.client.get_samples_stats(sensor_id=self.monitorID,
                                          start=start.isoformat(),
                                          end=end.isoformat(),
                                          granularity=granularity)

        df=pd.DataFrame(raw)
        df.start = pd.to_datetime(df.start).dt.tz_localize('America/Chicago').dt.tz_convert("America/Chicago")
        df.end   = pd.to_datetime(  df.end).dt.tz_localize('America/Chicago').dt.tz_convert("America/Chicago")

        return df


# TODO: add interface to utilityAPI