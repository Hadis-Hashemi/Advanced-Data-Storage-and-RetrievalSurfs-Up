import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

## reflect an existing database into a new model
Base = automap_base()

##Reflect the tables
Base.prepare(engine,reflect=True)

#Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

#Flask setup
app = Flask(__name__)

# Flask Routes
@app.route("/")
def welcome():
    return(
        f"Welcome to Hawaii Home Page.<br/>"
        f"Available Routes: <br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )

##Convert the query results to a dictionary using `date` as the key and `prcp` as the value.
##Return the JSON representation of your dictionary.
from collections import defaultdict 
@app.route("/api/v1.0/precipitation")
def precipitation():
    #Create session link from python to DB
    session = Session(engine)
    
    #Query results
    twelve_months_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    results= session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= twelve_months_ago).all()
    session.close()
    
    #Create dictionary of date and prcp
    result_dic = defaultdict(list)
    for key, value in results:
        result_dic[key].append(value)
        
    return jsonify(result_dic)  

#Returns a JSON list of stations from the dataset.
@app.route("/api/v1.0/stations")
def stations():
    #Create session link from python to DB
    session = Session(engine)
    
    #Query result
    station_list = session.query(Measurement.station).group_by(Measurement.station).all()
    session.close()
    # creating a dictionary of station_list
    dic_station_list = {"stations": station_list }
    return jsonify(dic_station_list)

#Query the dates and temperature observations of the most active station for the last year of data.
@app.route("/api/v1.0/tobs")
def active():
    #Create session link from python to DB
    session = Session(engine) 
    
    twelve_months_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    
    #date and temperature of the most active station 
    temp_date_results = session.query(Measurement.date, Measurement.tobs).filter(Measurement.station == 'USC00519281').\
    filter(Measurement.date >= twelve_months_ago).all()
    session.close()    
    
    #Return a JSON list
    station_temp_dict = {"Date and Temparture Observations for station USC00519281 From 2016-8-23 to 2017-8-23": temp_date_results}
    return jsonify(station_temp_dict)

##Query the dates and temperature observations of the most active station for the last year of data.
##Return a JSON list of temperature observations (TOBS) for the previous year.

from datetime import datetime
@app.route("/api/v1.0/<start>")
def temp_date_active(start):
    session = Session(engine)
    
    #Correct the format of date
    date_correct = start.replace("-", "")
    start_date = datetime.strptime(date_correct, '%Y%m%d').strftime('%Y-%m-%d') 
    
    #data
    max_temp = session.query(func.max(Measurement.tobs)).filter(Measurement.date >= start_date).all()
    min_temp = session.query(func.min(Measurement.tobs)).filter(Measurement.date >= start_date).all()
    avg_temp = session.query(func.avg(Measurement.tobs)).filter(Measurement.date >= start_date).all()
    
    #Create dictionary
    temp_date_active = {"Start Date": start_date, "Maximum Temperature": max_temp, "Minimum Temperature": min_temp,"Average Temperature": avg_temp}
    
    return jsonify(temp_date_active)
## When given the start only, calculate `TMIN`, `TAVG`, and `TMAX` for all dates greater than and equal to the start date.
@app.route("/api/v1.0/<start>/<end>")
def start_end(start,end):
    session = Session(engine)
    
    corrected_new = start.replace("-", "")
    
    start_date = datetime.strptime(corrected_new, '%Y%m%d').strftime('%Y-%m-%d') 
    
    corrected_last = end.replace("-", "")
    end_date = datetime.strptime(corrected_last,'%Y%m%d').strftime('%Y-%m-%d') 
    
    max_temp = session.query(func.max(Measurement.tobs)).filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()
    min_temp = session.query(func.min(Measurement.tobs)).filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()
    avg_temp = session.query(func.avg(Measurement.tobs)).filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()
    #Create dictionary
    temp_date_active = {"Start Date": start_date, "End Date": end_date, "Maximum Temp": max_temp, "Minimum Temp": min_temp,"Average Temperature": avg_temp}
    
    return jsonify(temp_date_active)
       
    
if __name__ == '__main__':
    app.run(debug=False)        