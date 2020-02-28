#!/usr/bin/env python
import os
from configparser import ConfigParser

energyMonitorDir = os.path.expandvars('${HOME}/.EnergyMonitor')
interfaceDBConnectionString = 'sqlite:///' + os.path.join(energyMonitorDir, 'EnergyMonitor.db')


def loadCfg():
    
    cfg_file_name = os.path.join(energyMonitorDir,'config')

    cfg = ConfigParser()
    cfg.read(cfg_file_name)

    return cfg

