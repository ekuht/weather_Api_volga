from sqlalchemy import Column, Integer, Float, String, DateTime
from sqlalchemy.orm import declarative_base
from datetime import datetime


Base = declarative_base()


class WeatherData(Base):
    __tablename__ = 'weather'
    id = Column(Integer, primary_key=True)
    temperature = Column(Float)
    wind_speed = Column(Float)
    wind_direction = Column(String(50))
    pressure = Column(Float)
    precipitation_type = Column(String(50))
    precipitation_amount = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)
