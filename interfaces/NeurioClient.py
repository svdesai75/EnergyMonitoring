#!/usr/bin/env python
import os
import neurio
import pandas as pd
import pytz

from energyMonitorConfig import energyMonitorDir
import logger

class NeurioClient:

    def __init__(self,cfg,monitorID, timeZone):

        logger.debug("Instantiating Neurio Client for monitor %s" % monitorID)
        self.monitorID=monitorID
        self.timeZone=timeZone

        clientID=cfg.get("neurio","clientID")
        secret=cfg.get("neurio","secret")

        tp = neurio.TokenProvider(key=clientID, secret=secret)
        self.client=neurio.Client(token_provider=tp)

        self.dataLoc=os.path.join(energyMonitorDir,"neurio",monitorID)
        if not os.path.isdir(self.dataLoc):
            os.makedirs(self.dataLoc)

        logger.debug("Neurio client data dir = %s" % self.dataLoc)

    def fetchConsumptionData(self, start, end, timeUnit):

        logger.debug("Fetching consumption data")
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

        timeSpan=end - start
        if timeUnit == 'QUARTER_OF_AN_HOUR' and timeSpan > 1:
            raise Exception('Granularity of QUARTER_OF_AN_HOUR does not support time span > 1 day')

        granularityInfo={}
        granularityInfo[            'MINUTE'] = ('minutes',  5)
        granularityInfo['QUARTER_OF_AN_HOUR'] = ('minutes', 15)
        granularityInfo[              'HOUR'] = (  'hours',  1)
        granularityInfo[               'DAY'] = (   'days',  1)
        granularityInfo[             'MONTH'] = ( 'months',  1)
        granularityInfo[              'YEAR'] = (  'years',  1)

        if timeUnit not in granularityInfo.keys():
            raise Exception ('Invalid time_unit %s' % timeUnit)

        granularity,frequency = granularityInfo[timeUnit]
        raw=self.client.get_samples_stats(sensor_id=self.monitorID,
                                          start=start.isoformat(),
                                          end=end.isoformat(),
                                          granularity=granularity,
                                          frequency=frequency)

        df=pd.DataFrame(raw)
        df.consumptionEnergy *= (1/1000./3600.) #convert Ws -> kWH

        ##raw start and end dates are returned in GMT:  eg '2018-08-08T00:50:00.000Z'
        ## after being put into data frame, formatted like
        ## convert to local timezone, eg:2018-08-08T00:45:00.000Z, 2018-08-08T00:45:03.314Z
        ## example format afterwards is '2018-08-08 01:10:00-05:00'
        df.start = pd.to_datetime(df.start).dt.tz_localize('UTC').dt.tz_convert(self.timeZone)
        df.end   = pd.to_datetime(  df.end).dt.tz_localize('UTC').dt.tz_convert(self.timeZone)

        return df

# TODO: add interface to utilityAPI