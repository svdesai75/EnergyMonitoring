#!/usr/bin/env python
import neurio
import pandas as pd
import pytz
import time

import logger

# for granularity passed to API, if minutes, frequency must be multiple of 5
granularityInfo = dict()
granularityInfo['MINUTE']             = ('minutes',  5,    1)  # max 1 day timespan
granularityInfo['QUARTER_OF_AN_HOUR'] = ('minutes', 15,    1)  # max 1 day timespan
granularityInfo['HOUR']               = (  'hours',  1,   31)  # max 31 day timespan
granularityInfo['DAY']                = (   'days',  1,   92)  # max 92 day timespan
granularityInfo['MONTH']              = ( 'months',  1,  365)  # max 1 year timespan
granularityInfo['YEAR']               = (  'years',  1, 3650)  # max 10y timespan


class NeurioHandler:

    def __init__(self, cfg, monitor_id, time_zone, activation_time):

        logger.debug("Instantiating Neurio Client for monitor %s" % monitor_id)
        self.monitorType = "neurio"
        self.monitor_id = monitor_id
        self.time_zone = time_zone
        self.activation_time = activation_time
        self.query_period = pd.Timedelta(31, 'D')

        client_id = cfg.get(self.monitorType, "clientID")
        secret = cfg.get(self.monitorType, "secret")

        tp = neurio.TokenProvider(key=client_id, secret=secret)
        self.client = neurio.Client(token_provider=tp)  # interface to remote data

    def download_raw(self, start, end, time_unit):

        logger.debug("download consumption data")
        logger.debug(self.monitor_id)
        logger.debug("{} to {}".format(start.isoformat(), end.isoformat()))

        if start.tzinfo is None:
            logger.warn("start date has no timezone info")
        if end.tzinfo is None:
            logger.warn("end date has no timezone info")

        start = start.astimezone(pytz.utc)
        end   = end.astimezone(pytz.utc)
        logger.debug("After formatting times:")
        logger.debug("{} to {}".format(start.isoformat(), end.isoformat()))
        time_delta = (end - start).total_seconds()/3600./24
        logger.debug("deltaTime %f" % time_delta)
        if time_unit == 'QUARTER_OF_AN_HOUR' and time_delta > 1:
            raise Exception('Granularity of QUARTER_OF_AN_HOUR does not support time span > 1 day')

        if time_unit not in granularityInfo.keys():
            raise Exception('Invalid time_unit %s' % time_unit)

        granularity, frequency, max_span = granularityInfo[time_unit]
        raw = self.client.get_samples_stats(sensor_id=self.monitor_id,
                                            start=start.isoformat(),
                                            end=end.isoformat(),
                                            granularity=granularity,
                                            frequency=frequency)
        # TODO Implement error checking on response
        if type(raw) == dict:
            # other keys = status, code
            # status  = raw["status"]
            message = raw["message"]
            raise ConnectionRefusedError(message)

        return raw

    def download(self, start, end, time_unit):
        raw_data = self.download_raw(start, end, time_unit)

        df = pd.DataFrame(raw_data)
        df.consumptionEnergy *= (1/1000./3600.)  # convert Ws -> kWH

        # raw start and end dates are returned in UTC:  eg '2018-08-08T00:50:00.000Z'
        #  after being put into data frame, need to convert to local timezone
        #  e.g. '2018-08-08 01:10:00-05:00'
        df.start = pd.to_datetime(df.start).dt.tz_convert(self.time_zone)
        df.end   = pd.to_datetime(  df.end).dt.tz_convert(self.time_zone)

        return df

    def batch_download(self, start, end, time_unit):

        out_df = None
        query_start = start
        while query_start < end:
            query_end = min(query_start + self.query_period, end)
            tmp_df = self.download(query_start, query_end, time_unit)
            if out_df is None:
                out_df = tmp_df
            else:
                out_df = out_df.append(tmp_df, ignore_index=True)

            query_start = query_end
            time.sleep(1)

        return out_df
