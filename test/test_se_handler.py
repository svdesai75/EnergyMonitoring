#!/usr/bin/env python
from connectionModel import *
from datetime import datetime, timedelta

engine = createDBEngine()
session = dbConnect(engine)

units = session.query(RentalUnit).all()
lastUnit = units[-1]

se = lastUnit.generationMonitor

print(lastUnit.unitName)
print(se)
end_date = datetime.now()
start_date = end_date - timedelta(days=1)
print(start_date)
print(end_date)
print(se.download(start_date, end_date, 'HOUR'))

