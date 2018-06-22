#!/usr/bin/env python
from dataModel import *
from datetime import datetime, timedelta
from bokeh.plotting import figure
from bokeh.layouts import  row, column

from tornado.ioloop import IOLoop
from bokeh.application.handlers import FunctionHandler
from bokeh.application import Application
from bokeh.server.server import Server

from bokeh.models.widgets import Div
from bokeh.models.widgets import DatePicker
from bokeh.models.widgets import Select
from bokeh.models.widgets import DataTable, TableColumn, NumberFormatter
from bokeh.models import ColumnDataSource

# https://github.com/bokeh/bokeh/blob/master/examples/app/stocks/main.py
# https://demo.bokehplots.com/apps/stocks
# want to use LRU at some point?  Could be valualble....
# TODO: bugfix on min/max dates

io_loop = IOLoop.current()

engine = createDBEngine()
session = dbConnect(engine)

maxTimeDelta=timedelta(days=30)

#####################
## Data sources
energyPlottingData=ColumnDataSource(data=dict(date=[],producedEnergy=[],consumedEnergy=[]))
summaryDataSource=ColumnDataSource(data=dict(fieldNames=[],values=[]))

#####################
## Selection Widgets
rentalUnits = [unit.unitName for unit in session.query(RentalUnit).all()]
rentalUnitSelector=Select(title="Rental Unit", value=rentalUnits[0],options=rentalUnits)

loadingText="<h2>Loading...</h2>"
doneText="<h2>Done</h2>"
statusText=Div(text='')

maxDate=datetime.today()
minDate=maxDate-maxTimeDelta
startDatePicker=DatePicker(title="Start Date", value=minDate, min_date=minDate, max_date=maxDate)
endDatePicker  =DatePicker(title=  "End Date", value=maxDate, min_date=minDate, max_date=maxDate)

#####################
## Summary Table
summaryRows=["Produced", "Used", "Net Consumption"]
summaryColumns=[TableColumn(field="fieldNames",title="fields"),
                TableColumn(field="values",title="values",formatter=NumberFormatter(format='0,0',language='en'))]
summaryTableTitle=Div(text='<h2>Summary (kWh)</h2>')
summaryTable=DataTable(source=summaryDataSource,columns=summaryColumns,index_position=None, width=300)

#####################
## Plots
energyPlot=figure(x_axis_type="datetime",plot_width=800,plot_height=400)
energyPlot.line("date", "producedEnergy", source=energyPlottingData, legend="Solar Production", color="blue")
energyPlot.line("date", "consumedEnergy", source=energyPlottingData, legend="Usage", color="red")

def updateRentalUnit(attrname, old, new):
    updateDisplay()

def updateStartDate(attrname, old, new):
    endDatePicker.min_date=new
    endDatePicker.max_date=new + maxTimeDelta
    updateDisplay()

def updateEndDate(attrname, old, new):
    startDatePicker.min_date=new - maxTimeDelta
    startDatePicker.max_date=new
    updateDisplay()

def updateDisplay():

    statusText.text=loadingText

    selectedUnit=rentalUnitSelector.value
    startTime=pd.to_datetime(startDatePicker.value)
    endTime=pd.to_datetime(endDatePicker.value)
    #print("Start and end dates: ",startTime,endTime)

    unit=session.query(RentalUnit).filter(RentalUnit.unitName==selectedUnit).one()
    energyPlot.title.text=unit.unitName

    time_unit = "HOUR"
    energyDataFrame = unit.getEnergyData(startTime, endTime, time_unit)

    totalProduced=energyDataFrame.producedEnergy.sum()
    totalUsed=energyDataFrame.consumedEnergy.sum()
    netConsumption=totalUsed-totalProduced
    summaryData=[totalProduced,totalUsed,netConsumption]
    summaryDataSource.data={"fieldNames":summaryRows,"values":summaryData}
    #print(energyDataFrame)
    energyPlottingData.data = energyPlottingData.from_df(energyDataFrame)

    statusText.text=doneText

rentalUnitSelector.on_change('value', updateRentalUnit)
startDatePicker   .on_change('value',  updateStartDate)
endDatePicker     .on_change('value',    updateEndDate)

def monitoringApp(doc):

    datePickers=row(startDatePicker, endDatePicker)
    widgets=column(row(rentalUnitSelector,statusText),datePickers,summaryTableTitle,summaryTable)
    plotsCol=column(energyPlot)
    layout=row(widgets,plotsCol)

    updateDisplay()

    doc.title="Energy Monitor"
    doc.add_root(layout)

bokeh_app = Application(FunctionHandler(monitoringApp))

server = Server({'/': bokeh_app}, io_loop=io_loop)
server.start()

if __name__ == '__main__':
    print('Opening Bokeh application on http://localhost:5006/')
    io_loop.add_callback(server.show, "/")
    io_loop.start()