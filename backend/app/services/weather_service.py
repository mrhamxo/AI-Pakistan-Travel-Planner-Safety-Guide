"""
Weather service integration with OpenWeatherMap

Provides:
- Current weather data for Pakistani cities
- Weather risk assessment (floods, fog, snow, wind)
- Automatic alert generation and storage
"""
import asyncio
import json
import os
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime
from typing import Any, Dict, List, Optional

from app.database import SessionLocal
from app.logging_config import Loggers
from app.models.travel import SafetyAlert

# Logger for weather operations
weather_logger = Loggers.weather()

WEATHER_BASE_URL = "https://api.openweathermap.org/data/2.5"

# Major Pakistan cities for alert checking
PAKISTAN_CITIES = [
    "Islamabad", "Lahore", "Karachi", "Peshawar", "Quetta",
    "Multan", "Faisalabad", "Rawalpindi", "Hyderabad", "Swat",
    "Gilgit", "Murree", "Skardu", "Chitral", "Abbottabad",
]


class WeatherService:
    """Service for fetching weather data and assessing risks"""

    def __init__(self):
        # Read directly from env (FastAPI app loads .env at startup)
        self.api_key = os.getenv("WEATHER_API_KEY")
        if not self.api_key:
            weather_logger.warning("WEATHER_API_KEY not set. Weather features will be limited.")
        else:
            weather_logger.debug("Weather service initialized with API key")

    def _fetch_json(self, endpoint: str, params: Dict[str, str]) -> Optional[Dict]:
        """Fetch JSON data from weather API with error handling."""
        # Hide API key in logs
        safe_params = {k: v if k != "appid" else "***" for k, v in params.items()}
        weather_logger.debug(f"Fetching: {endpoint} with params: {safe_params}")
        
        url = f"{endpoint}?{urllib.parse.urlencode(params)}"
        try:
            with urllib.request.urlopen(url, timeout=10) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                weather_logger.debug("Weather data fetched successfully")
                return data
        except urllib.error.HTTPError as e:
            weather_logger.warning(f"Weather API HTTP error: {e.code} {e.reason}")
            return None
        except urllib.error.URLError as e:
            weather_logger.warning(f"Weather API connection error: {e.reason}")
            return None
        except Exception as e:
            weather_logger.error(f"Weather API unexpected error: {e}")
            return None

    async def get_weather(self, city: str, country: str = "PK") -> Optional[Dict]:
        """Get current weather for a city"""
        if not self.api_key:
            return None

        endpoint = f"{WEATHER_BASE_URL}/weather"
        params = {"q": f"{city},{country}", "appid": self.api_key, "units": "metric"}
        return await asyncio.to_thread(self._fetch_json, endpoint, params)

    async def get_forecast(self, city: str, country: str = "PK") -> Optional[Dict]:
        """Get weather forecast"""
        if not self.api_key:
            return None

        endpoint = f"{WEATHER_BASE_URL}/forecast"
        params = {"q": f"{city},{country}", "appid": self.api_key, "units": "metric"}
        return await asyncio.to_thread(self._fetch_json, endpoint, params)

    def assess_weather_risks(self, weather_data: Optional[Dict]) -> Dict[str, Any]:
        """Assess weather-related travel risks"""
        if not weather_data:
            return {
                "risk_level": "unknown",
                "risks": [],
                "warnings": []
            }

        risks = []
        warnings = []
        risk_level = "low"

        weather = weather_data.get("weather", [{}])[0]
        main = weather_data.get("main", {})
        wind = weather_data.get("wind", {})

        # Check for heavy rain (flood risk)
        if weather.get("main") == "Rain":
            rain_volume = weather_data.get("rain", {}).get("1h", 0)
            if rain_volume > 10:  # mm per hour
                risks.append("flood")
                warnings.append("Heavy rainfall - flood risk")
                risk_level = "high"
            elif rain_volume > 5:
                risks.append("flood")
                warnings.append("Moderate rainfall - possible flooding")
                risk_level = "medium"

        # Check for fog
        if weather.get("main") == "Fog" or weather.get("description", "").lower().find("fog") != -1:
            risks.append("fog")
            warnings.append("Foggy conditions - reduced visibility")
            risk_level = "medium" if risk_level == "low" else risk_level

        # Check for snow (landslide risk in mountains)
        if weather.get("main") == "Snow":
            risks.append("landslide")
            warnings.append("Snow conditions - possible landslides in mountainous areas")
            risk_level = "high"

        # Check wind speed
        wind_speed = wind.get("speed", 0)
        if wind_speed > 20:  # m/s
            risks.append("wind")
            warnings.append("Strong winds - travel caution advised")
            risk_level = "medium" if risk_level == "low" else risk_level

        return {
            "risk_level": risk_level,
            "risks": risks,
            "warnings": warnings,
            "weather_condition": weather.get("main", "Unknown"),
            "description": weather.get("description", ""),
            "temperature": main.get("temp"),
            "humidity": main.get("humidity")
        }

    def get_city_coordinates(self, city: str) -> Optional[Dict[str, float]]:
        """Get approximate coordinates for major Pakistani cities"""
        city_coords = {
            "islamabad": {"lat": 33.6844, "lon": 73.0479},
            "karachi": {"lat": 24.8607, "lon": 67.0011},
            "lahore": {"lat": 31.5204, "lon": 74.3587},
            "rawalpindi": {"lat": 33.5651, "lon": 73.0169},
            "faisalabad": {"lat": 31.4504, "lon": 73.1350},
            "multan": {"lat": 30.1575, "lon": 71.5249},
            "peshawar": {"lat": 34.0151, "lon": 71.5249},
            "quetta": {"lat": 30.1798, "lon": 66.9750},
            "swat": {"lat": 35.2208, "lon": 72.4247},
            "murree": {"lat": 33.9072, "lon": 73.3903},
            "gilgit": {"lat": 35.9208, "lon": 74.3083},
            "hunza": {"lat": 36.3167, "lon": 74.6500},
            "skardu": {"lat": 35.2975, "lon": 75.6175},
            "chitral": {"lat": 35.8514, "lon": 71.7869},
        }
        return city_coords.get(city.lower())

    async def fetch_and_save_alerts(self) -> List[Dict]:
        """Fetch weather alerts for all major cities and save to DB."""
        weather_logger.info(f"Fetching weather alerts for {len(PAKISTAN_CITIES)} cities...")
        alerts_saved = []
        db = SessionLocal()
        
        try:
            for city in PAKISTAN_CITIES:
                try:
                    weather = await self.get_weather(city)
                    if not weather:
                        weather_logger.debug(f"No weather data for {city}")
                        continue
                    
                    risks = self.assess_weather_risks(weather)
                    if risks["risk_level"] in ("medium", "high") and risks["warnings"]:
                        for warning in risks["warnings"]:
                            # Check if similar alert exists
                            existing = db.query(SafetyAlert).filter(
                                SafetyAlert.region == city,
                                SafetyAlert.description == warning,
                                SafetyAlert.is_active == True
                            ).first()
                            
                            if not existing:
                                alert_type = "weather"
                                if "flood" in warning.lower():
                                    alert_type = "flood"
                                elif "fog" in warning.lower():
                                    alert_type = "fog"
                                elif "snow" in warning.lower() or "landslide" in warning.lower():
                                    alert_type = "landslide"
                                elif "wind" in warning.lower():
                                    alert_type = "wind"
                                
                                severity = "high" if risks["risk_level"] == "high" else "medium"
                                
                                coords = self.get_city_coordinates(city)
                                alert = SafetyAlert(
                                    alert_type=alert_type,
                                    region=city,
                                    severity=severity,
                                    description=warning,
                                    coordinates=coords,
                                    start_time=datetime.now(),
                                    is_active=True,
                                )
                                db.add(alert)
                                alerts_saved.append({
                                    "region": city,
                                    "type": alert_type,
                                    "severity": severity,
                                    "description": warning,
                                })
                                weather_logger.info(f"New alert: {city} - {alert_type} ({severity})")
                except Exception as city_error:
                    weather_logger.warning(f"Error processing {city}: {city_error}")
                    continue
            
            db.commit()
            weather_logger.info(f"Alert refresh complete: {len(alerts_saved)} new alerts")
        except Exception as e:
            db.rollback()
            weather_logger.error(f"Error saving alerts: {e}")
        finally:
            db.close()
        
        return alerts_saved

    def get_active_alerts(self, region: Optional[str] = None) -> List[Dict]:
        """Get active alerts from database."""
        db = SessionLocal()
        try:
            query = db.query(SafetyAlert).filter(SafetyAlert.is_active == True)
            if region:
                query = query.filter(SafetyAlert.region.ilike(f"%{region}%"))
            
            alerts = query.all()
            return [
                {
                    "id": a.id,
                    "alert_type": a.alert_type,
                    "region": a.region,
                    "severity": a.severity,
                    "description": a.description,
                    "coordinates": a.coordinates,
                    "is_active": a.is_active,
                }
                for a in alerts
            ]
        finally:
            db.close()
