#!/usr/bin/env python
from dataModel import *

from bokeh.plotting import figure
from bokeh.layouts import  row, column

from tornado.ioloop import IOLoop
from bokeh.application.handlers import FunctionHandler
from bokeh.application import Application
from bokeh.server.server import Server

from bokeh.models.widgets import DatePicker
from bokeh.models.widgets.inputs import AutocompleteInput

io_loop = IOLoop.current()

engine = createDBEngine()
session = dbConnect(engine)

rentalUnits = [unit.unitName for unit in session.query(RentalUnit).all()]
rentalUnitSelector=AutocompleteInput(title="Rental Unit",completions=rentalUnits)

startDatePicker=DatePicker(title="Start Date", min_date="2018-04-01")
endDatePicker  =DatePicker(title="End Date", min_date="2018-04-01")

def monitoringApp(doc):
    startTime=pd.to_datetime('2018-04-21 08:00:00')
    endTime=pd.to_datetime('2018-05-20 01:00:00')

    plots=[]

    rentalUnits=session.query(RentalUnit).all()
    for unit in rentalUnits:
        print("===================")
        print (unit.unitName)
        print (unit.propertyID)
        #time_unit="QUARTER_OF_AN_HOUR"
        time_unit="HOUR"
        combined=unit.getEnergyData(startTime, endTime, time_unit)
        print (combined.head())
        print (combined.producedEnergy.sum())
        unitPlot=figure(title=unit.unitName,x_axis_type="datetime",plot_width=1000,plot_height=400)
        unitPlot.line(combined.date, combined.producedEnergy,legend="Solar Production",color="blue")
        unitPlot.line(combined.date, combined.consumedEnergy,legend="Usage",color="red")
        plots.append(unitPlot)
        print(plots)

    widgets=column(rentalUnitSelector,startDatePicker, endDatePicker)
    plotsCol=column(plots)
    layout=row(widgets,plotsCol)#(plots,ncols=1)
    #curdoc().add_root(outGrid)
    doc.add_root(layout)

bokeh_app = Application(FunctionHandler(monitoringApp))

server = Server({'/': bokeh_app}, io_loop=io_loop)
server.start()

if __name__ == '__main__':
    print('Opening Bokeh application on http://localhost:5006/')
    io_loop.add_callback(server.show, "/")
    io_loop.start()