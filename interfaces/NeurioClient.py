#!/usr/bin/env python
import neurio
import pandas as pd

class NeurioClient:

    def __init__(self,cfg,monitorID):

        self.monitorID=monitorID

        clientID=cfg.get("neurio","clientID")
        secret=cfg.get("neurio","secret")

        tp = neurio.TokenProvider(key=clientID, secret=secret)
        self.client=neurio.Client(token_provider=tp)

    def fetchConsumptionData(self, start, end, timeUnit):

        timeSpan=end - start
        if timeUnit == 'QUARTER_OF_AN_HOUR' and timeSpan > 1:
            raise Exception('Granularity of QUARTER_OF_AN_HOUR does not support time span > 1 day')

        granularityInfo={}
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
        df.start = pd.to_datetime(df.start).dt.tz_localize('America/Chicago').dt.tz_convert("America/Chicago")
        df.end   = pd.to_datetime(  df.end).dt.tz_localize('America/Chicago').dt.tz_convert("America/Chicago")

        return df


# TODO: add interface to utilityAPI