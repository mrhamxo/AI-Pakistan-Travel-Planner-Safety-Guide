"""
Database models for travel and safety data
"""
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, JSON
from sqlalchemy.sql import func
from app.database import Base


class UserProfile(Base):
    """User profile for personalized safety advice"""
    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True, index=True)
    gender = Column(String(20))  # male, female, other, prefer_not_to_say
    travel_group = Column(String(20))  # solo, family, group, couple
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    preferences = Column(JSON)  # Store user preferences as JSON


class TravelQuery(Base):
    """Store user travel queries for learning"""
    __tablename__ = "travel_queries"

    id = Column(Integer, primary_key=True, index=True)
    query_text = Column(Text, nullable=False)
    origin = Column(String(200))
    destination = Column(String(200))
    travel_date = Column(DateTime(timezone=True))
    user_profile_id = Column(Integer)
    response = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Route(Base):
    """Route information and safety scores"""
    __tablename__ = "routes"

    id = Column(Integer, primary_key=True, index=True)
    origin = Column(String(200), nullable=False)
    destination = Column(String(200), nullable=False)
    route_name = Column(String(200))
    distance_km = Column(Float)
    estimated_time_hours = Column(Float)
    safety_score = Column(Float)  # 0-100
    risk_level = Column(String(20))  # recommended, caution, avoid
    weather_risk = Column(String(50))
    time_of_day_safety = Column(JSON)  # Safety by time of day
    transport_options = Column(JSON)  # Available transport modes
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class SafetyAlert(Base):
    """Real-time safety alerts and disasters"""
    __tablename__ = "safety_alerts"

    id = Column(Integer, primary_key=True, index=True)
    alert_type = Column(String(50), nullable=False)  # flood, landslide, protest, road_closure, fog
    region = Column(String(200), nullable=False)
    severity = Column(String(20))  # low, medium, high, critical
    description = Column(Text)
    coordinates = Column(JSON)  # lat, lng
    start_time = Column(DateTime(timezone=True))
    end_time = Column(DateTime(timezone=True))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
