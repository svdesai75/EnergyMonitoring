#!/usr/bin/env python
from energyMonitorConfig import *
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError
import pymongo
import logger

##TODO implement check on MongoDB status
##TODO Factorize deviceData code from DataCache


class DataCache:
    def __init__(self):
        cfg = loadCfg()
        self.client = self.getDataCacheClient(cfg)
        self.db = self.client['dataCache']
        print(self.db)

    def getDataCacheClient(self,cfg):
        uri = cfg['devicedata']['dburi']
        client = MongoClient(uri)
        try:
            print(client.server_info())
            # logger.info(client.server_info())
        except ServerSelectionTimeoutError as err:
            logger.error("Could not connect to dataCache (uri = %s)" % uri)
            raise err

        return client

    def initDataCache(self):
        logger.info("Initializing dataCache")
        self.client.drop_database('dataCache')
        self.db=self.client['dataCache']

        ## create collection for device data
        deviceData = self.db.create_collection(name='deviceData')
        deviceData.create_index([("deviceType", 1), ("deviceID", 1),("timeUnit", 1),("timeStamp", 1)], unique=True)

        ## create collection for billing data
        self.db.create_collection(name='billingData')
        logger.info("done initializing dataCache")

    def getDeviceList(self):
        deviceData = self.db['deviceData']
        return deviceData.aggregate([{"$group": {"_id": {"deviceID": "$deviceID", "deviceType": "$deviceType"}}}])

    def addDeviceDataSingleRecord(self, deviceType, deviceID, timeUnit, timeStamp, record):
        deviceData=self.db['deviceData']
        # TODO: appropriate error handling for duplicate data (catch exception?)
        to_insert = {"deviceType": deviceType,
                     "deviceID": deviceID,
                     "timeUnit": timeUnit,
                     "timeStamp": timeStamp,
                     "data": record}
        deviceData.insert_one(to_insert)

    def addDeviceDataMultipleRecords(self, deviceType, deviceID, timeUnit, timeStampKey, records):
        for record in records:
            time_stamp = record[timeStampKey]
            self.addDeviceDataSingleRecord(deviceType,deviceID,timeUnit,time_stamp,record)

    ##function to fetch deviceData for given timespan
    def getDeviceData(self, deviceType, deviceID, start, end, timeUnit):
        lookup_key = {'deviceID': deviceID, 'timeUnit': timeUnit, 'timeStamp': {'$gte': start, '$lte': end}}
        device_data = self.db['deviceData'].find(lookup_key)
        return [d['data'] for d in device_data]

    ##in principle, we should have a get-earliest timestamp too, but in the current model,
    ##  we are building up a history, so that seems unlikely to be needed
    def getDeviceLatestTimestamp(self,deviceType, deviceID, timeUnit, minDate):
        if self.db['deviceData'].count()==0:
            return minDate

        filter = {'deviceID': deviceID, 'timeUnit': timeUnit}
        sort = [('timeStamp', pymongo.DESCENDING)]
        queryResult = self.db['deviceData'].\
            find_one(filter=filter, sort=sort, projection=['timeStamp'])['timeStamp']

        return max(minDate, queryResult)


    #function to add billing address