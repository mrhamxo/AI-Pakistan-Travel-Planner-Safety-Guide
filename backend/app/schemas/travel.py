"""
Pydantic schemas for API requests and responses
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class UserProfileRequest(BaseModel):
    gender: Optional[str] = Field(None, description="male, female, other, prefer_not_to_say")
    travel_group: Optional[str] = Field(None, description="solo, family, group, couple")
    preferences: Optional[Dict[str, Any]] = None


class UserProfileResponse(BaseModel):
    id: int
    gender: Optional[str]
    travel_group: Optional[str]
    preferences: Optional[Dict[str, Any]]
    created_at: datetime

    class Config:
        from_attributes = True


class ConversationMessage(BaseModel):
    """A single message in conversation history"""
    type: str = Field(..., description="'user' or 'ai'")
    content: str = Field(..., description="Message content")
    timestamp: Optional[str] = None


class TravelQueryRequest(BaseModel):
    query: str = Field(..., description="Natural language travel query")
    origin: Optional[str] = None
    destination: Optional[str] = None
    travel_date: Optional[datetime] = None
    user_profile: Optional[UserProfileRequest] = None
    conversation_history: Optional[List[ConversationMessage]] = Field(
        None, 
        description="Previous messages for context-aware responses"
    )


class TransportOption(BaseModel):
    mode: str  # bus, van, train, rickshaw, ride_hailing
    estimated_fare_pkr: Optional[float] = None
    fare_range_pkr: Optional[Dict[str, float]] = None
    estimated_time_hours: Optional[float] = None
    safety_notes: Optional[str] = None
    availability: Optional[str] = None
    risk_level: Optional[str] = None


class RouteInfo(BaseModel):
    route_name: Optional[str] = None
    distance_km: Optional[float] = None
    estimated_time_hours: Optional[float] = None
    safety_score: Optional[float] = None
    risk_level: str  # recommended, caution, avoid
    transport_options: List[TransportOption] = []
    warnings: List[str] = []
    alternatives: List[str] = []


class TravelQueryResponse(BaseModel):
    query: str
    response: str  # AI-generated response
    routes: List[RouteInfo] = []
    safety_alerts: List[Dict[str, Any]] = []
    cost_estimate: Optional[Dict[str, Any]] = None
    recommendations: List[str] = []
    uncertainty_notes: Optional[str] = None  # AI explains data limitations


class RouteResponse(BaseModel):
    id: int
    origin: str
    destination: str
    route_name: Optional[str]
    distance_km: Optional[float]
    estimated_time_hours: Optional[float]
    safety_score: Optional[float]
    risk_level: str
    weather_risk: Optional[str]
    transport_options: Optional[Dict[str, Any]]

    class Config:
        from_attributes = True


class SafetyAlertResponse(BaseModel):
    id: int
    alert_type: str
    region: str
    severity: str
    description: Optional[str]
    coordinates: Optional[Dict[str, float]]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ==================== TRIP PLANNING SCHEMAS ====================

class TripPlanRequest(BaseModel):
    """Request for AI trip planning"""
    destination: str = Field(..., description="Primary destination (e.g., Hunza, Swat, Skardu)")
    duration_days: int = Field(..., ge=1, le=30, description="Trip duration in days")
    travel_type: str = Field(..., description="solo, family, group, couple")
    num_people: int = Field(1, ge=1, le=50, description="Number of travelers")
    budget_pkr: int = Field(..., ge=10000, description="Total budget in PKR")
    travel_style: str = Field("comfort", description="budget, comfort, adventure, luxury")
    start_date: Optional[datetime] = Field(None, description="Preferred start date")
    origin_city: str = Field("Islamabad", description="Starting city")
    special_requirements: Optional[List[str]] = Field(None, description="e.g., wheelchair, elderly, children")
    preferences: Optional[Dict[str, Any]] = Field(None, description="Additional preferences")


class DailyActivity(BaseModel):
    """Single activity in a day"""
    time: str = Field(..., description="Time slot (e.g., '09:00 AM')")
    activity: str = Field(..., description="Activity description")
    location: str = Field(..., description="Location name")
    duration_hours: float = Field(1.0, description="Duration in hours")
    cost_pkr: int = Field(0, description="Estimated cost")
    notes: Optional[str] = None


class DailyItinerary(BaseModel):
    """One day of the trip"""
    day: int = Field(..., description="Day number")
    date: Optional[str] = Field(None, description="Date if specified")
    title: str = Field(..., description="Day title (e.g., 'Arrival & Rest Day')")
    route: Optional[str] = Field(None, description="Travel route for the day")
    transport: Optional[str] = Field(None, description="Transport mode")
    transport_cost: int = Field(0)
    hotel: Optional[str] = Field(None, description="Hotel/accommodation")
    hotel_cost: int = Field(0)
    meals_cost: int = Field(0)
    activities: List[DailyActivity] = []
    activities_cost: int = Field(0)
    weather_note: Optional[str] = None
    safety_note: Optional[str] = None
    tips: List[str] = []


class CostBreakdown(BaseModel):
    """Detailed cost breakdown"""
    transport: int = Field(0, description="Total transport cost")
    accommodation: int = Field(0, description="Total hotel/stay cost")
    food: int = Field(0, description="Total food/meals cost")
    activities: int = Field(0, description="Sightseeing and activities")
    miscellaneous: int = Field(0, description="Tips, permits, extras")
    total: int = Field(0, description="Grand total")
    per_person: int = Field(0, description="Cost per person")
    buffer: int = Field(0, description="Emergency buffer (10%)")


class PackingItem(BaseModel):
    """Single packing item"""
    item: str
    category: str = Field(..., description="clothing, documents, electronics, medicine, etc.")
    essential: bool = Field(True)
    notes: Optional[str] = None


class TripPlanResponse(BaseModel):
    """Complete AI-generated trip plan"""
    # Trip Summary
    destination: str
    duration_days: int
    travel_type: str
    num_people: int
    budget_pkr: int
    travel_style: str
    origin_city: str
    
    # AI Generated Content
    trip_title: str = Field(..., description="Catchy trip title")
    best_time_to_visit: str
    weather_summary: str
    
    # Daily Itinerary
    daily_plan: List[DailyItinerary] = []
    
    # Cost Analysis
    cost_breakdown: CostBreakdown
    budget_status: str = Field(..., description="under_budget, on_budget, over_budget")
    cost_saving_tips: List[str] = []
    
    # Safety & Warnings
    safety_notes: List[str] = []
    weather_warnings: List[str] = []
    road_conditions: List[str] = []
    
    # Northern Area Specific
    altitude_warnings: List[str] = []
    connectivity_notes: List[str] = []
    fuel_stops: List[str] = []
    
    # Packing & Preparation
    packing_checklist: List[PackingItem] = []
    documents_required: List[str] = []
    emergency_contacts: List[Dict[str, str]] = []
    
    # Additional Info
    local_tips: List[str] = []
    food_recommendations: List[str] = []
    must_visit_spots: List[str] = []
    
    # Uncertainty & Disclaimers
    uncertainty_notes: Optional[str] = None
    data_freshness: Optional[str] = None


class QuickTripRequest(BaseModel):
    """Simple natural language trip request"""
    query: str = Field(..., description="e.g., 'Plan a 5-day family trip to Hunza under 150k'")
    user_profile: Optional[UserProfileRequest] = None
