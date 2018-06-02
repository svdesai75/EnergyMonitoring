# EnergyMonitoring

I own a duplex in Minneapolis, where I have had solar panels installed
on the roof.  When I got the installation done, I had to go from separate
meters for each unit to a single net production meter (as well as a production
meter for the panels).  I would still like to bill tenants individually to give
them incentive to reduce their electricity consumption.

I have a neur.io Home Energy Monitor installed on the breaker box for each unit, and a Solar Edge inverter,
each with APIs.  I rely on the following neurio package:
https://pypi.org/project/neurio/

There is also a packaged for interfacing with the Solar Edge inverters:
https://pypi.org/project/solaredge/


The APIs are documented at:
https://www.solaredge.com/sites/default/files/se_monitoring_api.pdf
https://api-docs.neur.io/


Tool to extract power usage from multiple neur.io Home Energy Monitors  at same house and single meter to compute individual tenant usage

### Setup
#### Setup virtual environment
```commandline
pyvenv env
source env/bin/activate
pip install --upgrade pip
```

#### Install packages
```commandline
pip install neurio
pip install  solaredge
pip install SQLAlchemy
pip install pandas
```
