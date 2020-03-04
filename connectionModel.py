#!/usr/bin/env python
from sqlalchemy import Column, ForeignKey, Float, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import orm
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from energyMonitorConfig import *
from interfaces import SolarEdgeHandler
from interfaces import NeurioHandler
from interfaces import UtilityAPIHandler

Base = declarative_base()


def create_db_engine():
    return create_engine(interface_db_connection_string)


def db_connect(db_engine):
    Base.metadata.bind = db_engine
    db_session = sessionmaker(bind=db_engine)
    session = db_session()
    return session


# corresponds to a solar generation monitor
class GenerationMonitor(Base):
    __tablename__ = 'generationMonitor'
    
    id             = Column(String(250), nullable=False, primary_key=True)
    monitorType    = Column(String(250), nullable=False)
    timeZone       = Column(String(250), nullable=False)
    activationTime = Column(String(250), nullable=False)

    handler = None

    @orm.reconstructor
    def init_on_load(self):
        if self.monitorType == 'SolarEdge':
            self.handler = SolarEdgeHandler.SolarEdgeHandler(cfg, self.id, self.timeZone, self.activationTime)
        else:
            raise Exception("Unknown monitor type %s" % self.monitorType)


# corresponds to a neurio home energy monitor or similar
class ConsumptionMonitor(Base):
    __tablename__ = 'consumptionMonitor'
    
    id             = Column(String(250), nullable=False, primary_key=True)
    monitorType    = Column(String(250), nullable=False)
    timeZone       = Column(String(250), nullable=False)
    activationTime = Column(String(250), nullable=False)

    handler = None

    @orm.reconstructor
    def init_on_load(self):
        if self.monitorType == 'Neurio':
            self.handler = NeurioHandler.NeurioHandler(cfg, self.id, self.timeZone, self.activationTime)
        else:
            raise Exception("Unknown monitor type %s" % self.monitorType)


class UtilityBilling(Base):
    __tablename__ = 'utilityBilling'

    id                 = Column(String(250), nullable=False, primary_key=True)
    timezone           = Column(String(250), nullable=False)
    billing_start_time = Column(String(250), nullable=False)

    handler            = None

    @orm.reconstructor
    def init_on_load(self):
        self.handler = UtilityAPIHandler.UtilityAPIHandler(cfg, self.id, self.timezone, self.billing_start_time)


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

    billingMeterID       = Column(String(250), ForeignKey('utilityBilling.id'), nullable=False)
    billingFraction      = Column(      Float, nullable=False)
    utilityBilling       = relationship(UtilityBilling)

    # property
    propertyID           = Column(String(250), nullable=False)
    
# class Property:
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


cfg = load_cfg()

# Create an engine that stores data in the local directory's
# sqlalchemy_example.db file.
engine = create_db_engine()
 
# Create all tables in the engine. This is equivalent to "Create Table"
# statements in raw SQL.
Base.metadata.create_all(engine)
