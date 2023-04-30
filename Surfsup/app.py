# Import the dependencies.
import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
measurement = Base.classes.measurement

# Create our session (link) from Python to the DB


#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:</br>"
        f"/api/v1.0/precipitation</br>"
        f"/api/v1.0/stations</br>"
        f"/api/v1.0/tobs</br>"
        f"/api/v1.0/start</br>"
        f"/api/v1.0/start/end"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    """Return a JSON representation of query results, showing the last 12 months of data"""
    results = session.query(measurement.date, measurement.prcp).order_by(measurement.id.desc()).limit(349).all()

    session.close()

    all_dates = list(np.ravel(results))

    return jsonify(all_dates)

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    """Return a JSON list of stations from the dataset"""
    results = session.query(measurement.station).all()

    session.close()

    all_stations = list(set(np.ravel(results)))

    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    """Return a JSON list of temperature observations for the most-active station for the previous year of data"""
    results = session.query(measurement.date, measurement.station, measurement.tobs).order_by(measurement.id.desc()).all()
    
    session.close()
    
    df = pd.DataFrame(results, columns=['date','station', 'temp'])
    station = df[df['station'] == 'USC00519281'][['date', 'temp']]
    station = station[0:356]

    station_temps = list(np.ravel(station))

    return jsonify(station_temps)

@app.route("/api/v1.0/<start>")
def start_date(start):
    session = Session(engine)
    """Return a JSON list of the min, avg, and max temp for a specified start date"""
    results = session.query(measurement.date, measurement.tobs).order_by(measurement.id.desc()).all()
    
    session.close()
    
    df = pd.DataFrame(results, columns=['date','temp'])
    df = df.sort_values(by='date').reset_index(drop=True)
    df = df.iloc[df[df.date == start].index[0]:]


    TMIN = df['temp'].min()
    TAVG = df['temp'].mean()
    TMAX = df['temp'].max()

    return jsonify({"Min Temp": TMIN, "Avg Temp": TAVG, "Max Temp": TMAX})

@app.route("/api/v1.0/<start>/<end>")
def start_and_end_date(start, end):
    session = Session(engine)
    """Return a JSON list of the min, avg, and max temp for a specified start date and end date"""
    results = session.query(measurement.date, measurement.tobs).order_by(measurement.id.desc()).all()
    
    session.close()
    
    df = pd.DataFrame(results, columns=['date','temp'])
    df = df.sort_values(by='date').reset_index(drop=True)
    df = df.iloc[df[df.date == start].index[0] : df[df.date == end].index[0]]


    TMIN = df['temp'].min()
    TAVG = df['temp'].mean()
    TMAX = df['temp'].max()

    return jsonify({"Min Temp": TMIN, "Avg Temp": TAVG, "Max Temp": TMAX})

if __name__ == "__main__":
    app.run(debug=True)