import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, distinct

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
measurement = Base.classes.measurement
station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################



#Create Routes
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end<br/>"
        f"Note: to access values between a start and end date enter both dates using format: YYYY-mm-dd/YYYY-mm-dd"
    )





# Create a route that queries precipiation levels and dates and returns a dictionary using date as key and precipation as value

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create session 
    session = Session(engine)

    """Return a list of all daily precipitation totals for the last year"""
      
    start_date = '2016-08-23'
    sel = [measurement.date, 
        func.sum(measurement.prcp)]
    precipitation = session.query(*sel).\
            filter(measurement.date >= start_date).\
            group_by(measurement.date).\
            order_by(measurement.date).all()
   
    session.close()



   # Return a dictionary with the date as key and the daily precipitation total as value
    precipitation_dates = []
    precipitation_totals = []

    for date, dailytotal in precipitation:
        precipitation_dates.append(date)
        precipitation_totals.append(dailytotal)
    
    precipitation_dict = dict(zip(precipitation_dates, precipitation_totals))

    return jsonify(precipitation_dict)




#  Return a JSON list of stations from the dataset.

@app.route("/api/v1.0/stations")
def stations():
    # Create session 
    session = Session(engine)

    """Return a list of all the active Weather stations in Hawaii"""
    # Return a list of active weather stations in Hawaii
    sel = [measurement.station]
    active_stations = session.query(*sel).\
        group_by(measurement.station).all()
    session.close()

    
    list_of_stations = list(np.ravel(active_stations)) 
    return jsonify(list_of_stations)




#Query the dates and temperature observations of the most-active station for the previous year of data.
@app.route("/api/v1.0/tobs")
def tobs():
    # Create session 
    session = Session(engine)
    # Query the last 12 months of temperature observation data for the most active station
    start_date = '2016-08-23'
    sel = [measurement.date, 
        measurement.tobs]
    station_temps = session.query(*sel).\
            filter(measurement.date >= start_date, measurement.station == 'USC00519281').\
            group_by(measurement.date).\
            order_by(measurement.date).all()

    session.close()

    # Return a JSON list of temperature observations for the previous year.    
    observation_dates = []
    temperature_observations = []

    for date, observation in station_temps:
        observation_dates.append(date)
        temperature_observations.append(observation)
    
    most_active_tobs_dict = dict(zip(observation_dates, temperature_observations))

    return jsonify(most_active_tobs_dict)




#Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start or start-end range.
#For a specified start, calculate TMIN, TAVG, and TMAX for all the dates greater than or equal to the start date.#

@app.route("/api/v1.0/trip/<start_date>")
def trip1(start_date, end_date='2017-08-23'):
    # Calculate minimum, average and maximum temperatures for the range of dates starting with start date.
    # If no end date is provided, the function defaults to 2017-08-23.

    session = Session(engine)
    query_result = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
        filter(measurement.date >= start_date).filter(measurement.date <= end_date).all()
    session.close()

    trip_stats = []
    for min, avg, max in query_result:
        trip_dict = {}
        trip_dict["Min"] = min
        trip_dict["Average"] = avg
        trip_dict["Max"] = max
        trip_stats.append(trip_dict)

    # If the query returned non-null values return the results,
    # otherwise return an error message
    if trip_dict['Min']: 
        return jsonify(trip_stats)
    else:
        return jsonify({"error": f"Date {start_date} not found or not formatted as YYYY-MM-DD."}), 404
  


#For a specified start date and end date, calculate TMIN, TAVG, and TMAX for the dates from the start date to the end date, inclusive.

@app.route("/api/v1.0/trip/<start_date>/<end_date>")
def trip2(start_date, end_date='2017-08-23'):
   
    # If no valid end date is provided, the function defaults to 2017-08-23.

    session = Session(engine)
    query_result = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
        filter(measurement.date >= start_date).filter(measurement.date <= end_date).all()
    session.close()

    trip_stats = []
    for min, avg, max in query_result:
        trip_dict = {}
        trip_dict["Min"] = min
        trip_dict["Average"] = avg
        trip_dict["Max"] = max
        trip_stats.append(trip_dict)

    # If the query returned non-null values return the results,
    # otherwise return an error message
    if trip_dict['Min']: 
        return jsonify(trip_stats)
    else:
        return jsonify({"error": f"Date(s) not found, invalid date range or dates not formatted correctly."}), 404
  

if __name__ == '__main__':
    app.run(debug=True)

    
