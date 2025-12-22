"""
FastAPI main application for AI Pakistan Travel & Safety Guide

This is the main entry point for the API server. It provides endpoints for:
- Travel query processing (AI-powered)
- Trip planning and itinerary generation
- Safety alerts and route information
- Emergency information

Author: AI Pakistan Travel Guide Team
Version: 2.0.0 (AI Travel Agency Edition)
"""
import re
from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from typing import Optional
import os
from pathlib import Path
from dotenv import load_dotenv

from app.database import init_db, get_db
from app.logging_config import setup_logging, Loggers
from app.schemas.travel import (
    TravelQueryRequest,
    TravelQueryResponse,
    UserProfileRequest,
    UserProfileResponse,
    TripPlanRequest,
    TripPlanResponse,
    QuickTripRequest,
)
from app.ai.orchestrator import TravelAIOrchestrator
from app.models.travel import UserProfile, TravelQuery
from sqlalchemy.orm import Session

# Load environment variables
_dotenv_path = Path(__file__).resolve().parents[1] / ".env"  # backend/.env
load_dotenv(dotenv_path=_dotenv_path)

# Setup logging
logger = setup_logging(os.getenv("LOG_LEVEL", "INFO"))
api_logger = Loggers.api()

# Initialize AI orchestrator (lazy: allow server to start without GROQ_API_KEY)
ai_orchestrator = None


def _parse_travel_date(query: str) -> Optional[datetime]:
    """
    Parse travel date from natural language query.
    
    Supports:
    - Relative dates: "tomorrow", "today", "next week"
    - Explicit dates: "15/12/2024", "15th December"
    
    Args:
        query: Natural language query string
        
    Returns:
        Parsed datetime or None if not found
    """
    query_lower = query.lower()
    today = datetime.now()

    # Keywords for relative dates
    if "tomorrow" in query_lower:
        return today + timedelta(days=1)
    if "today" in query_lower:
        return today
    if "next week" in query_lower:
        return today + timedelta(days=7)

    # Try to extract explicit date
    date_patterns = [
        r"(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})",  # 15/12/2024
        r"(\d{1,2})(?:st|nd|rd|th)?\s+(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)",
    ]
    months = {"jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
              "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12}
    
    for pattern in date_patterns:
        match = re.search(pattern, query_lower)
        if match:
            try:
                groups = match.groups()
                if len(groups) == 3 and groups[2].isdigit():  # dd/mm/yyyy
                    day, month, year = int(groups[0]), int(groups[1]), int(groups[2])
                    if year < 100:
                        year += 2000
                    return datetime(year, month, day)
                elif len(groups) == 2:  # 15th December
                    day = int(groups[0])
                    month = months.get(groups[1][:3], 1)
                    return datetime(today.year, month, day)
            except (ValueError, IndexError):
                api_logger.debug(f"Failed to parse date from: {query}")
    return None


def _get_ai_orchestrator() -> TravelAIOrchestrator:
    """
    Get or initialize the AI orchestrator.
    
    Raises:
        HTTPException: If GROQ_API_KEY is not configured
    """
    global ai_orchestrator
    if ai_orchestrator is None:
        try:
            api_logger.info("Initializing AI orchestrator...")
            ai_orchestrator = TravelAIOrchestrator()
            api_logger.info("AI orchestrator initialized successfully")
        except ValueError as e:
            api_logger.error(f"AI initialization failed: {e}")
            raise HTTPException(
                status_code=503,
                detail="AI is not configured. Set GROQ_API_KEY in backend/.env and restart the server."
            )
        except Exception as e:
            api_logger.error(f"Unexpected AI initialization error: {e}")
            raise HTTPException(
                status_code=503,
                detail=f"AI initialization failed: {str(e)}"
            )
    return ai_orchestrator


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events for startup and shutdown."""
    # Startup
    api_logger.info("Starting AI Pakistan Travel Guide API...")
    try:
        init_db()
        api_logger.info("Database initialized successfully")
    except Exception as e:
        api_logger.error(f"Database initialization failed: {e}")
        raise
    
    api_logger.info("API server ready to accept requests")
    yield
    
    # Shutdown
    api_logger.info("Shutting down API server...")


app = FastAPI(
    title="AI Pakistan Travel & Safety Guide",
    description="""
    AI-powered travel planning platform for Pakistan.
    
    Features:
    - Complete trip planning with day-by-day itineraries
    - Safety assessment and real-time alerts
    - Cost optimization and budget planning
    - Northern areas specialized guidance
    
    Version 2.0 - AI Travel Agency Edition
    """,
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
# Default origins include localhost for development and Render domains for production
default_origins = (
    "http://localhost:3000,"
    "http://localhost:5173,"
    "https://pakistan-travel-guide.onrender.com,"
    "https://ai-pakistan-travel-frontend.onrender.com"
)
cors_origins = os.getenv("CORS_ORIGINS", default_origins).split(",")
# Strip whitespace from origins
cors_origins = [origin.strip() for origin in cors_origins if origin.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "AI Pakistan Travel & Safety Guide API",
        "version": "1.0.0",
        "status": "operational"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


@app.post("/api/travel/query", response_model=TravelQueryResponse)
async def travel_query(
    request: TravelQueryRequest,
    db: Session = Depends(get_db)
):
    """
    Process a natural language travel query.
    
    This endpoint accepts free-form travel questions and returns:
    - AI-generated travel advice
    - Route information with safety scores
    - Cost estimates for different transport modes
    - Safety recommendations
    
    Example queries:
    - "Is it safe to travel from Islamabad to Swat tomorrow?"
    - "Best way to go from Lahore to Murree with family?"
    """
    api_logger.info(f"Travel query received: {request.query[:100]}...")
    
    try:
        orchestrator = _get_ai_orchestrator()
        
        # Format conversation history for orchestrator
        conversation_history = None
        if request.conversation_history:
            conversation_history = [
                {"type": msg.type, "content": msg.content}
                for msg in request.conversation_history
            ]
        
        # Process query with AI
        api_logger.debug("Processing query with AI orchestrator")
        result = await orchestrator.process_travel_query(
            query=request.query,
            origin=request.origin,
            destination=request.destination,
            travel_date=request.travel_date.isoformat() if request.travel_date else None,
            user_profile=request.user_profile.dict() if request.user_profile else None,
            conversation_history=conversation_history
        )

        # Extract origin/destination from AI result if not in request
        origin = request.origin
        destination = request.destination
        routes = result.get("routes", [])
        if routes and len(routes) > 0:
            route_name = routes[0].get("route_name", "")
            if " to " in route_name:
                parts = route_name.split(" to ", 1)
                origin = origin or parts[0].strip()
                destination = destination or parts[1].strip()

        # Parse travel date from query if not provided
        travel_date = request.travel_date
        if not travel_date:
            travel_date = _parse_travel_date(request.query)

        # Create user profile if provided
        user_profile_id = None
        if request.user_profile:
            try:
                db_profile = UserProfile(
                    gender=request.user_profile.gender,
                    travel_group=request.user_profile.travel_group,
                    preferences={}
                )
                db.add(db_profile)
                db.commit()
                db.refresh(db_profile)
                user_profile_id = db_profile.id
                api_logger.debug(f"Created user profile: {user_profile_id}")
            except Exception as profile_error:
                api_logger.warning(f"Failed to create user profile: {profile_error}")

        # Store query in database for history
        try:
            db_query = TravelQuery(
                query_text=request.query,
                origin=origin,
                destination=destination,
                travel_date=travel_date,
                user_profile_id=user_profile_id,
                response=result.get("response", "")
            )
            db.add(db_query)
            db.commit()
            api_logger.debug(f"Query saved to database: {db_query.id}")
        except Exception as db_error:
            api_logger.warning(f"Failed to save query to database: {db_error}")
            db.rollback()

        api_logger.info(f"Travel query processed successfully for: {origin} -> {destination}")
        return TravelQueryResponse(**result)

    except HTTPException:
        raise
    except Exception as e:
        api_logger.exception("Unhandled error in /api/travel/query")
        raise HTTPException(
            status_code=500, 
            detail="An error occurred while processing your travel query. Please try again."
        )


@app.post("/api/user/profile", response_model=UserProfileResponse)
async def create_user_profile(
    profile: UserProfileRequest,
    db: Session = Depends(get_db)
):
    """Create or update user profile"""
    try:
        db_profile = UserProfile(
            gender=profile.gender,
            travel_group=profile.travel_group,
            preferences=profile.preferences
        )
        db.add(db_profile)
        db.commit()
        db.refresh(db_profile)
        return UserProfileResponse.model_validate(db_profile)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating profile: {str(e)}")


@app.get("/api/routes/{origin}/{destination}")
async def get_route(
    origin: str,
    destination: str,
    db: Session = Depends(get_db)
):
    """Get route information"""
    from app.services.route_service import RouteService
    
    route_service = RouteService()
    route_info = route_service.get_route_info(origin, destination)
    
    if not route_info.get("distance_km"):
        raise HTTPException(
            status_code=404,
            detail=f"Route from {origin} to {destination} not found"
        )
    
    return route_info


@app.get("/api/safety/alerts")
async def get_safety_alerts(
    region: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get active safety alerts"""
    from app.models.travel import SafetyAlert
    
    query = db.query(SafetyAlert).filter(SafetyAlert.is_active == True)
    if region:
        query = query.filter(SafetyAlert.region.ilike(f"%{region}%"))
    
    alerts = query.all()
    return [
        {
            "id": alert.id,
            "alert_type": alert.alert_type,
            "region": alert.region,
            "severity": alert.severity,
            "description": alert.description,
            "coordinates": alert.coordinates,
            "is_active": alert.is_active
        }
        for alert in alerts
    ]


@app.get("/api/routes")
async def list_routes(db: Session = Depends(get_db)):
    """List all cached routes"""
    from app.models.travel import Route
    
    routes = db.query(Route).limit(100).all()
    return [
        {
            "id": r.id,
            "origin": r.origin,
            "destination": r.destination,
            "distance_km": r.distance_km,
            "estimated_time_hours": r.estimated_time_hours,
            "safety_score": r.safety_score,
            "risk_level": r.risk_level,
        }
        for r in routes
    ]


@app.get("/api/transport-options")
async def list_transport_options(
    origin: Optional[str] = None,
    destination: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List transport options, optionally filtered by route"""
    from app.models.transport import TransportOption
    
    query = db.query(TransportOption)
    if origin:
        query = query.filter(TransportOption.origin.ilike(f"%{origin}%"))
    if destination:
        query = query.filter(TransportOption.destination.ilike(f"%{destination}%"))
    
    options = query.limit(100).all()
    return [
        {
            "id": o.id,
            "mode": o.mode,
            "origin": o.origin,
            "destination": o.destination,
            "typical_fare_pkr": o.typical_fare_pkr,
            "fare_range_pkr": o.fare_range_pkr,
            "estimated_time_hours": o.estimated_time_hours,
            "availability": o.availability,
            "safety_notes": o.safety_notes,
            "night_travel_safe": o.night_travel_safe,
        }
        for o in options
    ]


@app.post("/api/alerts/refresh")
async def refresh_alerts():
    """
    Fetch latest weather alerts from OpenWeatherMap and save to database.
    
    Scans major Pakistan cities for weather conditions that could affect travel:
    - Heavy rain (flood risk)
    - Fog (visibility issues)
    - Snow (mountain road closures)
    - Strong winds
    """
    from app.services.weather_service import WeatherService
    
    api_logger.info("Refreshing weather alerts from OpenWeatherMap...")
    
    try:
        weather_service = WeatherService()
        new_alerts = await weather_service.fetch_and_save_alerts()
        
        api_logger.info(f"Alert refresh complete: {len(new_alerts)} new alerts added")
        return {
            "message": f"Refreshed alerts. {len(new_alerts)} new alerts added.",
            "alerts": new_alerts,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        api_logger.error(f"Failed to refresh alerts: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to refresh weather alerts. Weather API may be unavailable."
        )


@app.get("/api/queries/history")
async def get_query_history(
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """Get recent travel queries"""
    queries = db.query(TravelQuery).order_by(TravelQuery.created_at.desc()).limit(limit).all()
    return [
        {
            "id": q.id,
            "query_text": q.query_text,
            "origin": q.origin,
            "destination": q.destination,
            "travel_date": q.travel_date.isoformat() if q.travel_date is not None else None,
            "created_at": q.created_at.isoformat() if q.created_at is not None else None,
        }
        for q in queries
    ]


# ==================== TRIP PLANNING ENDPOINTS ====================

@app.post("/api/trip/plan")
async def create_trip_plan(request: TripPlanRequest, db: Session = Depends(get_db)):
    """
    Generate a complete AI-powered trip plan with day-by-day itinerary.
    
    This is the main trip planning endpoint that acts as a virtual travel agency.
    Returns a comprehensive trip plan including:
    - Day-by-day itinerary with activities
    - Cost breakdown (transport, accommodation, food, activities)
    - Safety notes and warnings
    - Packing checklist
    - Emergency contacts
    """
    api_logger.info(
        f"Trip plan request: {request.destination} for {request.duration_days} days, "
        f"{request.travel_type} ({request.num_people} people), budget: PKR {request.budget_pkr}"
    )
    
    try:
        orchestrator = _get_ai_orchestrator()
        
        # Validate request parameters
        if request.duration_days < 1 or request.duration_days > 30:
            raise HTTPException(
                status_code=400,
                detail="Trip duration must be between 1 and 30 days"
            )
        
        if request.budget_pkr < 10000:
            raise HTTPException(
                status_code=400,
                detail="Minimum budget is PKR 10,000"
            )
        
        # Generate trip plan
        api_logger.debug("Generating trip plan with AI...")
        trip_plan = await orchestrator.generate_trip_plan(
            destination=request.destination,
            duration_days=request.duration_days,
            travel_type=request.travel_type,
            num_people=request.num_people,
            budget_pkr=request.budget_pkr,
            travel_style=request.travel_style,
            origin_city=request.origin_city,
            start_date=request.start_date.isoformat() if request.start_date else None,
            special_requirements=request.special_requirements,
        )
        
        api_logger.info(
            f"Trip plan generated successfully for {request.destination}: "
            f"{len(trip_plan.get('daily_plan', []))} days planned"
        )
        return trip_plan
        
    except HTTPException:
        raise
    except Exception as e:
        api_logger.exception("Error generating trip plan")
        raise HTTPException(
            status_code=500, 
            detail="Failed to generate trip plan. Please try again with different parameters."
        )


@app.post("/api/trip/quick-plan")
async def quick_trip_plan(request: QuickTripRequest, db: Session = Depends(get_db)):
    """
    Generate a trip plan from natural language query.
    
    The AI parses your request to extract:
    - Destination
    - Duration
    - Budget
    - Travel type (solo, family, group, couple)
    - Travel style preference
    
    Example queries:
    - "Plan a 5-day family trip to Hunza under 150k"
    - "Solo budget trip to Skardu"
    - "Group tour to Swat for 10 people"
    """
    api_logger.info(f"Quick trip plan request: {request.query[:100]}...")
    
    try:
        orchestrator = _get_ai_orchestrator()
        
        if len(request.query.strip()) < 10:
            raise HTTPException(
                status_code=400,
                detail="Please provide a more detailed trip request (e.g., '5 day family trip to Hunza')"
            )
        
        # Parse the natural language query
        api_logger.debug("Parsing natural language trip request...")
        parsed_request = await orchestrator.parse_quick_trip_request(request.query)
        api_logger.info(
            f"Parsed request: {parsed_request['destination']}, "
            f"{parsed_request['duration_days']} days, PKR {parsed_request['budget_pkr']}"
        )
        
        # Generate trip plan with parsed parameters
        trip_plan = await orchestrator.generate_trip_plan(
            destination=parsed_request["destination"],
            duration_days=parsed_request["duration_days"],
            travel_type=parsed_request["travel_type"],
            num_people=parsed_request["num_people"],
            budget_pkr=parsed_request["budget_pkr"],
            travel_style=parsed_request["travel_style"],
            origin_city=parsed_request["origin_city"],
            start_date=parsed_request.get("start_date"),
            special_requirements=parsed_request.get("special_requirements"),
        )
        
        # Include parsed parameters in response for transparency
        trip_plan["_parsed_request"] = parsed_request
        
        api_logger.info(f"Quick trip plan generated for {parsed_request['destination']}")
        return trip_plan
        
    except HTTPException:
        raise
    except Exception as e:
        api_logger.exception("Error generating quick trip plan")
        raise HTTPException(
            status_code=500, 
            detail="Failed to generate trip plan. Please try rephrasing your request."
        )


@app.get("/api/trip/destinations")
async def get_destinations():
    """Get list of supported tourist destinations with basic info."""
    destinations = [
        {
            "name": "Hunza",
            "region": "Gilgit-Baltistan",
            "altitude_m": 2500,
            "best_season": "April - October",
            "highlights": ["Attabad Lake", "Eagle's Nest", "Baltit Fort", "Passu Cones"],
            "difficulty": "moderate",
            "min_days": 5,
            "image_url": "/images/hunza.jpg",
        },
        {
            "name": "Skardu",
            "region": "Gilgit-Baltistan",
            "altitude_m": 2228,
            "best_season": "May - September",
            "highlights": ["Shangrila", "Deosai", "Upper Kachura Lake"],
            "difficulty": "challenging",
            "min_days": 6,
            "image_url": "/images/skardu.jpg",
        },
        {
            "name": "Swat",
            "region": "KPK",
            "altitude_m": 980,
            "best_season": "March - October",
            "highlights": ["Malam Jabba", "Kalam Valley", "Mingora"],
            "difficulty": "easy",
            "min_days": 3,
            "image_url": "/images/swat.jpg",
        },
        {
            "name": "Naran",
            "region": "KPK",
            "altitude_m": 2409,
            "best_season": "June - September",
            "highlights": ["Lake Saif ul Malook", "Lulusar Lake", "Babusar Pass"],
            "difficulty": "easy",
            "min_days": 3,
            "image_url": "/images/naran.jpg",
        },
        {
            "name": "Chitral",
            "region": "KPK",
            "altitude_m": 1500,
            "best_season": "April - October",
            "highlights": ["Kalash Valley", "Shandur Pass", "Chitral Fort"],
            "difficulty": "challenging",
            "min_days": 5,
            "image_url": "/images/chitral.jpg",
        },
        {
            "name": "Murree",
            "region": "Punjab",
            "altitude_m": 2291,
            "best_season": "Year round",
            "highlights": ["Mall Road", "Pindi Point", "Patriata"],
            "difficulty": "easy",
            "min_days": 2,
            "image_url": "/images/murree.jpg",
        },
        {
            "name": "Gilgit",
            "region": "Gilgit-Baltistan",
            "altitude_m": 1500,
            "best_season": "April - October",
            "highlights": ["Naltar Valley", "Kargah Buddha", "Gilgit River"],
            "difficulty": "moderate",
            "min_days": 4,
            "image_url": "/images/gilgit.jpg",
        },
        {
            "name": "Kaghan",
            "region": "KPK",
            "altitude_m": 2134,
            "best_season": "May - September",
            "highlights": ["Shogran", "Siri Paye", "Kaghan Valley"],
            "difficulty": "easy",
            "min_days": 3,
            "image_url": "/images/kaghan.jpg",
        },
    ]
    return destinations


@app.get("/api/trip/packing-checklist")
async def get_packing_checklist(
    destination: str,
    duration_days: int = 5,
    travel_type: str = "family"
):
    """Get a packing checklist for a specific destination."""
    # Base checklist items
    base_items = [
        {"item": "CNIC/Passport", "category": "documents", "essential": True},
        {"item": "Cash (PKR)", "category": "documents", "essential": True},
        {"item": "Phone charger", "category": "electronics", "essential": True},
        {"item": "Power bank", "category": "electronics", "essential": True},
        {"item": "First aid kit", "category": "medicine", "essential": True},
        {"item": "Personal medications", "category": "medicine", "essential": True},
        {"item": "Sunscreen", "category": "toiletries", "essential": True},
        {"item": "Toiletries bag", "category": "toiletries", "essential": True},
    ]
    
    # Destination-specific items
    destination_lower = destination.lower()
    
    if destination_lower in ["hunza", "skardu", "gilgit", "chitral"]:
        base_items.extend([
            {"item": "Warm jacket", "category": "clothing", "essential": True, "notes": "Nights are cold"},
            {"item": "Altitude sickness tablets", "category": "medicine", "essential": True},
            {"item": "Offline maps", "category": "electronics", "essential": True, "notes": "No internet in remote areas"},
            {"item": "Flashlight", "category": "electronics", "essential": True},
            {"item": "Water bottle", "category": "misc", "essential": True},
            {"item": "Snacks", "category": "food", "essential": False},
            {"item": "Camera", "category": "electronics", "essential": False},
            {"item": "Sunglasses", "category": "accessories", "essential": True},
        ])
    
    if destination_lower in ["naran", "kaghan", "murree"]:
        base_items.extend([
            {"item": "Light jacket", "category": "clothing", "essential": True},
            {"item": "Umbrella/raincoat", "category": "clothing", "essential": True},
            {"item": "Comfortable walking shoes", "category": "clothing", "essential": True},
        ])
    
    if travel_type == "family":
        base_items.extend([
            {"item": "Kids snacks", "category": "food", "essential": True},
            {"item": "Entertainment for kids", "category": "misc", "essential": False},
            {"item": "Extra clothes for children", "category": "clothing", "essential": True},
        ])
    
    if duration_days > 5:
        base_items.extend([
            {"item": "Laundry bag", "category": "misc", "essential": False},
            {"item": "Extra batteries", "category": "electronics", "essential": True},
        ])
    
    return {"destination": destination, "checklist": base_items}


@app.get("/api/trip/emergency-info")
async def get_emergency_info(region: Optional[str] = None):
    """Get emergency contact information for travel regions."""
    emergency_info = {
        "general": {
            "police": "15",
            "ambulance": "115",
            "rescue": "1122",
            "tourist_helpline": "1422",
        },
        "gilgit_baltistan": {
            "rescue_1122": "1122",
            "ptdc_gilgit": "+92-5811-920356",
            "aga_khan_hospital": "+92-5811-457204",
            "police": "+92-5811-920333",
        },
        "kpk": {
            "rescue_1122": "1122",
            "swat_hospital": "+92-946-9240033",
            "tourist_police": "+92-946-9240000",
        },
        "punjab": {
            "rescue_1122": "1122",
            "motorway_police": "130",
            "highway_patrol": "+92-51-9250566",
        },
    }
    
    tips = [
        "Always share your live location with family",
        "Keep hotel contact saved offline",
        "Carry physical copies of important documents",
        "Know the nearest hospital location",
        "Keep emergency cash separate from wallet",
        "Register with local police if staying long",
    ]
    
    if region and region.lower() in emergency_info:
        return {
            "region": region,
            "contacts": emergency_info[region.lower()],
            "general": emergency_info["general"],
            "tips": tips,
        }
    
    return {
        "all_regions": emergency_info,
        "tips": tips,
    }


# ============================================
# Transport Schedules API
# ============================================

@app.get("/api/transport/schedules")
async def get_transport_schedules(
    origin: Optional[str] = None,
    destination: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get bus/transport schedules with operator details."""
    from app.models.transport import TransportRoute, TransportOption
    import json
    
    # Get all transport routes
    routes = db.query(TransportRoute).filter(TransportRoute.is_active == True).all()
    
    # Get transport options for route context
    options_query = db.query(TransportOption)
    if origin and destination:
        options_query = options_query.filter(
            TransportOption.origin.ilike(f"%{origin}%"),
            TransportOption.destination.ilike(f"%{destination}%")
        )
    options = options_query.all()
    
    # Format response
    schedules = []
    for route in routes:
        try:
            departure_times = json.loads(route.departure_times) if route.departure_times else []
        except (json.JSONDecodeError, TypeError):
            departure_times = []
        
        schedules.append({
            "id": route.id,
            "route_code": route.route_code,
            "operator": route.operator,
            "departure_times": departure_times,
            "frequency": route.frequency,
            "is_active": route.is_active,
            "last_verified": route.last_verified.isoformat() if route.last_verified else None,
        })
    
    # Format transport options
    transport_options = [
        {
            "id": opt.id,
            "mode": opt.mode,
            "origin": opt.origin,
            "destination": opt.destination,
            "fare_pkr": opt.typical_fare_pkr,
            "time_hours": opt.estimated_time_hours,
            "availability": opt.availability,
            "safety_notes": opt.safety_notes,
        }
        for opt in options
    ]
    
    return {
        "schedules": schedules,
        "transport_options": transport_options,
        "operators": list(set(s["operator"] for s in schedules)),
        "total_routes": len(schedules),
    }


@app.get("/api/transport/operators")
async def get_transport_operators(db: Session = Depends(get_db)):
    """Get list of all transport operators."""
    from app.models.transport import TransportRoute
    import json
    
    routes = db.query(TransportRoute).filter(TransportRoute.is_active == True).all()
    
    operators = {}
    for route in routes:
        if route.operator not in operators:
            try:
                times = json.loads(route.departure_times) if route.departure_times else []
            except (json.JSONDecodeError, TypeError):
                times = []
            
            operators[route.operator] = {
                "name": route.operator,
                "routes": [],
                "total_departures": 0,
            }
        
        operators[route.operator]["routes"].append(route.route_code)
        try:
            times = json.loads(route.departure_times) if route.departure_times else []
            operators[route.operator]["total_departures"] += len(times)
        except (json.JSONDecodeError, TypeError):
            pass
    
    return {
        "operators": list(operators.values()),
        "total_operators": len(operators),
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
