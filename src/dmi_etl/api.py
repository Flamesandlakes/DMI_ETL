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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)