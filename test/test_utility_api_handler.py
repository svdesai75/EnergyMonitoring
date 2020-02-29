from connectionModel import *
import pytz
from datetime import datetime, timedelta
import logger

logger.logLevel = "debug"
engine = createDBEngine()
session = dbConnect(engine)

units = session.query(RentalUnit).all()
lastUnit = units[-1]

handler = lastUnit.utilityBilling.handler

df = handler.download_lineitems()
print(df)
