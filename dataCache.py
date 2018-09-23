#!/usr/bin/env python
from energyMonitorConfig import *
from pymongo import MongoClient

class DataCache:
    def __init__(self):
        cfg=loadCfg()
        self.client=self.getDataCacheClient(cfg)
        self.db=self.client['dataCache']

    def getDataCacheClient(self,cfg):
        uri=cfg['devicedata']['dburi']
        client=MongoClient(uri)
        return client

    def initDataCache(self):
        self.client.drop_database('dataCache')
        self.db=self.client['dataCache']

        ## create collection for device data
        deviceData=self.db.create_collection(name='deviceData')
        deviceData.create_index([("deviceType",1), ("deviceID",1),("timeUnit",1),("timeStamp", 1)], unique=True)

        ## create collection for billing data
        self.db.create_collection(name='billingData')

    def addDeviceDataSingleRecord(self,deviceType,deviceID, timeUnit,timeStamp, record):
        deviceData=self.db['deviceData']
        #check if record with time stamp exists:
        #  if yes, print warning message and skip
        #  #if no, insert
        toInsert={"deviceType":deviceType, "deviceID":deviceID, "timeUnit":timeUnit,"timeStamp": timeStamp, "data":record}
        deviceData.insert_one(toInsert)

    def addDeviceDataMultipleRecords(self, deviceType, deviceID, timeUnit, timeStampKey, records):
        for record in records:
            timeStamp=record[timeStampKey]
            self.addDeviceDataSingleRecord(deviceType,deviceID,timeUnit,timeStamp,record)

    ##function to fetch deviceData for given timespan
    ##function to get latest timestamp

    #function to add billing address