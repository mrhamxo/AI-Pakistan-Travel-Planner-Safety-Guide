"""
Safety assessment and risk scoring service

Provides:
- Route safety scoring (0-100 scale)
- Risk level classification (recommended, caution, avoid)
- Personalized safety advice based on user profile
"""
from typing import Dict, List, Optional
from datetime import datetime, time

from app.logging_config import Loggers
from app.services.weather_service import WeatherService

# Logger for safety operations
safety_logger = Loggers.safety()


class SafetyService:
    """Service for assessing route safety and providing safety advice"""

    def __init__(self):
        self.weather_service = WeatherService()

    def calculate_safety_score(
        self,
        route_info: Dict,
        weather_risks: Dict,
        time_of_day: Optional[str] = None,
        user_profile: Optional[Dict] = None
    ) -> Dict:
        """
        Calculate comprehensive safety score (0-100)
        Higher score = safer
        """
        base_score = 70  # Start with moderate safety assumption

        # Weather risk adjustment
        weather_risk_level = weather_risks.get("risk_level", "unknown")
        if weather_risk_level == "high":
            base_score -= 30
        elif weather_risk_level == "medium":
            base_score -= 15
        elif weather_risk_level == "low":
            base_score += 10

        # Time of day adjustment
        if time_of_day:
            hour = self._parse_time_of_day(time_of_day)
            if hour is not None:
                # Night travel (8 PM - 6 AM) is less safe
                if hour >= 20 or hour < 6:
                    base_score -= 20
                # Early morning (6 AM - 9 AM) is safer
                elif 6 <= hour < 9:
                    base_score += 5
                # Daytime (9 AM - 6 PM) is safest
                elif 9 <= hour < 18:
                    base_score += 10

        # User profile adjustments
        if user_profile:
            gender = user_profile.get("gender", "").lower()
            travel_group = user_profile.get("travel_group", "").lower()

            # Solo female travelers need extra caution
            if gender == "female" and travel_group == "solo":
                base_score -= 15
            # Families are generally safer
            elif travel_group == "family":
                base_score += 5

        # Route-specific risks
        route_region = route_info.get("region", "").lower()
        
        # Northern areas have different risk profiles
        northern_areas = ["gilgit", "hunza", "skardu", "chitral", "swat"]
        if any(area in route_region for area in northern_areas):
            # Mountainous areas have landslide risks
            if weather_risks.get("risks", []):
                base_score -= 10

        # Ensure score stays within bounds
        base_score = max(0, min(100, base_score))

        # Determine risk level
        if base_score >= 75:
            risk_level = "recommended"
        elif base_score >= 50:
            risk_level = "caution"
        else:
            risk_level = "avoid"

        return {
            "safety_score": round(base_score, 1),
            "risk_level": risk_level,
            "factors": self._get_safety_factors(base_score, weather_risks, time_of_day, user_profile)
        }

    def _parse_time_of_day(self, time_str: str) -> Optional[int]:
        """Parse time string to hour (0-23)"""
        try:
            # Try parsing various formats
            if ":" in time_str:
                hour = int(time_str.split(":")[0])
                return hour
            elif time_str.isdigit():
                return int(time_str)
            # Handle "morning", "afternoon", "evening", "night"
            time_str_lower = time_str.lower()
            if "morning" in time_str_lower or "am" in time_str_lower:
                return 9
            elif "afternoon" in time_str_lower:
                return 14
            elif "evening" in time_str_lower or "pm" in time_str_lower:
                return 18
            elif "night" in time_str_lower:
                return 22
        except (ValueError, TypeError, AttributeError) as e:
            safety_logger.debug(f"Could not parse time string '{time_str}': {e}")
        return None

    def _get_safety_factors(
        self,
        score: float,
        weather_risks: Dict,
        time_of_day: Optional[str],
        user_profile: Optional[Dict]
    ) -> List[str]:
        """Get list of factors affecting safety score"""
        factors = []

        weather_level = weather_risks.get("risk_level")
        if weather_level == "high":
            factors.append("Severe weather conditions")
        elif weather_level == "medium":
            factors.append("Moderate weather risks")

        if time_of_day:
            hour = self._parse_time_of_day(time_of_day)
            if hour and (hour >= 20 or hour < 6):
                factors.append("Night travel")

        if user_profile:
            if user_profile.get("gender") == "female" and user_profile.get("travel_group") == "solo":
                factors.append("Solo female traveler")

        return factors

    def get_safety_advice(
        self,
        route: str,
        risk_level: str,
        user_profile: Optional[Dict] = None
    ) -> List[str]:
        """Get personalized safety advice"""
        advice = []

        if risk_level == "avoid":
            advice.append("⚠️ Consider postponing this trip or finding alternative routes")
            advice.append("Check weather conditions and road closures before traveling")
        elif risk_level == "caution":
            advice.append("⚠️ Travel with caution - monitor conditions closely")
            advice.append("Inform someone about your travel plans")
        else:
            advice.append("✅ Route appears safe, but always stay alert")

        if user_profile:
            gender = user_profile.get("gender", "").lower()
            travel_group = user_profile.get("travel_group", "").lower()

            if gender == "female" and travel_group == "solo":
                advice.append("💡 For solo female travelers: Share live location with trusted contacts")
                advice.append("💡 Prefer daytime travel and well-lit routes")
                advice.append("💡 Use reputable transport services")

            if travel_group == "family":
                advice.append("💡 For families: Plan rest stops and keep emergency contacts ready")

        return advice
