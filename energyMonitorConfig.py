#!/usr/bin/env python
import os
from configparser import ConfigParser

energy_monitor_dir = os.path.expandvars('${HOME}/.EnergyMonitor')
interface_db_connection_string = 'sqlite:///' + os.path.join(energy_monitor_dir, 'EnergyMonitor.db')


def load_cfg():
    
    cfg_file_name = os.path.join(energy_monitor_dir, 'config')

    cfg = ConfigParser()
    cfg.read(cfg_file_name)

    return cfg

