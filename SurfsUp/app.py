# Import the dependencies.
import numpy as np
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, Column, Integer, Float, String, Date
from sqlalchemy.ext.declarative import declarative_base
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
Measure= Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

## Create the homepage route:

@app.route("/")
def homepage():
    """List all available api routes."""
    print("server received request for 'Home' page....")

	    # list all available routes
    return(f"Available Routes:<br/>"
               f"/api/v1.0/precipitation<br/>"
               f"/api/v1.0/stations<br/>"
               f"/api/v1.0/tobs<br/>"
               f"/api/v1.0/<start><br/>"
               f"/api/v1.0/<start>/<end>"

            )
Base = declarative_base()

## Create the precipipation route

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)

    recent_date =session.query(Measure.date).order_by(Measure.date.desc()).first()
    recent_date = dt.datetime.strptime("2017-08-23", "%Y-%m-%d")

    #calculate the one year date
    one_year_date = recent_date - dt.timedelta(days=365)
    precipt_data = session.query(Measure.date,Measure.prcp).filter(Measure.date >=one_year_date). order_by(Measure.date).all()

    # convert to a dictionary
    prcpt_dict = {entry.date: entry.prcp for entry in precipt_data}
      

    return jsonify(prcpt_dict)

# Close the session explicitly
    session.close()

## Create the stations route

@app.route("/api/v1.0/stations",methods=['GET'])
def stations():
    session = Session(engine)

    station_results = session.query(Station.station).all()
    station_names = [entry.station for entry in station_results]
  # make it a list
    stations= list(np.ravel(station_names))
    
    return jsonify(stations)

# Close the session explicitly
    session.close()


## Create the tobs route
    
@app.route("/api/v1.0/tobs", methods=['GET'])
def tobs():
    session = Session(engine)

    most_active_station = session.query(Measure.station, func.count(Measure.station)).group_by(Measure.station).order_by(func.count(Measure.station).desc()).first()

    if most_active_station:
        most_active_station_id = most_active_station[0]
        recent_date = session.query(Measure.date).filter(Measure.station == 'USC00519281').order_by(Measure.date.desc()).first()

        if recent_date:
            recent_date = recent_date[0]  # Extract the date from the tuple
            recent_date_cv = dt.datetime.strptime(recent_date, "%Y-%m-%d")

            one_year_date = recent_date_cv - dt.timedelta(days=365)
            one_year_date_str = one_year_date.strftime("%Y-%m-%d")  # Convert to string

            most_active_station_data = session.query(Measure.date, Measure.tobs).filter(Measure.station == 'USC00519281', Measure.date >= one_year_date_str).order_by(Measure.date).all()

            result_list = [{"date": entry.date, "tobs": entry.tobs} for entry in most_active_station_data]

            return jsonify(result_list)

    return jsonify({"error": "No data found for the most active station"})


def valid_date(datestr):
    """Helper function to check if a date string is valid."""
    try:
        dt.datetime.strptime(datestr, "%Y-%m-%d")
        return True
    except ValueError:
        return False
    
    # Close the session explicitly
    session.close()


  ## Create the start date route
@app.route("/api/v1.0/<start>")
def start(start):
    session = Session(engine)
  
    # Query to retrieve temperature statistics from the given start date
    temp_results = session.query(func.min(Measure.tobs), func.max(Measure.tobs), func.avg(Measure.tobs)).filter(Measure.date >= start).all()
        
    #query the min, avg and max temperatures for the start date
    temperature = session.query(
        func.min(Measure.tobs),
        func.avg(Measure.tobs),
        func.max(Measure.tobs)
        ).filter(Measure.date>= start).all()
    min_temp, avg_temp, max_temp = temperature[0]
    result_list = [{'start_date':start, 'min_temperature':min_temp, 'max_temperature': max_temp} for entry in temp_results]

    return jsonify(result_list)

    # Close the session explicitly
    session.close()

## Create the start or end route
    
@app.route("/api/v1.0/<start>/<end>", methods=['GET'])
def get_temp_range(start,end):
    session = Session(engine)
    
    start_date = dt.datetime.strptime(start, "%Y-%m-%d")
    end_date = dt.datetime.strptime(end, "%Y-%m-%d")

    temp_results_start_end = session.query(func.min(Measure.tobs), func.max(Measure.tobs), func.avg(Measure.tobs)).filter(Measure.date >= start, Measure.date <= end_date).all()
      
    #query the min, avg and max temperatures for the start date
    temperature = session.query(
        func.min(Measure.tobs),
        func.avg(Measure.tobs),
        func.max(Measure.tobs)
        ).filter(Measure.date>= start_date, Measure.date <= end_date).all()
    if not temperature:
        return jsonify({'error': 'No data available for the specified date range'})
    min_temp, avg_temp, max_temp = temperature[0]
    result_start_end_list =[{
        'start_date':start,
        'end_date':end,
        'min_temperature':min_temp,
        'max_temperature': max_temp} for entry in temp_results_start_end]

    return jsonify(result_start_end_list)

# Close the session explicitly
    session.close()


if __name__ == '__main__':
    app.run(debug=True)