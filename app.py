from flask import Flask, jsonify

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect
import numpy as np
import pandas as pd
import datetime as dt

app = Flask(__name__)

# establish connectioin to database
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
# reflect the tables
Base = automap_base()
Base.prepare(engine, reflect=True)

# Save references to each table
measurement = Base.classes.measurement
station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)


# specify home route
@app.route("/")
def home():
    return(
        f"welcome to climate analysis API"
        f"select from  the below routes "
        f"/api/v1.0/precipitation"
        f"/api/v1.0/stations"
        f"/api/v1.0/tobs"
        f"/api/v1.0/start/end"
          )

# route for /api/v1.0/precipitation
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Calculate the date one year from the last date in data set.
    one_year_from_lastDate = dt.date(2017,8,23) - dt.timedelta(days=365)
    print ("the date one year from the last date in data set :", one_year_from_lastDate)

    # Perform a query to retrieve the data and precipitation scores

    data = session.query(measurement.date, measurement.prcp).filter(measurement.date>= one_year_from_lastDate).all()
    session.close

    precip = {date: prcp for date, prcp in data}

    # jsonfiy
    return jsonify(precip)

# route for /api/v1.0/stations
@app.route("/api/v1.0/stations")
def Station():
    # show a list of station
    stations_name = session.query(station.station).all()

    session.close()

    station_list = list(np.ravel(stations_name))

    #jsonify
    return jsonify(station_list)

# route for /api/v1.0/tobs
@app.route("/api/v1.0/tobs")
def Temp():
    # previous year temperature from most active station
    one_year_from_lastDate = dt.date(2017,8,23) - dt.timedelta(days=365)
    past_year = session.query(measurement.tobs).filter(measurement.station == 'USC00519281').filter(measurement.date >= one_year_from_lastDate).all()
    session.close

    temp_list = list(np.ravel(past_year))

    #jsonify
    return jsonify(temp_list)

# /api/v1.0/<start/end and /api/v1.0/start routes

@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def date_stat(start = None, end = None):
    # select statment
    selection = [func.min(measurement.tobs), func.max(measurement.tobs), func.avg(measurement.tobs)]

    if not end:
        startDate = dt.datetime.strptime(start, "%m%d%Y")
        results = session.query(*selection.filter(measurement.date >= startDate).filter(measurement.date <= endDate)).all()

        session.close()

        templist = list(np.ravel(results ))

        return jsonify(templist)

    else:

        startDate = dt.datetime.strptime(start, "%m%d%Y")
        endDate = dt.datetime.strptime(start, "%m%d%Y")
        results = session.query(*selection.filter(measurement.date >= startDate)).all()

        session.close()

        templist = list(np.ravel(results ))

        return jsonify(templist)







if __name__ == '__main__':
    app.run(debug=True)
