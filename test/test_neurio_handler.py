#!/usr/bin/env python
from connectionModel import *
import pytz
from datetime import datetime, timedelta
import logger

TimeZone = 'America/Chicago'

logger.logLevel = "debug"
engine = createDBEngine()
session = dbConnect(engine)

units = session.query(RentalUnit).all()
lastUnit = units[-1]

nc = lastUnit.consumptionMonitor.client
monitorID = lastUnit.consumptionMonitor.client.monitorID
print(lastUnit.unitName)
print(nc)
print(monitorID)


def make_date_time(year, month, day, hour, tz):
    tz_info = pytz.timezone(tz)
    return tz_info.localize(datetime(year=year,month=month,day=day,hour=hour))


startDate = make_date_time(year=2020, month=1, day=14, hour=21, tz='America/Chicago')
endDate   = make_date_time(year=2020, month=1, day=15, hour=21, tz='America/Chicago')

print("Start: ", startDate)
print("  End: ",   endDate)
hours = (endDate - startDate).total_seconds()/3600
print("Duration (h): ", hours)

dfSamples = nc.download_as_df(startDate, endDate, "HOUR")
print(dfSamples)
