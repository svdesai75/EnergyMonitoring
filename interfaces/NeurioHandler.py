#!/usr/bin/env python
import os
import neurio
from dataCache import DataCache
import pandas as pd
import pytz
from datetime import datetime, timedelta

from energyMonitorConfig import energyMonitorDir
import logger

# for granularity passed to API, if grnularity is minutes, frequency must be multiple of 5
granularityInfo = {}
granularityInfo['MINUTE']             = ('minutes',  5,    1)  # max 1 day timespan
granularityInfo['QUARTER_OF_AN_HOUR'] = ('minutes', 15,    1)  # max 1 day timespan
granularityInfo['HOUR']               = (  'hours',  1,   31)  # max 31 day timespan
granularityInfo['DAY']                = (   'days',  1,   92)  # max 92 day timespan
granularityInfo['MONTH']              = ( 'months',  1,  365)  # max 1 year timespan
granularityInfo['YEAR']               = (  'years',  1, 3650)  # max 10y timespan

class NeurioHandler:

    def __init__(self,cfg,monitorID, timeZone, activationTime):

        logger.debug("Instantiating Neurio Client for monitor %s" % monitorID)
        self.monitorType="neurio"
        self.monitorID=monitorID
        self.timeZone=timeZone
        self.activationTime=activationTime

        clientID=cfg.get(self.monitorType,"clientID")
        secret=cfg.get(self.monitorType,"secret")

        tp = neurio.TokenProvider(key=clientID, secret=secret)
        self.client=neurio.Client(token_provider=tp) ## interface to remote data
        self.dataCache=DataCache()

        self.dataLoc=os.path.join(energyMonitorDir,"data","neurio",monitorID)
        if not os.path.isdir(self.dataLoc):
            os.makedirs(self.dataLoc)

        logger.debug("Neurio client data dir = %s" % self.dataLoc)

    def getConsumptionData(self, start, end, timeUnit):
        raw=self.dataCache.getDeviceData(self.monitorType,self.monitorID,start,end,timeUnit)

        df=pd.DataFrame(raw)
        df.consumptionEnergy *= (1/1000./3600.) #convert Ws -> kWH

        ##raw start and end dates are returned in GMT:  eg '2018-08-08T00:50:00.000Z'
        ## after being put into data frame, formatted like
        ## convert to local timezone, eg:2018-08-08T00:45:00.000Z, 2018-08-08T00:45:03.314Z
        ## example format afterwards is '2018-08-08 01:10:00-05:00'
        df.start = pd.to_datetime(df.start).dt.tz_localize('UTC').dt.tz_convert(self.timeZone)
        df.end   = pd.to_datetime(  df.end).dt.tz_localize('UTC').dt.tz_convert(self.timeZone)

        return df

    def downloadData(self, start, end, timeUnit):

        logger.debug("download consumption data")
        logger.debug(self.monitorID)
        logger.debug("%s to %s" %(start.isoformat(),end.isoformat()))

        if start.tzinfo==None:
            logger.warn("start date has no timezone info")
        if end.tzinfo==None:
            logger.warn("end date has no timezone info")

        start=start.astimezone(pytz.utc)
        end=end.astimezone(pytz.utc)
        logger.debug("After formatting times:")
        logger.debug("%s to %s" %(start.isoformat(),end.isoformat()))
        d=end-start
        logger.debug("deltaTime %f" %  d.total_seconds()/3600./24)
        timeSpan=end - start
        if timeUnit == 'QUARTER_OF_AN_HOUR' and timeSpan > 1:
            raise Exception('Granularity of QUARTER_OF_AN_HOUR does not support time span > 1 day')

        if timeUnit not in granularityInfo.keys():
            raise Exception ('Invalid time_unit %s' % timeUnit)

        granularity,frequency, maxSpan = granularityInfo[timeUnit]
        raw=self.client.get_samples_stats(sensor_id=self.monitorID,
                                          start=start.isoformat(),
                                          end=end.isoformat(),
                                          granularity=granularity,
                                          frequency=frequency)
        ##TODO Implement error checking on response

        #self.persistData(raw,timeUnit)
        return (raw)

    def getLatestTimestamp(self,timeUnit):
        latestTimestamp=self.dataCache.

    def updateDataCache(self,timeUnit):

        granularity, frequency, maxSpan = granularityInfo[timeUnit]

        latestTimeStamp=self.dataCache.getDeviceLatestTimestamp(self.monitorType,self.monitorID,timeUnit)
        currentTimeStamp=datetime.now()
        while latestTimeStamp < currentTimeStamp:
            start=something
            end=start + timedelta(days=maxSpan)

            data=self.downloadData(start,end,timeUnit)
            self.dataCache.addDeviceDataMultipleRecords(self.monitorType, self.monitorID, timeUnit, 'start', data)

            latestTimeStamp = self.dataCache.getDeviceLatestTimestamp(self.monitorType, self.monitorID, timeUnit)
