"""
Route service for calculating routes, distances, and transport options

Provides:
- Distance calculation between Pakistani cities
- Transport options with fare estimates
- OpenRouteService API integration with DB caching
"""
import json
import os
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Dict, List, Optional

from app.database import SessionLocal
from app.logging_config import Loggers
from app.models.travel import Route
from app.models.transport import TransportOption

# Logger for route operations
route_logger = Loggers.routes()


# Pakistan city coordinates for OpenRouteService
# Format: (longitude, latitude) - required by OpenRouteService
CITY_COORDINATES = {
    # Major Cities
    "islamabad": (73.0479, 33.6844),
    "rawalpindi": (73.0169, 33.5651),
    "lahore": (74.3587, 31.5204),
    "karachi": (67.0011, 24.8607),
    "peshawar": (71.5249, 34.0151),
    "quetta": (66.9750, 30.1798),
    "multan": (71.5249, 30.1575),
    "faisalabad": (73.1350, 31.4504),
    "hyderabad": (68.3578, 25.3960),
    "sialkot": (74.5229, 32.4945),
    "gujranwala": (74.1871, 32.1877),
    "sukkur": (68.8228, 27.7052),
    "bahawalpur": (71.6833, 29.3956),
    "dera ghazi khan": (70.6400, 30.0489),
    
    # Northern Areas - Tourist Destinations
    "murree": (73.3903, 33.9070),
    "naran": (73.6500, 34.9000),
    "kaghan": (73.5167, 34.7667),
    "shogran": (73.4833, 34.6333),
    "babusar": (74.0167, 35.1500),
    "swat": (72.3609, 34.7717),  # Using Mingora coordinates (main city of Swat)
    "mingora": (72.3609, 34.7717),
    "kalam": (72.5833, 35.5000),
    "malam jabba": (72.5667, 35.0167),
    "bahrain": (72.5500, 35.2167),
    "gilgit": (74.4584, 35.9208),
    "hunza": (74.6597, 36.3167),
    "karimabad": (74.6597, 36.3167),
    "passu": (74.8833, 36.4833),
    "attabad lake": (74.8500, 36.3167),
    "skardu": (75.5550, 35.2971),
    "shigar": (75.7167, 35.4167),
    "deosai": (75.4000, 35.0000),
    "chitral": (71.7864, 35.8508),
    "kalash": (71.6667, 35.6833),
    "abbottabad": (73.2215, 34.1688),
    "nathia gali": (73.3833, 34.0667),
    "ayubia": (73.3833, 34.0500),
    "khunjerab": (75.4209, 36.8500),
    
    # Azad Kashmir
    "muzaffarabad": (73.4711, 34.3700),
    "neelum": (73.9000, 34.5833),
    "rawalakot": (73.7603, 33.8575),
    "bagh": (73.7772, 33.9803),
    
    # South Punjab
    "dera ismail khan": (70.9019, 31.8326),
    "rahim yar khan": (70.3297, 28.4202),
}

# Fallback distances if API fails (in km)
# Comprehensive routes from all major cities to tourist destinations
FALLBACK_DISTANCES = {
    # ============================================
    # FROM ISLAMABAD (Capital)
    # ============================================
    ("islamabad", "rawalpindi"): 15,
    ("islamabad", "lahore"): 375,
    ("islamabad", "karachi"): 1410,
    ("islamabad", "peshawar"): 165,
    ("islamabad", "quetta"): 800,
    ("islamabad", "multan"): 550,
    ("islamabad", "faisalabad"): 390,
    ("islamabad", "sialkot"): 260,
    ("islamabad", "gujranwala"): 300,
    # Islamabad to Northern Tourist Destinations
    ("islamabad", "murree"): 65,
    ("islamabad", "nathia gali"): 85,
    ("islamabad", "ayubia"): 80,
    ("islamabad", "abbottabad"): 120,
    ("islamabad", "naran"): 275,
    ("islamabad", "kaghan"): 250,
    ("islamabad", "shogran"): 230,
    ("islamabad", "swat"): 270,
    ("islamabad", "kalam"): 310,
    ("islamabad", "malam jabba"): 300,
    ("islamabad", "mingora"): 270,
    ("islamabad", "gilgit"): 600,
    ("islamabad", "hunza"): 670,
    ("islamabad", "skardu"): 620,
    ("islamabad", "chitral"): 470,
    ("islamabad", "muzaffarabad"): 140,
    ("islamabad", "neelum"): 200,
    ("islamabad", "rawalakot"): 180,
    
    # ============================================
    # FROM RAWALPINDI
    # ============================================
    ("rawalpindi", "islamabad"): 15,
    ("rawalpindi", "lahore"): 380,
    ("rawalpindi", "peshawar"): 170,
    ("rawalpindi", "murree"): 60,
    ("rawalpindi", "nathia gali"): 80,
    ("rawalpindi", "abbottabad"): 115,
    ("rawalpindi", "naran"): 270,
    ("rawalpindi", "kaghan"): 245,
    ("rawalpindi", "swat"): 275,
    ("rawalpindi", "gilgit"): 605,
    ("rawalpindi", "hunza"): 675,
    ("rawalpindi", "skardu"): 625,
    ("rawalpindi", "muzaffarabad"): 135,
    
    # ============================================
    # FROM LAHORE (Punjab Capital)
    # ============================================
    ("lahore", "islamabad"): 375,
    ("lahore", "rawalpindi"): 380,
    ("lahore", "karachi"): 1220,
    ("lahore", "peshawar"): 540,
    ("lahore", "quetta"): 870,
    ("lahore", "multan"): 340,
    ("lahore", "faisalabad"): 185,
    ("lahore", "sialkot"): 130,
    ("lahore", "gujranwala"): 70,
    # Lahore to Tourist Destinations
    ("lahore", "murree"): 440,
    ("lahore", "nathia gali"): 460,
    ("lahore", "abbottabad"): 495,
    ("lahore", "naran"): 550,
    ("lahore", "kaghan"): 525,
    ("lahore", "swat"): 620,
    ("lahore", "kalam"): 680,
    ("lahore", "gilgit"): 975,
    ("lahore", "hunza"): 1045,
    ("lahore", "skardu"): 995,
    ("lahore", "muzaffarabad"): 515,
    ("lahore", "chitral"): 845,
    
    # ============================================
    # FROM PESHAWAR (KPK Capital)
    # ============================================
    ("peshawar", "islamabad"): 165,
    ("peshawar", "rawalpindi"): 170,
    ("peshawar", "lahore"): 540,
    ("peshawar", "karachi"): 1575,
    ("peshawar", "quetta"): 750,
    # Peshawar to Tourist Destinations
    ("peshawar", "swat"): 175,
    ("peshawar", "mingora"): 175,
    ("peshawar", "kalam"): 250,
    ("peshawar", "malam jabba"): 200,
    ("peshawar", "bahrain"): 220,
    ("peshawar", "chitral"): 340,
    ("peshawar", "kalash"): 380,
    ("peshawar", "abbottabad"): 150,
    ("peshawar", "naran"): 310,
    ("peshawar", "kaghan"): 285,
    ("peshawar", "gilgit"): 560,
    ("peshawar", "hunza"): 630,
    ("peshawar", "murree"): 230,
    
    # ============================================
    # FROM KARACHI (Sindh Capital)
    # ============================================
    ("karachi", "islamabad"): 1410,
    ("karachi", "lahore"): 1220,
    ("karachi", "peshawar"): 1575,
    ("karachi", "quetta"): 690,
    ("karachi", "multan"): 900,
    ("karachi", "hyderabad"): 165,
    ("karachi", "sukkur"): 470,
    ("karachi", "faisalabad"): 1100,
    # Karachi to Tourist Destinations (long distance)
    ("karachi", "murree"): 1475,
    ("karachi", "swat"): 1680,
    ("karachi", "hunza"): 2080,
    ("karachi", "skardu"): 2030,
    ("karachi", "gilgit"): 2010,
    
    # ============================================
    # FROM QUETTA (Balochistan Capital)
    # ============================================
    ("quetta", "islamabad"): 800,
    ("quetta", "lahore"): 870,
    ("quetta", "karachi"): 690,
    ("quetta", "peshawar"): 750,
    ("quetta", "multan"): 530,
    # Quetta to Tourist Destinations
    ("quetta", "ziarat"): 130,
    ("quetta", "murree"): 865,
    ("quetta", "swat"): 920,
    ("quetta", "gilgit"): 1400,
    ("quetta", "hunza"): 1470,
    
    # ============================================
    # FROM MULTAN (South Punjab)
    # ============================================
    ("multan", "islamabad"): 550,
    ("multan", "lahore"): 340,
    ("multan", "karachi"): 900,
    ("multan", "peshawar"): 715,
    ("multan", "quetta"): 530,
    ("multan", "faisalabad"): 210,
    ("multan", "bahawalpur"): 100,
    # Multan to Tourist Destinations
    ("multan", "murree"): 615,
    ("multan", "swat"): 820,
    ("multan", "naran"): 700,
    ("multan", "gilgit"): 1150,
    ("multan", "hunza"): 1220,
    
    # ============================================
    # FROM FAISALABAD
    # ============================================
    ("faisalabad", "islamabad"): 390,
    ("faisalabad", "lahore"): 185,
    ("faisalabad", "karachi"): 1100,
    ("faisalabad", "multan"): 210,
    ("faisalabad", "peshawar"): 555,
    # Faisalabad to Tourist Destinations
    ("faisalabad", "murree"): 455,
    ("faisalabad", "naran"): 530,
    ("faisalabad", "swat"): 635,
    ("faisalabad", "gilgit"): 990,
    ("faisalabad", "hunza"): 1060,
    
    # ============================================
    # FROM SIALKOT
    # ============================================
    ("sialkot", "islamabad"): 260,
    ("sialkot", "lahore"): 130,
    ("sialkot", "murree"): 325,
    ("sialkot", "naran"): 415,
    ("sialkot", "swat"): 520,
    ("sialkot", "hunza"): 930,
    ("sialkot", "gilgit"): 860,
    ("sialkot", "skardu"): 880,
    ("sialkot", "chitral"): 730,
    ("sialkot", "kalam"): 580,
    ("sialkot", "muzaffarabad"): 400,
    
    # ============================================
    # ADDITIONAL MISSING ROUTES
    # ============================================
    # From Rawalpindi
    ("rawalpindi", "chitral"): 475,
    ("rawalpindi", "kalam"): 315,
    
    # From Peshawar
    ("peshawar", "skardu"): 785,
    ("peshawar", "muzaffarabad"): 305,
    
    # From Karachi (long distance to northern areas)
    ("karachi", "naran"): 1560,
    ("karachi", "chitral"): 1885,
    ("karachi", "kalam"): 1720,
    ("karachi", "muzaffarabad"): 1550,
    
    # From Quetta (long distance to northern areas)
    ("quetta", "naran"): 1075,
    ("quetta", "skardu"): 1420,
    ("quetta", "chitral"): 1090,
    ("quetta", "kalam"): 970,
    ("quetta", "muzaffarabad"): 940,
    
    # From Multan
    ("multan", "skardu"): 1170,
    ("multan", "chitral"): 1020,
    ("multan", "kalam"): 870,
    ("multan", "muzaffarabad"): 690,
    
    # From Faisalabad
    ("faisalabad", "skardu"): 1010,
    ("faisalabad", "chitral"): 860,
    ("faisalabad", "kalam"): 710,
    ("faisalabad", "muzaffarabad"): 530,
    
    # ============================================
    # NORTHERN AREAS - Internal Connections
    # ============================================
    # Gilgit-Baltistan
    ("gilgit", "hunza"): 100,
    ("gilgit", "skardu"): 170,
    ("gilgit", "chitral"): 340,
    ("gilgit", "khunjerab"): 220,
    ("hunza", "khunjerab"): 120,
    ("hunza", "passu"): 45,
    ("hunza", "attabad lake"): 25,
    ("hunza", "karimabad"): 5,
    ("skardu", "deosai"): 80,
    ("skardu", "shigar"): 35,
    
    # Kaghan Valley
    ("naran", "kaghan"): 25,
    ("naran", "babusar"): 70,
    ("naran", "shogran"): 35,
    ("kaghan", "shogran"): 20,
    ("abbottabad", "naran"): 160,
    ("abbottabad", "kaghan"): 140,
    ("abbottabad", "shogran"): 120,
    
    # Swat Valley
    ("swat", "kalam"): 95,
    ("swat", "malam jabba"): 40,
    ("swat", "bahrain"): 50,
    ("swat", "mingora"): 5,
    ("mingora", "kalam"): 100,
    ("mingora", "malam jabba"): 45,
    ("kalam", "mahodand"): 35,
    
    # Murree & Galiyat
    ("murree", "nathia gali"): 25,
    ("murree", "ayubia"): 30,
    ("abbottabad", "murree"): 55,
    ("abbottabad", "nathia gali"): 35,
    
    # Chitral & Kalash
    ("chitral", "kalash"): 40,
    ("chitral", "bumburet"): 40,
    
    # ============================================
    # AZAD KASHMIR
    # ============================================
    ("muzaffarabad", "neelum"): 90,
    ("muzaffarabad", "rawalakot"): 120,
    ("muzaffarabad", "bagh"): 50,
    ("rawalakot", "bagh"): 70,
    ("neelum", "kel"): 50,
    ("neelum", "sharda"): 80,
}


class RouteService:
    """Service for route calculations and transport options"""

    def __init__(self):
        self.ors_api_key = os.getenv("OPENROUTE_API_KEY")
        self.ors_base_url = "https://api.openrouteservice.org/v2"
        if self.ors_api_key:
            route_logger.debug("Route service initialized with OpenRouteService API key")
        else:
            route_logger.info("Route service initialized (using fallback distances - no ORS API key)")

    def _get_db_route(self, origin: str, destination: str) -> Optional[Route]:
        """Get route from database."""
        db = SessionLocal()
        try:
            route = db.query(Route).filter(
                Route.origin.ilike(origin),
                Route.destination.ilike(destination)
            ).first()
            return route
        finally:
            db.close()

    def _get_db_transport_options(self, origin: str, destination: str) -> List[Dict]:
        """Get transport options from database."""
        db = SessionLocal()
        try:
            options = db.query(TransportOption).filter(
                TransportOption.origin.ilike(origin),
                TransportOption.destination.ilike(destination)
            ).all()
            return [
                {
                    "mode": o.mode,
                    "estimated_fare_pkr": o.typical_fare_pkr,
                    "fare_range_pkr": o.fare_range_pkr or {"min": o.typical_fare_pkr * 0.8, "max": o.typical_fare_pkr * 1.2},
                    "estimated_time_hours": o.estimated_time_hours,
                    "availability": o.availability,
                    "safety_notes": o.safety_notes,
                    "risk_level": "recommended" if o.night_travel_safe else "caution",
                    "overcrowding_risk": o.overcrowding_risk,
                }
                for o in options
            ]
        finally:
            db.close()

    def _save_route_to_db(self, origin: str, destination: str, distance_km: float, time_hours: float):
        """Cache route in database."""
        db = SessionLocal()
        try:
            existing = db.query(Route).filter(
                Route.origin.ilike(origin),
                Route.destination.ilike(destination)
            ).first()
            if not existing:
                route = Route(
                    origin=origin.title(),
                    destination=destination.title(),
                    route_name=f"{origin.title()} to {destination.title()}",
                    distance_km=distance_km,
                    estimated_time_hours=time_hours,
                    safety_score=75,  # Default score
                    risk_level="caution",
                )
                db.add(route)
                db.commit()
        except Exception:
            db.rollback()
        finally:
            db.close()

    # Remote areas where OpenRouteService has NO road data (Karakoram Highway region)
    # Only skip API for areas that consistently fail - let ORS handle everything else
    ORS_UNSUPPORTED_AREAS = {
        # Gilgit-Baltistan (beyond Chilas - KKH has no OSM road data)
        "gilgit", "hunza", "karimabad", "passu", "attabad lake", "khunjerab",
        "skardu", "shigar", "deosai", "fairy meadows", "naltar",
        # Remote valleys with no road data
        "kalash", "bumburet", "rumbur",  # Kalash valleys
        "neelum", "kel", "arang kel", "taobat", "sharda",  # Upper Neelum
        "mahodand", "ushu forest",  # Remote Swat
        "lulusar", "saiful muluk", "lake saiful muluk",  # Kaghan lakes
    }
    # Note: These cities WORK with ORS API and should NOT be in unsupported list:
    # murree, naran, kalam, chitral, muzaffarabad, mingora, abbottabad, swat area

    def _fetch_ors_route(self, origin: str, destination: str) -> Optional[Dict]:
        """Fetch route from OpenRouteService API."""
        if not self.ors_api_key:
            return None

        origin_lower = origin.lower()
        dest_lower = destination.lower()
        
        # Skip API call for remote mountain areas with no ORS road data
        if origin_lower in self.ORS_UNSUPPORTED_AREAS or dest_lower in self.ORS_UNSUPPORTED_AREAS:
            route_logger.debug(f"Skipping ORS API for remote area: {origin} -> {destination}")
            return None

        origin_coords = CITY_COORDINATES.get(origin_lower)
        dest_coords = CITY_COORDINATES.get(dest_lower)
        if not origin_coords or not dest_coords:
            route_logger.debug(f"Coordinates not found for: {origin} or {destination}")
            return None

        try:
            route_logger.debug(f"Fetching ORS route: {origin} -> {destination}")
            url = f"{self.ors_base_url}/directions/driving-car"
            params = {
                "api_key": self.ors_api_key,
                "start": f"{origin_coords[0]},{origin_coords[1]}",
                "end": f"{dest_coords[0]},{dest_coords[1]}",
            }
            full_url = f"{url}?{urllib.parse.urlencode(params)}"
            
            with urllib.request.urlopen(full_url, timeout=10) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                
            if "features" in data and len(data["features"]) > 0:
                props = data["features"][0]["properties"]["summary"]
                distance_km = props["distance"] / 1000
                duration_hours = props["duration"] / 3600
                route_logger.debug(f"ORS route found: {distance_km:.1f} km, {duration_hours:.1f} hours")
                return {"distance_km": round(distance_km, 1), "time_hours": round(duration_hours, 1)}
        except urllib.error.HTTPError as e:
            route_logger.warning(f"OpenRouteService HTTP error: {e.code}")
        except urllib.error.URLError as e:
            route_logger.warning(f"OpenRouteService connection error: {e.reason}")
        except Exception as e:
            route_logger.error(f"OpenRouteService unexpected error: {e}")
        return None

    def get_distance(self, origin: str, destination: str) -> Optional[float]:
        """Get distance between two cities.
        
        Priority order:
        1. OpenRouteService API (real-time) - always try first
        2. Database cache (if API fails)
        3. Fallback distances (saved to DB for future use)
        """
        origin_lower = origin.lower().strip()
        dest_lower = destination.lower().strip()

        # 1. FIRST: Try OpenRouteService API (real-time data)
        ors_result = self._fetch_ors_route(origin, destination)
        if ors_result:
            # Cache in DB for future requests
            self._save_route_to_db(origin, destination, ors_result["distance_km"], ors_result["time_hours"])
            route_logger.info(f"🌐 ORS API: {origin} → {destination}: {ors_result['distance_km']} km (real-time)")
            return ors_result["distance_km"]

        # 2. SECOND: Check database cache (if API failed)
        db_route = self._get_db_route(origin, destination)
        if db_route and db_route.distance_km:
            route_logger.info(f"📦 DB CACHE: {origin} → {destination}: {db_route.distance_km} km")
            return db_route.distance_km

        # 3. THIRD: Use fallback and save to database for future use
        fallback_distance = None
        if (origin_lower, dest_lower) in FALLBACK_DISTANCES:
            fallback_distance = FALLBACK_DISTANCES[(origin_lower, dest_lower)]
        elif (dest_lower, origin_lower) in FALLBACK_DISTANCES:
            fallback_distance = FALLBACK_DISTANCES[(dest_lower, origin_lower)]
        
        if fallback_distance:
            # Save fallback to database so it becomes cached for next time
            estimated_time = self.estimate_travel_time(fallback_distance)
            self._save_route_to_db(origin, destination, fallback_distance, estimated_time)
            route_logger.info(f"📋 FALLBACK → DB: {origin} → {destination}: {fallback_distance} km (saved to database)")
            return fallback_distance

        route_logger.warning(f"❌ NO DATA: {origin} → {destination}")
        return None

    def estimate_travel_time(self, distance_km: float, transport_mode: str = "bus") -> float:
        """Estimate travel time in hours."""
        speeds = {
            "bus": 60,
            "daewoo": 80,
            "van": 65,
            "train": 50,
            "rickshaw": 30,
            "careem": 70,
            "indriver": 70,
            "ride_hailing": 70,
            "flight": 600,
        }
        speed = speeds.get(transport_mode, 60)
        return round(distance_km / speed, 1)

    def get_transport_options(
        self,
        origin: str,
        destination: str,
        distance_km: Optional[float] = None
    ) -> List[Dict]:
        """Get available transport options with fare estimates."""
        # 1. Check database first
        db_options = self._get_db_transport_options(origin, destination)
        if db_options:
            return db_options

        # 2. Fallback to calculated options
        if distance_km is None:
            distance_km = self.get_distance(origin, destination)
            if distance_km is None:
                return []

        return self._generate_fallback_options(distance_km)

    def _generate_fallback_options(self, distance_km: float) -> List[Dict]:
        """Generate fallback transport options based on distance."""
        options = []

        if distance_km > 20:
            options.append({
                "mode": "bus",
                "estimated_fare_pkr": 50 + distance_km * 2.5,
                "fare_range_pkr": {"min": 40 + distance_km * 2, "max": 70 + distance_km * 3},
                "estimated_time_hours": self.estimate_travel_time(distance_km, "bus"),
                "availability": "always",
                "safety_notes": "Standard bus service",
                "risk_level": "caution" if distance_km > 500 else "recommended",
            })

        if distance_km > 100:
            options.append({
                "mode": "train",
                "estimated_fare_pkr": 200 + distance_km * 1.5,
                "fare_range_pkr": {"min": 150 + distance_km, "max": 400 + distance_km * 2},
                "estimated_time_hours": self.estimate_travel_time(distance_km, "train"),
                "availability": "limited",
                "safety_notes": "Book in advance",
                "risk_level": "recommended",
            })

        if distance_km < 200:
            options.append({
                "mode": "ride_hailing",
                "estimated_fare_pkr": 150 + distance_km * 25,
                "fare_range_pkr": {"min": 130 + distance_km * 20, "max": 200 + distance_km * 35},
                "estimated_time_hours": self.estimate_travel_time(distance_km, "ride_hailing"),
                "availability": "always",
                "safety_notes": "Trackable, safest option",
                "risk_level": "recommended",
            })

        return options

    def get_route_info(self, origin: str, destination: str) -> Dict[str, Any]:
        """Get comprehensive route information."""
        distance = self.get_distance(origin, destination)
        transport_options = self.get_transport_options(origin, destination, distance)

        # Get safety info from DB if available
        db_route = self._get_db_route(origin, destination)
        safety_score = db_route.safety_score if db_route else 75
        risk_level = db_route.risk_level if db_route else "caution"

        return {
            "origin": origin,
            "destination": destination,
            "distance_km": distance,
            "estimated_time_hours": self.estimate_travel_time(distance) if distance else None,
            "safety_score": safety_score,
            "risk_level": risk_level,
            "transport_options": transport_options,
            "region": self._get_region(origin, destination),
        }

    def _get_region(self, origin: str, destination: str) -> str:
        """Determine region for route."""
        northern = [
            "gilgit", "hunza", "skardu", "chitral", "swat", "murree", "kalam", "khunjerab",
            "naran", "kaghan", "shogran", "babusar", "mingora", "malam jabba", "bahrain",
            "karimabad", "passu", "attabad", "shigar", "deosai", "kalash", "nathia gali", "ayubia"
        ]
        kashmir = ["muzaffarabad", "neelum", "rawalakot", "bagh"]
        origin_lower = origin.lower()
        dest_lower = destination.lower()

        if any(city in origin_lower for city in northern) or any(city in dest_lower for city in northern):
            return "northern_areas"
        elif any(city in origin_lower for city in kashmir) or any(city in dest_lower for city in kashmir):
            return "azad_kashmir"
        elif "karachi" in origin_lower or "karachi" in dest_lower:
            return "sindh"
        elif "lahore" in origin_lower or "lahore" in dest_lower:
            return "punjab"
        elif "peshawar" in origin_lower or "peshawar" in dest_lower:
            return "kpk"
        else:
            return "general"
