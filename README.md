# sqlalchemy-challenge

## First Part
# using Jupyter rNotebook

import warnings
warnings.filterwarnings('ignore')


# dependencies
import numpy as np
import pandas as pd
import datetime as dt

# Python SQL toolkit and Object Relational Mapper
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect

# create engine to hawaii.sqlite
engine = create_engine("sqlite:///Resources/hawaii.sqlite")


# Declare a Base using `automap_base()`
Base = automap_base()

# reflect an existing database into a new model
# reflect the tables
Base.prepare(engine, reflect=True)

# View all of the classes that automap found
Base.classes.keys()

# Use the Inspector to explore the database and print the table names
inspector = inspect(engine)
inspector.get_table_names()

# Get a list of column names and types
columns = inspector.get_columns('measurement')
for c in columns:
    print(c['name'], c["type"])
# columns

# Get a list of column names and types
columns = inspector.get_columns('station')
for c in columns:
    print(c['name'], c["type"])
# columns

# Save references to each table
measurement = Base.classes.measurement
station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

### Exploratory Precipitation Analysis

# Find the most recent date in the data set.
Most_Recent_Date = session.query(func.max(measurement.date)).first()
print ( "the most recent date in the data set :", Most_Recent_Date)

# Design a query to retrieve the last 12 months of precipitation data and plot the results. 
# Starting from the most recent data point in the database. 


# Calculate the date one year from the last date in data set.
one_year_from_lastDate = dt.date(2017,8,23) - dt.timedelta(days=365)
print ("the date one year from the last date in data set :", one_year_from_lastDate)

# Perform a query to retrieve the data and precipitation scores

data = session.query(measurement.date, measurement.prcp).filter(measurement.date>= one_year_from_lastDate).all()
 

# Save the query results as a Pandas DataFrame and set the index to the date column

dataDF = pd.DataFrame(data, columns = ['date', 'percipitation'])


#prcp_dates_DF_sorted
dataDF_sorted = dataDF.sort_values('date')

# Use Pandas Plotting with Matplotlib to plot the dataDF.plot.bar()

dataDF_sorted.plot(x='date', y = 'percipitation', rot = 90)
plt.ylabel('inches')
plt.show()

# Use Pandas to calcualte the summary statistics for the precipitation data
dataDF_sorted.describe()

# Design a query to find the most active stations (i.e. what stations have the most rows?)
# List the stations and the counts in descending order.
most_active = session.query(measurement.station, func.count(measurement.station)).group_by(measurement.station).order_by(func.count(measurement.station).desc()).all()
most_active 

# Using the most active station id from the previous query, calculate the lowest, highest, and average temperature.
session.query(func.min(measurement.tobs), func.max(measurement.tobs), func.avg(measurement.tobs)).filter( measurement.station == 'USC00519281').all()

# Using the most active station id
# Query the last 12 months of temperature observation data for this station and plot the results as a histogram
past_year = session.query(measurement.tobs).filter(measurement.station == 'USC00519281').filter(measurement.date >= one_year_from_lastDate).all()
past_year 

past_year_DF = pd.DataFrame(past_year, columns=['tobs'])
past_year_DF

past_year_DF.plot.hist(bins=12)
plt.show()

# Close Session
session.close()



### Second Part

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