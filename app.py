import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt

from flask import Flask, jsonify


engine = create_engine("sqlite:///Resources/hawaii.sqlite")

last_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

app = Flask(__name__)



@app.route("/")
def index():
    return (
        f"Welcome!<br/>"
        f"Available routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"    
        f"/api/v1.0/tobs<br/>" 
        f"/api/v1.0/<start><br/>" 
        f"/api/v1.0/<start>/<end><br/>" 
        
    )

@app.route("/api/v1.0/precipitation/")
def precipitation():
    session = Session(engine)
    prcp_results = session.query(Measurement.date, Measurement.prcp).all()

    session.close()


    level = []
    for date, prcp in prcp_results:
        measurement_dict = {}
        measurement_dict["date"] = date
        measurement_dict["prcp"] = prcp
        level.append(measurement_dict)

    return jsonify(level)

@app.route("/api/v1.0/stations/")
def stations():
    session = Session(engine)
    station_results = session.query(Station.station).all()

    session.close()

    # Convert list of tuples into normal list
    station_names = list(np.ravel(station_results))

    return jsonify(station_names)

@app.route("/api/v1.0/tobs")
def tobs():

    session = Session(engine)
    
    active_station = session.query(Measurement.station, func.count(Measurement.tobs))\
                            .group_by(Measurement.station)\
                            .order_by(func.count(Measurement.tobs).desc()).first()[0]
                      
    tobs_result = session.query(Measurement.date, Measurement.station, Measurement.tobs)\
                        .filter(Measurement.station == active_station)\
                        .filter(Measurement.date >= last_year).all()
    
    session.close()


    tobs_active = []
    for date, station, tobs in tobs_result:
        tobs_dict = {}
        tobs_dict["date"] = date
        tobs_dict["station"] = station
        tobs_dict["tobs"] = tobs
        tobs_active.append(tobs_dict)

    return jsonify(tobs_active)


@app.route("/api/v1.0/<start>")
def stat1(start):
    
    session = Session(engine)

    stats_1 = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs)\
                                , func.max(Measurement.tobs))\
                                .filter(Measurement.date >= start).all()
    
    session.close()


    stats_start = []
    for min, avg, max in stats_1:
        stats_start_dict = {}
        stats_start_dict["min"] = min
        stats_start_dict["avg"] = avg
        stats_start_dict["max"] = max
        stats_start.append(stats_start_dict)

    return jsonify(stats_start)


@app.route("/api/v1.0/<start>/<end>")
def stat2(start, end):

    session=Session(engine)

    stats_2 = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs)\
                                , func.max(Measurement.tobs))\
                                .filter(Measurement.date >= start)\
                                .filter(Measurement.date <= end).all()
                
    session.close()
    
    # Create a dictionary to hold start/end data
    stats_start_end = []
    for min, avg, max in stats_2:
        stats_start_end_dict = {}
        stats_start_end_dict["min"] = min
        stats_start_end_dict["avg"] = avg
        stats_start_end_dict["max"] = max
        stats_start_end.append(stats_start_end_dict)

    return jsonify(stats_start_end)


if __name__ == "__main__":
    app.run(debug=True)
