#!/usr/bin/env python
from connectionModel import *
import pytz
from datetime import datetime, timedelta
import logger

logger.logLevel = "debug"
engine = createDBEngine()
session = dbConnect(engine)

units = session.query(RentalUnit).all()
lastUnit = units[-1]

nc = lastUnit.consumptionMonitor.client
monitor_id = lastUnit.consumptionMonitor.client.monitor_id
print(lastUnit.unitName)
print(nc)
print(monitor_id)


def make_date_time(year, month, day, hour, tz):
    tz_info = pytz.timezone(tz)
    return tz_info.localize(datetime(year=year, month=month, day=day, hour=hour))


startDate = make_date_time(year=2020, month=1, day=14, hour=21, tz=nc.time_zone)
endDate   = make_date_time(year=2020, month=1, day=15, hour=21, tz=nc.time_zone)

print("Start: ", startDate)
print("  End: ",   endDate)
hours = (endDate - startDate).total_seconds()/3600
print("Duration (h): ", hours)

dfSamples = nc.download_as_df(startDate, endDate, "HOUR")
print(dfSamples)
