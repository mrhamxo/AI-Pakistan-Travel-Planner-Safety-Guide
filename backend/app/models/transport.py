"""
Database models for transport options
"""
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, JSON
from sqlalchemy.sql import func
from app.database import Base


class TransportOption(Base):
    """Transport mode information"""
    __tablename__ = "transport_options"

    id = Column(Integer, primary_key=True, index=True)
    mode = Column(String(50), nullable=False)  # bus, van, train, rickshaw, ride_hailing
    route_name = Column(String(200))
    origin = Column(String(200))
    destination = Column(String(200))
    typical_fare_pkr = Column(Float)
    fare_range_pkr = Column(JSON)  # min, max
    estimated_time_hours = Column(Float)
    availability = Column(String(50))  # always, daytime_only, limited
    safety_notes = Column(Text)
    overcrowding_risk = Column(String(20))  # low, medium, high
    night_travel_safe = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class TransportRoute(Base):
    """Specific transport routes with schedules"""
    __tablename__ = "transport_routes"

    id = Column(Integer, primary_key=True, index=True)
    transport_option_id = Column(Integer)
    route_code = Column(String(50))
    operator = Column(String(200))
    departure_times = Column(JSON)  # Array of times
    frequency = Column(String(50))  # hourly, daily, weekly
    is_active = Column(Boolean, default=True)
    last_verified = Column(DateTime(timezone=True))
