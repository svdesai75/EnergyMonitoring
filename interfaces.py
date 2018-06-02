#!/usr/bin/env python
from energyMonitorConfig import *
import pandas as pd

import neurio
import solaredge

class solarEdgeClient:
    
    def __init__(self,cfg,monitorID):

        self.siteID = monitorID
        key         = cfg.get("solaredge","key")

        self.client =  solaredge.Solaredge(key)

    def getEnergyProduction(self,start,end):
        siteEnergy=self.client.get_energy_details_dataframe(site_id=self.siteID,start_time=pd.to_datetime(start),end_time=pd.to_datetime(end),time_unit="HOUR")
        return siteEnergy
     
def loadNeurioClient(cfg):
    
    clientID=cfg.get("neurio","clientID")
    secret=cfg.get("neurio","secret")

    tp = neurio.TokenProvider(key=clientID, secret=secret)

    return  neurio.Client(token_provider=tp)
