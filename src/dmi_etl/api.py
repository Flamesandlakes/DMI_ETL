from typing import Annotated
from fastapi import FastAPI, Query, Depends, HTTPException, Security
from sqlalchemy import create_engine, Column, Integer, String, Numeric, Time, Date, Identity
from sqlalchemy.orm import sessionmaker, Session
import sqlalchemy
from pydantic import BaseModel
import datetime
from dmi_etl.api_auth import app as auth_router
from dmi_etl.api_auth import User, get_current_active_user

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
    __tablename__ = "station_data"
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
                                                                  scopes=["parameters","admin"])],
                            parameter: ParameterCreate, db: Session = Depends(get_db)):
    # if not check_authorization(user, "write"):
    #     return
    db_parameter = Parameter(**parameter.model_dump()) #dictionary representation of the model
    db.add(db_parameter)
    db.commit()
    db.refresh(db_parameter)
    return db_parameter

@app.get("/parameters/{name}", response_model=ParameterResponse, tags=["metadata"])
async def read_parameter(current_user: Annotated[User, Security(get_current_active_user, 
                                                        scopes=["parameters"])],
                         name: str, db: Session = Depends(get_db)):
    db_parameter = db.query(Parameter).filter(Parameter.name == name).first()
    if db_parameter is None:
        raise HTTPException(status_code=404, detail="Parameter not found")
    return db_parameter

#replace the resource with what the client sends
#if the parameter exists, it will be overwritten
#if parameter does not exist, respond  with 404
#the response is the updated parameter
@app.put("/parameters/{name}", response_model=ParameterResponse, tags=["metadata"]) #fetch the name from the url
async def update_parameter(current_user: Annotated[User, Security(get_current_active_user, 
                                                        scopes=["parameters","admin"])],
                           name: str, paramUpdate:ParameterUpdate, db: Session = Depends(get_db)):
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
                                                    scopes=["parameters","admin"])],
                            name:str, db: Session = Depends(get_db)):
    db_parameter = db.query(Parameter).filter(Parameter.name == name).first()
    #parameter does not exist, respond with 404
    if db_parameter is None:
        raise HTTPException(status_code=404, detail="Parameter not found")
    #parameter exists, delete it
    db.delete(db_parameter)
    db.commit()



@app.post("/stations/", response_model=StationResponse, tags=["metadata"])
async def create_station(current_user: Annotated[User, Security(get_current_active_user, 
                                                scopes=["stations","admin"])],
                         station: StationCreate, db: Session = Depends(get_db)):
    db_station = Station(**station.model_dump()) #dictionary representation of the model
    db.add(db_station)
    db.commit()
    db.refresh(db_station)
    return db_station

@app.get("/stations/{station_id}", response_model=StationResponse, tags=["metadata"])
async def read_station(current_user: Annotated[User, Security(get_current_active_user, 
                                                scopes=["stations"])],
                        station_id: str, db: Session = Depends(get_db)):
    db_station = db.query(Station).filter(Station.station_id == station_id).first()
    if db_station is None:
        raise HTTPException(status_code=404, detail="Station not found")
    return db_station


@app.put("/stations/{station_id}", response_model=StationResponse, tags=["metadata"])
async def update_parameter(current_user: Annotated[User, Security(get_current_active_user, 
                                                scopes=["stations","admin"])],
                            station_id: str, stationUpdate:StationUpdate, db: Session = Depends(get_db)):
    db_station = db.query(Station).filter(Station.station_id == station_id).first()
    if db_station is None:
        raise HTTPException(status_code=404, detail="Station not found")
    db_station.longitude = stationUpdate.longitude
    db_station.latitude = stationUpdate.latitude
    db_station.location_name = stationUpdate.location_name
    db.commit()
    db.refresh(db_station)
    return db_station


@app.delete("/stations/{station_id}", status_code=204, tags=["metadata"])
async def delete_station(current_user: Annotated[User, Security(get_current_active_user, 
                                                scopes=["stations","admin"])],
                            station_id:str, db: Session = Depends(get_db)):
    db_station = db.query(Station).filter(Station.station_id == station_id).first()
    #parameter does not exist, respond with 404
    if db_station is None:
        raise HTTPException(status_code=404, detail="Station not found")
    #parameter exists, delete it
    db.delete(db_station)
    db.commit()


@app.post("/readings/", response_model=list[ReadingResponse], tags=["climate readings"])
async def create_reading(current_user: Annotated[User, Security(get_current_active_user, 
                                                scopes=["readings","admin"])],
                        readings: list[ReadingCreate], db: Session = Depends(get_db)):
    for reading in readings:
        db_reading = Reading(**reading.model_dump())
        db.add(db_reading)
    db.commit()
    db.refresh(db_reading)
    return db_reading


@app.get("/readings/", response_model=list[ReadingResponse], tags=["climate readings"])
async def read_reading(
    current_user: Annotated[User, Security(get_current_active_user, 
                                                scopes=["readings"])],
    parameter_name: Annotated[str | None, Query] = None,
    reading_id: Annotated[int | None, Query] = None,
    station_id: Annotated[str | None, Query] = None, 
    date_start: Annotated[datetime.date | None, Query] = None,
    date_end: Annotated[datetime.date | None, Query] = None,    
    db: Session = Depends(get_db)):

    db_reading = db.query(Reading)
    if db_reading is None:
        raise HTTPException(status_code=404, detail="Reading not found")

    if parameter_name != None:
        db_reading = db_reading.filter(Reading.parameter_name == parameter_name)
    if reading_id != None:
        db_reading = db_reading.filter( Reading.reading_id == reading_id)
    if station_id != None:
        db_reading = db_reading.filter(Reading.station_id == station_id)
    if date_start != None:
        db_reading = db_reading.filter(Reading.date >= date_start)
    if date_end != None:
        db_reading = db_reading.filter(Reading.date <= date_end)

    db_return = db_reading.all()
    
    if db_reading is None:
        raise HTTPException(status_code=404, detail="Reading not found")
    return db_return


@app.put("/readings/", response_model=ReadingResponse, tags=["climate readings"])
async def update_reading(
    current_user: Annotated[User, Security(get_current_active_user, 
                                                scopes=["readings","admin"])],
    reading: ReadingCreate,
    parameter_name: Annotated[str | None, Query] = None,
    reading_id: Annotated[int | None, Query] = None,
    station_id: Annotated[str | None, Query] = None, 
    date_start: Annotated[datetime.date | None, Query] = None,
    date_end: Annotated[datetime.date | None, Query] = None,
    db: Session = Depends(get_db)):

    db_reading = db.query(Reading)
    if db_reading is None:
        raise HTTPException(status_code=404, detail="Reading not found")
    
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
    
    if db_reading is None:
            raise HTTPException(status_code=404, detail="Reading not found")
    
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
                                                scopes=["readings","admin"])],
                        reading_id:int, db: Session = Depends(get_db)):
    db_reading = db.query(Reading).filter(Reading.reading_id == reading_id).first()

    if db_reading is None:
        raise HTTPException(status_code=404, detail="Reading not found")

    db.delete(db_reading)
    db.commit()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)