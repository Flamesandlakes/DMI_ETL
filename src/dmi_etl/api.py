from typing import Annotated
from fastapi import FastAPI, Query, Depends, HTTPException, Security
from sqlalchemy import create_engine, Column, Integer, String, Numeric, Time, Date, Identity
from sqlalchemy.orm import sessionmaker, Session
import sqlalchemy
from pydantic import BaseModel
import datetime
from dmi_etl.api_auth import app as auth_router
from dmi_etl.api_auth import User, get_current_active_user, check_authorization

from dmi_etl.DB_operations import *

## define order in Swagger order based on tags, after the order in the dict
tags_order_dict = [
    {"name": "authentication"},
    {"name": "climate readings"},
    {"name": "metadata"}
]
app = FastAPI(title="DMI ETL Pipeline API",
              openapi_tags=tags_order_dict)
engine = get_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = sqlalchemy.orm.declarative_base()

# integrate method from authentication
#app.post = dmi_etl.api_auth.app.post
app.include_router(auth_router,tags=["authentication"]) 


# CRUD, first defining format of respective database rows/entries, and then the CRUD methods themselves
class Parameter(Base):
    __tablename__ = "parameter_data"
    __table_args__ = {"schema": "climate"}
    name = Column(String, primary_key=True)
    unit = Column(String)
    frequency = Column(String)

class Station(Base):
    __tablename__ = "stations_data"
    __table_args__ = {"schema": "climate"}
    station_id = Column(String, primary_key=True, index=True)
    longitude = Column(Numeric(6,3))
    latitude = Column(Numeric(6,3))
    location_name = Column(String)

class Reading(Base):
    __tablename__ = "readings_data"
    __table_args__ = {"schema": "climate"}
    parameter_name = Column(String)
    value = Column(Numeric(6,3))
    reading_id = Column(Integer, Identity(always=True), primary_key=True)
    station_id = Column(String)
    time = Column(Time)
    date = Column(Date)

class Link(BaseModel):
    href : str
    rel : str
    type : str
    title : str

class Geometry(BaseModel):
    type : str
    coordinates : list[float, float]

class PropertiesStation(BaseModel):
    stationId : str
    name : str

class StationFeature(BaseModel):
    type : str
    geometry : Geometry
    properties : PropertiesStation

class PropertiesReading(BaseModel):
    parameterId: str
    value: float
    stationId: str
    time: datetime.time
    date: datetime.date

class ReadingFeature(BaseModel):
    type : str
    geometry : Geometry
    properties : PropertiesReading
    
#Pydantic models - describes what the client is allowed to send
class ParameterCreate(BaseModel):
    name: str
    unit: str
    frequency: str

class ParameterUpdate(BaseModel): #client is only allowed to change unit and frequency as name is primary key and readings_data has foerign key to it.
    unit: str
    frequency: str

#describes what the server sends back
class ParameterResponse(BaseModel):
    name: str
    unit: str
    frequency: str


class StationCreate(BaseModel):
    station_id : str
    longitude : float
    latitude : float
    location_name : str

class StationUpdate(BaseModel):
    longitude : float
    latitude : float
    location_name : str

class StationResponse(BaseModel):
    station_id : str
    longitude : float
    latitude : float
    location_name : str

class StationResponsesInfo(BaseModel):
    type : str
    features : list[StationFeature]
    timestamp : datetime.datetime
    numberReturned : int
    links : list[Link]


class ReadingCreate(BaseModel):
    parameter_name: str
    value: float
    station_id: str
    time: datetime.time
    date: datetime.date

class ReadingResponse(BaseModel):
    parameter_name: str
    value: float
    reading_id: int
    station_id: str
    time: datetime.time
    date: datetime.date

class ReadingResponsesInfo(BaseModel):
    type : str
    features : list[ReadingFeature]
    timestamp : datetime.datetime
    numberReturned : int
    links : list[Link]


# GET options for readings
# parameter or
# stationId or
# time (start and end time /potentially as T-seperated datetime obj string)

# GET options for station (and stations)
# stationid or
# station name

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/parameters/", response_model=ParameterResponse, tags=["metadata"])
async def create_parameter(current_user: Annotated[User, Security(get_current_active_user, 
                                                                  scopes=[])],
                            parameter: ParameterCreate, db: Session = Depends(get_db)):
    check_authorization(current_user, "parameters_admin")
    if db.query(Parameter).filter_by(name = parameter.name).first() is not None:
        raise HTTPException(status_code=422, detail=f"parameter {parameter.station_id} already exists. Consider updating existing parameter instead.")
    
    db_parameter = Parameter(**parameter.model_dump()) #dictionary representation of the model
    db.add(db_parameter)
    db.commit()
    db.refresh(db_parameter)
    return db_parameter

@app.get("/parameters/", response_model=list[ParameterResponse], tags=["metadata"])
async def read_parameter(current_user: Annotated[User, Security(get_current_active_user, 
                                                        scopes=[])],
                         name: Annotated[str | None, Query] = None, db: Session = Depends(get_db)):
    check_authorization(current_user, ["parameters_read", "parameters_admin"])

    db_parameter = db.query(Parameter)
    if db_parameter.first() is None:
        raise HTTPException(status_code=404, detail="No Parameters found in database.")
    if name != None:
        db_parameter = db_parameter.filter(Parameter.name == name)
        if db_parameter.first() is None:
            raise HTTPException(status_code=404, detail=f"Parameter {name} not found.")
    return db_parameter.all()

#replace the resource with what the client sends
#if the parameter exists, it will be overwritten
#if parameter does not exist, respond  with 404
#the response is the updated parameter
@app.put("/parameters/{name}", response_model=ParameterResponse) #fetch the name from the url
async def update_parameter(name: str, paramUpdate:ParameterUpdate, db: Session = Depends(get_db)):
    if db.query(Parameter).first() is None:
        raise HTTPException(status_code=404, detail="No Parameters found in database.")
    db_parameter = db.query(Parameter).filter(Parameter.name == name).first() #from the db, get the row with the name from the url.
    #parameter does not exist, respond with 404
    if db_parameter is None:
        raise HTTPException(status_code=404, detail=f"Parameter {name} not found.")
    #parameter does exist, so overwrite it
    db_parameter.unit = paramUpdate.unit
    db_parameter.frequency = paramUpdate.frequency
    #db.add(db_parameter)
    db.commit()
    db.refresh(db_parameter) #ask db to send the row again and update the object with fresh values
    return db_parameter

#replace the resource with what the client sends
#if the parameter exists, it will be overwritten
#if parameter does not exist, respond  with 404
#the response is the updated parameter
@app.put("/parameters/{name}", response_model=ParameterResponse, tags=["metadata"]) #fetch the name from the url
async def update_parameter(current_user: Annotated[User, Security(get_current_active_user, 
                                                        scopes=[])],
                           name: str, paramUpdate:ParameterUpdate, db: Session = Depends(get_db)):
    check_authorization(current_user, "parameters_admin")
    db_parameter = db.query(Parameter).filter(Parameter.name == name).first() #from the db, get the row with the name from the url.
    #parameter does not exist, respond with 404
    if db_parameter is None:
        raise HTTPException(status_code=404, detail="Parameter not found")
    #parameter does exist, so overwrite it
    db_parameter.unit = paramUpdate.unit
    db_parameter.frequency = paramUpdate.frequency
    #db.add(db_parameter)
    db.commit()
    db.refresh(db_parameter) #ask db to send the row again and update the object with fresh values
    return db_parameter


@app.delete("/parameters/{name}", status_code=204, tags=["metadata"])
async def delete_parameter(current_user: Annotated[User, Security(get_current_active_user, 
                                                    scopes=[])],
                            name:str, db: Session = Depends(get_db)):
    check_authorization(current_user, "parameters_admin")
    db_parameter = db.query(Parameter).filter(Parameter.name == name).first()
    #parameter does not exist, respond with 404
    if db_parameter is None:
        raise HTTPException(status_code=404, detail=f"Parameter {name} not found.")
    #parameter exists, delete it
    db.delete(db_parameter)
    db.commit()


@app.post("/stations/", response_model=StationResponse, tags=["metadata"])
async def create_station(current_user: Annotated[User, Security(get_current_active_user, 
                                                scopes=[])],
                         station: StationCreate, db: Session = Depends(get_db)):
    check_authorization(current_user, "stations_admin")
    if db.query(Station).filter_by(station_id = station.station_id).first() is not None:
        raise HTTPException(status_code=422, detail=f"Station id {station.station_id} already exists. Consider updating existing station instead.")
    
    db_station = Station(**station.model_dump()) #dictionary representation of the model
    db.add(db_station)
    db.commit()
    db.refresh(db_station)
    return db_station


@app.get("/stations/", response_model=StationResponsesInfo, tags=["metadata"])
async def read_station(current_user: Annotated[User, Security(get_current_active_user, 
                                                scopes=[])],
                        station_id: Annotated[str | None, Query] = None, 
                        location_name: Annotated[str | None, Query] = None,
                        bbox: Annotated[str | None, Query] = None,  
                        limit: Annotated[int | None, Query] = None, 
                        offset: Annotated[int | None, Query] = None, 
                        db: Session = Depends(get_db)):
    
    check_authorization(current_user,["stations_read", "stations_admin"])
    
    db_station = db.query(Station)
    if db_station.first() is None:
        raise HTTPException(status_code=404, detail="No stations found in database.")

    if station_id != None:
        db_station = db_station.filter(Station.station_id == station_id)
        if db_station.first() == None:
            raise HTTPException(status_code=404, detail=f"Stations with id: {station_id} not found.")
    
    if location_name != None:
        db_station = db_station.filter(Station.location_name == location_name)
        if db_station.first() == None:
            raise HTTPException(status_code=404, detail=f"Stations with location: {location_name} not found.")
    
    if bbox != None:
        bbox_list = bbox.split(",")
        try:
            for i in range(len(bbox_list)):
                bbox_list[i] = float(bbox_list[i])
        except:
            raise HTTPException(status_code=400, detail="The given bounding box is formated incorrectly.")
        if len(bbox_list) != 4:
            raise HTTPException(status_code=400, detail="The bounding box only takes 4 inputs")

        db_station = db_station.filter(
            Station.latitude >= bbox_list[0]).filter(
            Station.latitude <= bbox_list[1]).filter(
            Station.longitude >= bbox_list[2]).filter(
            Station.longitude <= bbox_list[3])
        
        if db_station.first() == None:
            raise HTTPException(status_code=404, detail=f"Stations in the bounding box: {bbox} not found.")
    
    if limit != None:
        if limit == 0:
            raise HTTPException(status_code=400, detail="Limit of requests can not be 0.")
        db_station = db_station.limit(limit)
    if offset != None:
        db_station = db_station.offset(offset)
        if db_station.first() == None:
            raise HTTPException(status_code=404, detail=f"No stations over offset {offset}.")

    features_list =[]
    for stat in db_station.all():
        geom = {"type": "point", "coordinates" : [stat.latitude,stat.longitude]}

        prop = {}
        prop["stationId"] = stat.station_id
        prop["name"] = stat.location_name
        features_list.append({"type": "feature", "geometry": geom, "properties": prop})

    response = {}
    response["type"] = ("FeatureCollection")
    response["features"] = features_list
    response["timestamp"] = datetime.datetime.now()
    response["numberReturned"] = db_station.count()

    self_link = {}
    self_link["href"] = "some link"
    self_link["rel"] = "self"
    self_link["type"] = "some type"
    self_link["title"] = "This document"

    next_link = {}
    next_link["href"] = "some link"
    next_link["rel"] = "next"
    next_link["type"] = "some type"
    next_link["title"] = "Next set of results"

    response["links"] = [self_link, next_link]
    return response


@app.put("/stations/{station_id}", response_model=StationResponse, tags=["metadata"])
async def update_parameter(current_user: Annotated[User, Security(get_current_active_user, 
                                                scopes=[])],
                            station_id: str, stationUpdate:StationUpdate, db: Session = Depends(get_db)):
    check_authorization(current_user, "stations_admin")
    if db.query(Station).first() is None:
            raise HTTPException(status_code=404, detail="No stations found in database.")
       
    db_station = db.query(Station).filter(Station.station_id == station_id).first()
    if db_station is None:
        raise HTTPException(status_code=404, detail=f"Station with id {station_id} not found.")
    db_station.longitude = stationUpdate.longitude
    db_station.latitude = stationUpdate.latitude
    db_station.location_name = stationUpdate.location_name
    db.commit()
    db.refresh(db_station)
    return db_station



@app.delete("/stations/{station_id}", status_code=204, tags=["metadata"])
async def delete_station(current_user: Annotated[User, Security(get_current_active_user, 
                                                scopes=["stations_admin"])],
                            station_id:str, db: Session = Depends(get_db)):
    check_authorization(current_user, "stations_admin")

    db_station = db.query(Station).filter(Station.station_id == station_id).first()
    #parameter does not exist, respond with 404
    if db_station is None:
        raise HTTPException(status_code=404, detail=f"Station with id {station_id} not found")
    #parameter exists, delete it
    db.delete(db_station)
    db.commit()


@app.post("/readings/", response_model=list[ReadingResponse], tags=["climate readings"])
async def create_reading(current_user: Annotated[User, Security(get_current_active_user, 
                                                scopes=[])],
                        readings: list[ReadingCreate], db: Session = Depends(get_db)):
    check_authorization(current_user, "readings_admin")

    db_list =[]
    db_readings = db.query(Reading)
    for reading in readings:
        if db.query(Station).filter(Station.station_id == reading.station_id).first() == None:
            raise HTTPException(status_code=422, detail=f"A station with the id {reading.station_id} does not exists in station database. Consider looking up available stations.")
        
        if db.query(Parameter).filter(Parameter.name == reading.parameter_name).first() == None:
            raise HTTPException(status_code=422, detail=f"A parameter with the name {reading.parameter_name} does not exists in station database. Consider looking up available parameters.")
        
        search_identical = db_readings.filter_by(
            parameter_name=reading.parameter_name,
            station_id=reading.station_id,
            date=reading.date,
            time=reading.time).first()
        
        if search_identical != None:
            raise HTTPException(status_code=422, detail="Unique entry already exists. Consider using update instead.")
        
        db_reading = Reading(**reading.model_dump())
        db.add(db_reading)
        db_list.append(db_reading)
    db.commit()
    db.refresh(db_reading)
    return db_list


@app.get("/readings/", response_model=ReadingResponsesInfo, tags=["climate readings"])
async def read_reading(
    current_user: Annotated[User, Security(get_current_active_user, 
                                                scopes=[])],
    parameter_name: Annotated[str | None, Query] = None,
    reading_id: Annotated[int | None, Query] = None,
    station_id: Annotated[str | None, Query] = None, 
    date_start: Annotated[datetime.date | None, Query] = None,
    date_end: Annotated[datetime.date | None, Query] = None,   
    limit: Annotated[int | None, Query] = None, 
    offset: Annotated[int | None, Query] = None,  
    db: Session = Depends(get_db)):

    check_authorization(current_user, ["readings_read", "readings_admin"])
    
    db_reading = db.query(Reading)

    if db_reading.first() is None:
        raise HTTPException(status_code=404, detail="No readings found in database.")

    if parameter_name != None:
        db_reading = db_reading.filter(Reading.parameter_name == parameter_name)
        if db_reading.first() == None:
            raise HTTPException(status_code=404, detail=f"Readings with parameter name {parameter_name} not found.")
            
    if reading_id != None:
        db_reading = db_reading.filter(Reading.reading_id == reading_id)
        if db_reading.first() == None:
            raise HTTPException(status_code=404, detail=f"Readings with reading id: {parameter_name} not found.")
    if station_id != None:
        db_reading = db_reading.filter(Reading.station_id == station_id)
        if db_reading.first() == None:
            raise HTTPException(status_code=404, detail=f"Readings with station id: {station_id} not found.")
                 
    if date_start != None:
        db_reading = db_reading.filter(Reading.date >= date_start)
        if db_reading.first() == None:
            raise HTTPException(status_code=404, detail=f"Readings after the date {date_start} not found.")
        
    if date_end != None:
        db_reading = db_reading.filter(Reading.date <= date_end)
        if db_reading.first() == None:
            raise HTTPException(status_code=404, detail=f"Readings before the date {date_end} not found.")
                

    if limit != None:
        if limit == 0:
            raise HTTPException(status_code=400, detail="Limit of requests can not be 0.")
                     
        db_reading = db_reading.limit(limit)
    if offset != None:
        db_reading = db_reading.offset(offset)
        if db_reading.first() == None:
            raise HTTPException(status_code=404, detail=f"No readings over offset {offset}.")
        
    if db_reading.first() is None:
        raise HTTPException(status_code=404, detail="Reading not found.")

    features_list =[]
    for read in db_reading.all():
        associated_station = db.query(Station).filter(Station.station_id == read.station_id).first()

        geom = {"type": "point", "coordinates" : [associated_station.latitude,associated_station.longitude]}

        prop = {}
        prop["parameterId"] = read.parameter_name
        prop["value"] = read.value
        prop["stationId"] = read.station_id
        prop["date"] = read.date
        prop["time"] = read.time
        features_list.append({"type": "feature", "geometry": geom, "properties": prop})

    response = {}
    response["type"] = ("FeatureCollection")
    response["features"] = features_list
    response["timestamp"] = datetime.datetime.now()
    response["numberReturned"] = db_reading.count()

    self_link = {}
    self_link["href"] = "some link"
    self_link["rel"] = "self"
    self_link["type"] = "some type"
    self_link["title"] = "This document"
    
    next_link = {}
    next_link["href"] = "some link"
    next_link["rel"] = "next"
    next_link["type"] = "some type"
    next_link["title"] = "Next set of results"

    response["links"] = [self_link, next_link]
    return response


@app.put("/readings/", response_model=ReadingResponse, tags=["climate readings"])
async def update_reading(
    current_user: Annotated[User, Security(get_current_active_user, 
                                                scopes=[])],
    reading: ReadingCreate,
    parameter_name: Annotated[str | None, Query] = None,
    reading_id: Annotated[int | None, Query] = None,
    station_id: Annotated[str | None, Query] = None, 
    date_start: Annotated[datetime.date | None, Query] = None,
    date_end: Annotated[datetime.date | None, Query] = None,
    db: Session = Depends(get_db)):

    check_authorization(current_user, "readings_admin")
    
    db_reading = db.query(Reading)
    if db_reading.first() is None:
        raise HTTPException(status_code=404, detail="No readings found in database.")
    
    if parameter_name != None:
        db_reading = db_reading.filter(Reading.parameter_name == parameter_name)
    if reading_id != None:
        db_reading = db_reading.filter(Reading.reading_id == reading_id)
    if station_id != None:
        db_reading = db_reading.filter(Reading.station_id == station_id)
    if date_start != None:
        db_reading = db_reading.filter(Reading.date >= date_start)
    if date_end != None:
        db_reading = db_reading.filter(Reading.date <= date_end)
    
    if db_reading.first() is None:
        raise HTTPException(status_code=404, detail="Reading not found.")
    
    db_reading = db_reading.first()
    db_reading.parameter_name = reading.parameter_name
    db_reading.value = reading.value
    db_reading.date = reading.date
    db_reading.time = reading.time

    db.commit()
    db.refresh(db_reading)
    return db_reading


@app.delete("/readings/{reading_id}", status_code=204, tags=["climate readings"])
async def delete_reading(current_user: Annotated[User, Security(get_current_active_user, 
                                                scopes=[])],
                        reading_id:int, db: Session = Depends(get_db)):
    
    check_authorization(current_user, "readings_admin")
    
    db_reading = db.query(Reading).filter(Reading.reading_id == reading_id).first()

    if db_reading.first() is None:
        raise HTTPException(status_code=404, detail="Reading not found.")

    db.delete(db_reading)
    db.commit()


if __name__ == "__main__":
    import uvicorn
    import socket
    hostname = socket.gethostname()
    IPAddr = socket.gethostbyname(hostname)
    uvicorn.run(app, host=IPAddr, port=8000)

# uv run uvicorn dmi_etl.api:app --host xxx.xxx.xxx.xx --port 8000
# where xxx.xxx.xxx.xx is the IPv4 address