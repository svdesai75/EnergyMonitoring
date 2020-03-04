from connectionModel import *
import pytz
from datetime import datetime, timedelta
import logger

logger.logLevel = "debug"
engine = create_db_engine()
session = db_connect(engine)

units = session.query(RentalUnit).all()
lastUnit = units[-1]

handler = lastUnit.utilityBilling.handler

df = handler.download_line_items()
print(df)
