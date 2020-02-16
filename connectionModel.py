#!/usr/bin/env python
from sqlalchemy import Column, ForeignKey, Integer, Float, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import orm
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from energyMonitorConfig import *
from interfaces import SolarEdgeHandler
from interfaces import NeurioHandler

import pandas as pd

Base = declarative_base()


def createDBEngine():
    return create_engine(interfaceDBConnectionString)


def dbConnect(engine):
    Base.metadata.bind = engine 
    dbSession = sessionmaker(bind=engine)
    session = dbSession()
    return session


# corresponds to a solar generation monitor
class GenerationMonitor(Base):
    __tablename__ = 'generationMonitor'
    
    id            = Column(String(250), nullable=False, primary_key=True)
    monitorType   = Column(String(250), nullable=False)
    timeZone      = Column(String(250), nullable=False)
    activationTime= Column(String(250), nullable=False)

    @orm.reconstructor
    def init_on_load(self):
        if self.monitorType=='SolarEdge':
            self.client=SolarEdgeHandler.SolarEdgeHandler(cfg, self.id, self.timeZone, self.activationTime)
        else:
            raise Exception("Unknown monitor type %s" % self.monitorType)

    def download(self, start, end, time_unit):

        data = self.client.download(start, end, time_unit)
        return data


# corresponds to a neurio home energy monitor or similar
class ConsumptionMonitor(Base):
    __tablename__ = 'consumptionMonitor'
    
    id            = Column(String(250), nullable=False, primary_key=True)
    monitorType   = Column(String(250), nullable=False)
    timeZone      = Column(String(250), nullable=False)
    activationTime= Column(String(250), nullable=False)

    @orm.reconstructor
    def init_on_load(self):
        if self.monitorType == 'Neurio':
            self.client = NeurioHandler.NeurioHandler(cfg, self.id, self.timeZone, self.activationTime)
        else:
            raise Exception("Unknown monitor type %s" % self.monitorType)

    def download(self, start, end, time_unit):
        data = self.client.download(start, end, time_unit)
        return data

# Todo: Add interface to utilityAPI


class RentalUnit(Base):
    __tablename__ = 'rentalUnit'
    unitName = Column(String(250), nullable=False, primary_key=True)
    
    generationMonitorID = Column(String(250), ForeignKey('generationMonitor.id'), nullable=True)
    generationFraction  = Column(      Float, nullable=True)
    generationMonitor   = relationship(GenerationMonitor)

    # consumption monitor
    consumptionMonitorID = Column(String(250), ForeignKey('consumptionMonitor.id'), nullable=False)
    consumptionFraction  = Column(      Float, nullable=False)
    consumptionMonitor   = relationship(ConsumptionMonitor)

    def getEnergyData(self, startTime, endTime, timeUnit):
        generationData  = self.generationMonitor .download(startTime, endTime, timeUnit)
        consumptionData = self.consumptionMonitor.getConsumptionData(startTime, endTime, timeUnit)
        combined = pd.merge(generationData, consumptionData, left_on=["date"], right_on=["start"])
        combined.drop(['start', 'end'], axis=1, inplace=True)
        combined.rename({'Production': 'producedEnergy', 'consumptionEnergy': 'consumedEnergy'},
                        axis='columns',
                        inplace=True)
        combined.producedEnergy *= self.generationFraction
        combined.producedEnergy *= self.consumptionFraction
        return combined

    ##property
    propertyID           = Column(String(250), nullable=False)
    
#class Property:
#    __tablename__ = 'property'
#    
#    
#    def getUnit(unitID):
#        return
#
#    def getConsumedEnergy():
#        return
#
#    def getGeneratedEnergy():
#        return
#
#    def getNetEnergy():
#        return


cfg = loadCfg()

# Create an engine that stores data in the local directory's
# sqlalchemy_example.db file.
engine = createDBEngine()
 
# Create all tables in the engine. This is equivalent to "Create Table"
# statements in raw SQL.
Base.metadata.create_all(engine)
