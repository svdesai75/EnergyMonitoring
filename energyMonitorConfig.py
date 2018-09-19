#!/usr/bin/env python
import os
from configparser import ConfigParser

energyMonitorDir=os.path.expandvars('${HOME}/.EnergyMonitor')
interfaceDBConnectionString= 'sqlite:///' + os.path.join(energyMonitorDir, 'EnergyMonitor.db')

def loadCfg():
    
    cfgFileName=os.path.join(energyMonitorDir,'config')

    cfg=ConfigParser()
    cfg.read(cfgFileName)

    return cfg

#def dbConnect(cfg):
#
#    dbFileName=
