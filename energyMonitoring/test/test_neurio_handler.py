#!/usr/bin/env python
from energyMonitoring.connectionModel import *
import pytz
from datetime import datetime, timedelta
from energyMonitoring import logger

logger.log_level = "debug"
engine = create_db_engine()
session = db_connect(engine)

units = session.query(RentalUnit).all()
lastUnit = units[-1]

handler = lastUnit.consumptionMonitor.handler
monitor_id = handler.monitor_id
print(lastUnit.unitName)
print(handler)
print(monitor_id)


def make_date_time(year, month, day, hour, tz):
    tz_info = pytz.timezone(tz)
    return tz_info.localize(datetime(year=year, month=month, day=day, hour=hour))


startDate = make_date_time(year=2020, month=1, day=14, hour=21, tz=handler.time_zone)
endDate   = make_date_time(year=2020, month=1, day=15, hour=21, tz=handler.time_zone)

print("Start: ", startDate)
print("  End: ",   endDate)
hours = (endDate - startDate).total_seconds()/3600
print("Duration (h): ", hours)

dfSamples = handler.download(startDate, endDate, "HOUR")
print(dfSamples)
