"""
AI tools/functions for LangChain agents
"""
from langchain.tools import tool
from typing import Dict, Optional
from app.services.route_service import RouteService
from app.services.weather_service import WeatherService
from app.services.safety_service import SafetyService


route_service = RouteService()
weather_service = WeatherService()
safety_service = SafetyService()


@tool
def get_route_info(origin: str, destination: str) -> Dict:
    """Get route information including distance, transport options, and estimated travel time.
    
    Args:
        origin: Origin city or location
        destination: Destination city or location
    
    Returns:
        Dictionary with route information
    """
    return route_service.get_route_info(origin, destination)


@tool
def get_weather_risks(city: str) -> Dict:
    """Get weather data and assess travel risks for a city.
    
    Args:
        city: City name to check weather for
    
    Returns:
        Dictionary with weather risks and warnings
    """
    # This will be async in actual implementation
    # For now, return a placeholder structure
    return {
        "city": city,
        "risk_level": "unknown",
        "risks": [],
        "warnings": []
    }


@tool
def calculate_safety_score(
    route_info: Dict,
    weather_risks: Dict,
    time_of_day: Optional[str] = None,
    user_profile: Optional[Dict] = None
) -> Dict:
    """Calculate safety score for a route based on multiple factors.
    
    Args:
        route_info: Route information dictionary
        weather_risks: Weather risk assessment
        time_of_day: Time of day (optional)
        user_profile: User profile with gender and travel_group (optional)
    
    Returns:
        Dictionary with safety score and risk level
    """
    return safety_service.calculate_safety_score(
        route_info, weather_risks, time_of_day, user_profile
    )


@tool
def get_transport_options(origin: str, destination: str) -> list:
    """Get available transport options with fare estimates.
    
    Args:
        origin: Origin city
        destination: Destination city
    
    Returns:
        List of transport options with details
    """
    distance = route_service.get_distance(origin, destination)
    return route_service.get_transport_options(origin, destination, distance)


@tool
def get_safety_advice(route: str, risk_level: str, user_profile: Optional[Dict] = None) -> list:
    """Get personalized safety advice for a route.
    
    Args:
        route: Route description
        risk_level: Risk level (recommended, caution, avoid)
        user_profile: User profile (optional)
    
    Returns:
        List of safety advice strings
    """
    return safety_service.get_safety_advice(route, risk_level, user_profile)
