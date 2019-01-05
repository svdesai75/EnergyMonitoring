#!/usr/bin/env python
from dataCache import DataCache
import logger
import argparse, sys

logger.info("Loading Data Cache")
dataCache=DataCache()

def listDevices():
    print ("Listing Devices")
    deviceList=dataCache.getDeviceList()
    for d in deviceList:
        print(d)

def actionNotSupported():
    print ("Action not supported")

parser=argparse.ArgumentParser(prog=sys.argv[0], description="Manage/inspect local data Cache")
subParser=parser.add_subparsers(title="Action",dest="action")
subParser.required=True

subParsers={}
subParsers[         "initDB"]={"help":               "Re-initialize DB","func":dataCache.initDataCache}
subParsers[    "listDevices"]={"help":                   "List devices","func":listDevices}
subParsers[    "clearDevice"]={"help": "Clear data for specific device","func":actionNotSupported}
subParsers[     "viewDevice"]={"help":  "View data for specific device","func":actionNotSupported}

for cmd in subParsers:
    help=subParsers[cmd]["help"]
    sp=subParser.add_parser(cmd, help=help)

x=parser.parse_args()
subParsers[x.action]['func']()


#dataCache.initDataCache()


