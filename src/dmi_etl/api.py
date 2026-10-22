from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import create_engine, Column, Integer, String, Numeric, Time, Date, Identity
from sqlalchemy.orm import sessionmaker, Session
import sqlalchemy
from pydantic import BaseModel

from dmi_etl.DB_operations import *

app = FastAPI()
engine = get_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = sqlalchemy.orm.declarative_base()

#Define a SQLAlchemy models to store data in the database. Describes the tables in our schema
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

@app.post("/parameters/", response_model=ParameterResponse)
async def create_parameter(parameter: ParameterCreate, db: Session = Depends(get_db)):
    db_parameter = Parameter(**parameter.model_dump()) #dictionary representation of the model
    db.add(db_parameter)
    db.commit()
    db.refresh(db_parameter)
    return db_parameter

@app.get("/parameters/{name}", response_model=ParameterResponse)
async def read_parameter(name: str, db: Session = Depends(get_db)):
    db_parameter = db.query(Parameter).filter(Parameter.name == name).first()
    if db_parameter is None:
        raise HTTPException(status_code=404, detail="Parameter not found")
    return db_parameter

#replace the resource with what the client sends
#if the parameter exists, it will be overwritten
#if parameter does not exist, respond  with 404
#the response is the updated parameter
@app.put("/parameters/{name}", response_model=ParameterResponse) #fetch the name from the url
async def update_parameter(name: str, paramUpdate:ParameterUpdate, db: Session = Depends(get_db)):
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


@app.delete("/parameters/{name}", status_code=204)
async def delete_parameter(name:str, db: Session = Depends(get_db)):
    db_parameter = db.query(Parameter).filter(Parameter.name == name).first()
    #parameter does not exist, respond with 404
    if db_parameter is None:
        raise HTTPException(status_code=404, detail="Parameter not found")
    #parameter exists, delete it
    db.delete(db_parameter)
    db.commit()





if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)