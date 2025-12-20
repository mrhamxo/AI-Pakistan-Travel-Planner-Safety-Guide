"""
Seed script to populate database with Pakistan travel data
Run: python -m app.seed_data
"""
import sys
from pathlib import Path

# Add backend to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.database import SessionLocal, init_db
from app.models.travel import Route, SafetyAlert
from app.models.transport import TransportOption, TransportRoute

# Pakistan city routes with realistic distances
ROUTES = [
    # Major intercity routes
    {"origin": "Islamabad", "destination": "Lahore", "distance_km": 375, "time_hours": 4.5, "safety_score": 85, "risk_level": "recommended"},
    {"origin": "Islamabad", "destination": "Karachi", "distance_km": 1410, "time_hours": 16, "safety_score": 70, "risk_level": "caution"},
    {"origin": "Islamabad", "destination": "Peshawar", "distance_km": 165, "time_hours": 2, "safety_score": 75, "risk_level": "recommended"},
    {"origin": "Islamabad", "destination": "Murree", "distance_km": 65, "time_hours": 1.5, "safety_score": 80, "risk_level": "recommended"},
    {"origin": "Islamabad", "destination": "Swat", "distance_km": 270, "time_hours": 5, "safety_score": 70, "risk_level": "caution"},
    {"origin": "Islamabad", "destination": "Gilgit", "distance_km": 600, "time_hours": 14, "safety_score": 60, "risk_level": "caution"},
    {"origin": "Islamabad", "destination": "Hunza", "distance_km": 670, "time_hours": 15, "safety_score": 65, "risk_level": "caution"},
    {"origin": "Islamabad", "destination": "Skardu", "distance_km": 620, "time_hours": 18, "safety_score": 55, "risk_level": "caution"},
    {"origin": "Islamabad", "destination": "Multan", "distance_km": 540, "time_hours": 6.5, "safety_score": 80, "risk_level": "recommended"},
    {"origin": "Islamabad", "destination": "Faisalabad", "distance_km": 390, "time_hours": 4.5, "safety_score": 82, "risk_level": "recommended"},
    {"origin": "Islamabad", "destination": "Rawalpindi", "distance_km": 15, "time_hours": 0.5, "safety_score": 90, "risk_level": "recommended"},
    {"origin": "Islamabad", "destination": "Quetta", "distance_km": 820, "time_hours": 12, "safety_score": 50, "risk_level": "caution"},
    {"origin": "Islamabad", "destination": "Chitral", "distance_km": 450, "time_hours": 11, "safety_score": 55, "risk_level": "caution"},
    
    # Lahore routes
    {"origin": "Lahore", "destination": "Karachi", "distance_km": 1220, "time_hours": 14, "safety_score": 75, "risk_level": "recommended"},
    {"origin": "Lahore", "destination": "Multan", "distance_km": 340, "time_hours": 4, "safety_score": 85, "risk_level": "recommended"},
    {"origin": "Lahore", "destination": "Faisalabad", "distance_km": 185, "time_hours": 2.5, "safety_score": 88, "risk_level": "recommended"},
    {"origin": "Lahore", "destination": "Peshawar", "distance_km": 490, "time_hours": 6, "safety_score": 75, "risk_level": "recommended"},
    {"origin": "Lahore", "destination": "Murree", "distance_km": 330, "time_hours": 5, "safety_score": 80, "risk_level": "recommended"},
    {"origin": "Lahore", "destination": "Sialkot", "distance_km": 130, "time_hours": 2, "safety_score": 85, "risk_level": "recommended"},
    
    # Karachi routes
    {"origin": "Karachi", "destination": "Hyderabad", "distance_km": 165, "time_hours": 2.5, "safety_score": 80, "risk_level": "recommended"},
    {"origin": "Karachi", "destination": "Quetta", "distance_km": 690, "time_hours": 10, "safety_score": 55, "risk_level": "caution"},
    {"origin": "Karachi", "destination": "Multan", "distance_km": 880, "time_hours": 11, "safety_score": 70, "risk_level": "caution"},
    {"origin": "Karachi", "destination": "Sukkur", "distance_km": 470, "time_hours": 6, "safety_score": 75, "risk_level": "recommended"},
    
    # Peshawar routes
    {"origin": "Peshawar", "destination": "Swat", "distance_km": 175, "time_hours": 3.5, "safety_score": 65, "risk_level": "caution"},
    {"origin": "Peshawar", "destination": "Chitral", "distance_km": 350, "time_hours": 10, "safety_score": 50, "risk_level": "caution"},
    {"origin": "Peshawar", "destination": "Abbottabad", "distance_km": 115, "time_hours": 2.5, "safety_score": 80, "risk_level": "recommended"},
    
    # Northern areas
    {"origin": "Gilgit", "destination": "Hunza", "distance_km": 100, "time_hours": 2, "safety_score": 75, "risk_level": "recommended"},
    {"origin": "Gilgit", "destination": "Skardu", "distance_km": 170, "time_hours": 5, "safety_score": 60, "risk_level": "caution"},
    {"origin": "Hunza", "destination": "Khunjerab", "distance_km": 120, "time_hours": 3, "safety_score": 50, "risk_level": "caution"},
    {"origin": "Swat", "destination": "Kalam", "distance_km": 80, "time_hours": 2.5, "safety_score": 70, "risk_level": "caution"},
    
    # Southern Punjab
    {"origin": "Multan", "destination": "Bahawalpur", "distance_km": 100, "time_hours": 1.5, "safety_score": 85, "risk_level": "recommended"},
    {"origin": "Multan", "destination": "Dera Ghazi Khan", "distance_km": 200, "time_hours": 3, "safety_score": 70, "risk_level": "caution"},
    
    # Add reverse routes for key city pairs
    {"origin": "Lahore", "destination": "Islamabad", "distance_km": 375, "time_hours": 4.5, "safety_score": 85, "risk_level": "recommended"},
    {"origin": "Karachi", "destination": "Lahore", "distance_km": 1220, "time_hours": 14, "safety_score": 75, "risk_level": "recommended"},
    {"origin": "Peshawar", "destination": "Islamabad", "distance_km": 165, "time_hours": 2, "safety_score": 75, "risk_level": "recommended"},
    {"origin": "Murree", "destination": "Islamabad", "distance_km": 65, "time_hours": 1.5, "safety_score": 80, "risk_level": "recommended"},
    {"origin": "Rawalpindi", "destination": "Islamabad", "distance_km": 15, "time_hours": 0.5, "safety_score": 90, "risk_level": "recommended"},
    {"origin": "Hunza", "destination": "Gilgit", "distance_km": 100, "time_hours": 2, "safety_score": 75, "risk_level": "recommended"},
]

# Transport options with realistic Pakistan fares
TRANSPORT_OPTIONS = [
    # Bus services
    {"mode": "bus", "origin": "Islamabad", "destination": "Lahore", "fare": 1500, "fare_range": [1200, 2500], "time_hours": 5, "availability": "always", "safety_notes": "AC buses recommended, Daewoo/Faisal Movers safest", "overcrowding_risk": "low", "night_safe": True},
    {"mode": "bus", "origin": "Islamabad", "destination": "Karachi", "fare": 4500, "fare_range": [3500, 6000], "time_hours": 18, "availability": "always", "safety_notes": "Take daytime bus for safety", "overcrowding_risk": "medium", "night_safe": False},
    {"mode": "bus", "origin": "Lahore", "destination": "Karachi", "fare": 4000, "fare_range": [3000, 5500], "time_hours": 16, "availability": "always", "safety_notes": "Multiple stops, prefer direct buses", "overcrowding_risk": "medium", "night_safe": False},
    {"mode": "bus", "origin": "Islamabad", "destination": "Peshawar", "fare": 800, "fare_range": [600, 1200], "time_hours": 2.5, "availability": "always", "safety_notes": "Motorway buses are safest", "overcrowding_risk": "low", "night_safe": True},
    {"mode": "bus", "origin": "Islamabad", "destination": "Multan", "fare": 2000, "fare_range": [1500, 3000], "time_hours": 7, "availability": "always", "safety_notes": "Take morning buses", "overcrowding_risk": "medium", "night_safe": False},
    {"mode": "bus", "origin": "Islamabad", "destination": "Swat", "fare": 1200, "fare_range": [900, 1800], "time_hours": 6, "availability": "daytime_only", "safety_notes": "Only travel in daylight, mountain roads", "overcrowding_risk": "high", "night_safe": False},
    {"mode": "bus", "origin": "Islamabad", "destination": "Gilgit", "fare": 3000, "fare_range": [2500, 4000], "time_hours": 16, "availability": "daytime_only", "safety_notes": "Dangerous mountain road, only experienced drivers", "overcrowding_risk": "medium", "night_safe": False},
    
    # Ride hailing
    {"mode": "careem", "origin": "Islamabad", "destination": "Lahore", "fare": 8000, "fare_range": [7000, 12000], "time_hours": 4.5, "availability": "always", "safety_notes": "Trackable, safest option", "overcrowding_risk": "low", "night_safe": True},
    {"mode": "careem", "origin": "Islamabad", "destination": "Murree", "fare": 3500, "fare_range": [3000, 5000], "time_hours": 1.5, "availability": "always", "safety_notes": "Trackable ride", "overcrowding_risk": "low", "night_safe": True},
    {"mode": "indriver", "origin": "Islamabad", "destination": "Lahore", "fare": 6500, "fare_range": [5500, 9000], "time_hours": 4.5, "availability": "always", "safety_notes": "Negotiate fare, share trip details", "overcrowding_risk": "low", "night_safe": True},
    
    # Daewoo Express (premium bus)
    {"mode": "daewoo", "origin": "Islamabad", "destination": "Lahore", "fare": 2200, "fare_range": [2000, 2800], "time_hours": 4.5, "availability": "always", "safety_notes": "Premium service, fully AC, safest bus option", "overcrowding_risk": "low", "night_safe": True},
    {"mode": "daewoo", "origin": "Islamabad", "destination": "Karachi", "fare": 5500, "fare_range": [5000, 6500], "time_hours": 17, "availability": "always", "safety_notes": "Sleeper option available", "overcrowding_risk": "low", "night_safe": True},
    {"mode": "daewoo", "origin": "Lahore", "destination": "Multan", "fare": 1500, "fare_range": [1200, 1800], "time_hours": 4, "availability": "always", "safety_notes": "Best option for this route", "overcrowding_risk": "low", "night_safe": True},
    
    # Train
    {"mode": "train", "origin": "Islamabad", "destination": "Lahore", "fare": 800, "fare_range": [400, 2500], "time_hours": 5, "availability": "limited", "safety_notes": "Book business class for comfort", "overcrowding_risk": "high", "night_safe": False},
    {"mode": "train", "origin": "Islamabad", "destination": "Karachi", "fare": 2500, "fare_range": [1200, 5000], "time_hours": 22, "availability": "limited", "safety_notes": "Long journey, sleeper recommended", "overcrowding_risk": "high", "night_safe": False},
    {"mode": "train", "origin": "Lahore", "destination": "Karachi", "fare": 2200, "fare_range": [1000, 4500], "time_hours": 18, "availability": "limited", "safety_notes": "Multiple classes available", "overcrowding_risk": "high", "night_safe": False},
    
    # Flights
    {"mode": "flight", "origin": "Islamabad", "destination": "Karachi", "fare": 12000, "fare_range": [8000, 25000], "time_hours": 1.5, "availability": "always", "safety_notes": "PIA/Airblue/Serene, book early for deals", "overcrowding_risk": "low", "night_safe": True},
    {"mode": "flight", "origin": "Islamabad", "destination": "Lahore", "fare": 8000, "fare_range": [5000, 15000], "time_hours": 0.75, "availability": "always", "safety_notes": "Short flight, often delayed", "overcrowding_risk": "low", "night_safe": True},
    {"mode": "flight", "origin": "Islamabad", "destination": "Gilgit", "fare": 10000, "fare_range": [7000, 18000], "time_hours": 1, "availability": "limited", "safety_notes": "Weather dependent, frequent cancellations", "overcrowding_risk": "low", "night_safe": True},
    {"mode": "flight", "origin": "Islamabad", "destination": "Skardu", "fare": 12000, "fare_range": [8000, 20000], "time_hours": 1, "availability": "limited", "safety_notes": "Very weather dependent", "overcrowding_risk": "low", "night_safe": True},
    
    # Local transport
    {"mode": "wagon", "origin": "Islamabad", "destination": "Rawalpindi", "fare": 50, "fare_range": [40, 80], "time_hours": 0.5, "availability": "always", "safety_notes": "Crowded, keep valuables safe", "overcrowding_risk": "high", "night_safe": False},
    {"mode": "rickshaw", "origin": "Islamabad", "destination": "Rawalpindi", "fare": 300, "fare_range": [200, 500], "time_hours": 0.75, "availability": "always", "safety_notes": "Negotiate fare before boarding", "overcrowding_risk": "low", "night_safe": False},
]

# Sample safety alerts
SAFETY_ALERTS = [
    {"alert_type": "fog", "region": "Lahore", "severity": "medium", "description": "Dense fog expected on M2 motorway during winter mornings", "is_active": True},
    {"alert_type": "landslide", "region": "Karakoram Highway", "severity": "high", "description": "Landslide risk on KKH near Chilas, proceed with caution", "is_active": True},
    {"alert_type": "road_closure", "region": "Khunjerab Pass", "severity": "critical", "description": "Pass closed during winter months (Nov-Apr)", "is_active": True},
    {"alert_type": "flood", "region": "Swat Valley", "severity": "medium", "description": "Monsoon flooding possible July-September", "is_active": True},
    {"alert_type": "protest", "region": "Islamabad", "severity": "low", "description": "Occasional road blocks near Red Zone", "is_active": True},
]


def seed_database():
    """Seed the database with initial data."""
    init_db()
    db = SessionLocal()
    
    try:
        # Clear existing data
        db.query(TransportOption).delete()
        db.query(Route).delete()
        db.query(SafetyAlert).delete()
        db.commit()
        
        # Seed routes
        for r in ROUTES:
            route = Route(
                origin=r["origin"],
                destination=r["destination"],
                route_name=f"{r['origin']} to {r['destination']}",
                distance_km=r["distance_km"],
                estimated_time_hours=r["time_hours"],
                safety_score=r["safety_score"],
                risk_level=r["risk_level"],
            )
            db.add(route)
        
        # Seed transport options
        for t in TRANSPORT_OPTIONS:
            option = TransportOption(
                mode=t["mode"],
                origin=t["origin"],
                destination=t["destination"],
                route_name=f"{t['origin']} to {t['destination']}",
                typical_fare_pkr=t["fare"],
                fare_range_pkr={"min": t["fare_range"][0], "max": t["fare_range"][1]},
                estimated_time_hours=t["time_hours"],
                availability=t["availability"],
                safety_notes=t["safety_notes"],
                overcrowding_risk=t["overcrowding_risk"],
                night_travel_safe=t["night_safe"],
            )
            db.add(option)
        
        # Seed safety alerts
        for a in SAFETY_ALERTS:
            alert = SafetyAlert(
                alert_type=a["alert_type"],
                region=a["region"],
                severity=a["severity"],
                description=a["description"],
                is_active=a["is_active"],
            )
            db.add(alert)
        
        db.commit()
        print(f"[OK] Seeded {len(ROUTES)} routes")
        print(f"[OK] Seeded {len(TRANSPORT_OPTIONS)} transport options")
        print(f"[OK] Seeded {len(SAFETY_ALERTS)} safety alerts")
        print("Database seeding complete!")
        
    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
