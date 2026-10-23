from fastapi import FastAPI, Query, Depends, HTTPException
from sqlalchemy import create_engine, Column, Integer, String, Numeric, Time, Date, Identity
from sqlalchemy.orm import sessionmaker, Session
import sqlalchemy
from pydantic import BaseModel
from typing import Annotated
import datetime

from dmi_etl.DB_operations import *

app = FastAPI()
engine = get_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = sqlalchemy.orm.declarative_base()


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


class ParameterCreate(BaseModel):
    name: str
    unit: str
    frequency: str

class ParameterResponse(BaseModel):
    name: str
    unit: str
    frequency: str

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

@app.post("/parameters/", response_model=ParameterResponse)
async def create_item(parameter: ParameterCreate, db: Session = Depends(get_db)):
    db_parameter = Parameter(**parameter.model_dump())
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


@app.post("/readings/", response_model=ReadingResponse)
async def create_reading(reading: ReadingCreate, db: Session = Depends(get_db)):
    db_reading = Reading(**reading.model_dump())
    db.add(db_reading)
    db.commit()
    db.refresh(db_reading)
    return db_reading


@app.get("/readings/", response_model=list[ReadingResponse])
async def read_reading(
    parameter_name: Annotated[str | None, Query] = None,
    reading_id: Annotated[int | None, Query] = None,
    station_id: Annotated[str | None, Query] = None, 
    date_start: Annotated[datetime.date | None, Query] = None,
    date_end: Annotated[datetime.date | None, Query] = None,    db: Session = Depends(get_db)):

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

    test = db_reading.all()

    db_reading = db_reading.first()
    
    
    if db_reading is None:
        raise HTTPException(status_code=404, detail="Reading not found")
    return test


@app.put("/readings/", response_model=ReadingResponse)
async def update_reading(
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

    #db.execute(sqlalchemy.update(db_reading, reading))

    db.commit()
    db.refresh(db_reading)
    return db_reading


@app.delete("/readings/{reading_id}", status_code=204)
async def delete_reading(reading_id:int, db: Session = Depends(get_db)):
    db_reading = db.query(Reading).filter(Reading.reading_id == reading_id).first()

    if db_reading is None:
        raise HTTPException(status_code=404, detail="Reading not found")

    db.delete(db_reading)
    db.commit()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)