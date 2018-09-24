#!/usr/bin/env python
from energyMonitorConfig import *
from pymongo import MongoClient
import pymongo

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
        # TODO: appropriate error handling for duplicate data (catch exception?)
        toInsert={"deviceType":deviceType, "deviceID":deviceID, "timeUnit":timeUnit,"timeStamp": timeStamp, "data":record}
        deviceData.insert_one(toInsert)

    def addDeviceDataMultipleRecords(self, deviceType, deviceID, timeUnit, timeStampKey, records):
        for record in records:
            timeStamp=record[timeStampKey]
            self.addDeviceDataSingleRecord(deviceType,deviceID,timeUnit,timeStamp,record)

    ##function to fetch deviceData for given timespan
    def getDeviceData(self, deviceType, deviceID, timeUnit, start, end):
        deviceData=self.db['deviceData'].find({'deviceID':deviceID,  'deviceID':deviceID, 'timeUnit':timeUnit, 'timeStamp':{'$gte':start, '$lte':end}})
        return [d['data'] for d in deviceData]

    ##in principle, we should have a get-earliest timestamp too, but in the current model,
    ##  we are building up a history, so that seems unlikely to be needed
    def getDeviceLatestTimestamp(self,deviceType, deviceID, timeUnit):
        filter={'deviceID':deviceID,  'deviceID':deviceID, 'timeUnit':timeUnit}
        sort=[('timeStamp',pymongo.DESCENDING)]
        queryResult=self.db['deviceData'].\
            find_one(filter=filter, sort=sort,projection=['timeStamp'])['timeStamp']

        return queryResult


    #function to add billing address