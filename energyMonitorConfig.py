#!/usr/bin/env python
import os
import sqlalchemy
from configparser import ConfigParser

energyMonitorDir=os.path.expandvars('${HOME}/.EnergyMonitor')
energyMonitorDB='sqlite:///'+os.path.join(energyMonitorDir,'EnergyMonitor.db')

def loadCfg():
    
    cfgFileName=os.path.join(energyMonitorDir,'config')

    cfg=ConfigParser()
    cfg.read(cfgFileName)

    return cfg

#def dbConnect(cfg):
#
#    dbFileName=
