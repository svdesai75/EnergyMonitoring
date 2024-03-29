from energyMonitoring.connectionModel import *
import pytz
from datetime import datetime, timedelta
from energyMonitoring import logger

logger.log_level = "debug"
engine = create_db_engine()
session = db_connect(engine)

units = session.query(RentalUnit).all()
lastUnit = units[-1]

handler = lastUnit.utilityBilling.handler

df = handler.download_line_items()
print(df)
