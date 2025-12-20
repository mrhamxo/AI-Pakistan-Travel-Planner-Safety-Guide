"""
AI Orchestrator using LangChain and Groq LLM

This module orchestrates all AI-powered features:
- Travel query processing
- Trip itinerary generation
- Natural language parsing

It integrates with:
- Groq LLM for AI responses
- Route service for distance/transport data
- Weather service for conditions and alerts
- Safety service for risk assessment
"""

import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from langchain_groq import ChatGroq

from app.ai.prompts import get_travel_planner_prompt, get_trip_planner_prompt, QUICK_TRIP_PARSE_PROMPT
from app.logging_config import Loggers
from app.services.route_service import RouteService
from app.services.safety_service import SafetyService
from app.services.weather_service import WeatherService

# Load environment variables
_dotenv_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(dotenv_path=_dotenv_path)

# Logger for AI operations
ai_logger = Loggers.ai()

# Initialize services
route_service = RouteService()
weather_service = WeatherService()
safety_service = SafetyService()


class TravelAIOrchestrator:
    """
    Main AI orchestrator for travel planning.
    
    This class coordinates all AI-powered features:
    - Processing natural language travel queries
    - Generating complete trip itineraries
    - Parsing user requests
    
    It uses Groq's LLM API for AI inference.
    """

    def __init__(self):
        """
        Initialize the AI orchestrator.
        
        Raises:
            ValueError: If GROQ_API_KEY is not set
        """
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            ai_logger.error("GROQ_API_KEY not found in environment variables")
            raise ValueError("GROQ_API_KEY not found in environment variables")

        # Choose supported model (override via backend/.env)
        model_name = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile").strip()
        ai_logger.info(f"Initializing AI orchestrator with model: {model_name}")

        try:
            # Using **dict avoids basedpyright false-positives
            self.llm = ChatGroq(  # type: ignore[call-arg]
                **{"model_name": model_name, "groq_api_key": api_key, "temperature": 0.3}
            )
            self.prompt_template = get_travel_planner_prompt()
            ai_logger.info("AI orchestrator initialized successfully")
        except Exception as e:
            ai_logger.error(f"Failed to initialize LLM: {e}")
            raise

    async def process_travel_query(
        self,
        query: str,
        origin: Optional[str] = None,
        destination: Optional[str] = None,
        travel_date: Optional[str] = None,
        user_profile: Optional[Dict] = None,
        conversation_history: Optional[List[Dict]] = None,
    ) -> Dict[str, Any]:
        """Process a natural language travel query and return a response payload."""
        ai_logger.info(f"Processing travel query: {query[:50]}...")
        
        # Extract travel info and detect query intent
        extracted = self._extract_travel_info(query)
        origin = origin or extracted.get("origin")
        destination = destination or extracted.get("destination")
        travel_date = travel_date or extracted.get("travel_date")
        
        # Detect if user is asking for comprehensive guidance
        is_comprehensive_request = self._is_comprehensive_request(query)
        group_type = self._detect_group_type(query, user_profile)
        
        # Detect if this is a follow-up question
        is_follow_up = self._is_follow_up_question(query, conversation_history)
        
        # Only use context from previous conversation if it's truly a follow-up
        # AND the current query doesn't specify its own destination
        if is_follow_up and conversation_history and not destination:
            context = self._extract_conversation_context(conversation_history)
            # Only inherit destination if query has no destination AND is a genuine follow-up
            if not destination and context.get("destination"):
                # Double-check: if query mentions ANY city, don't inherit
                query_lower = query.lower()
                mentions_city = any(city in query_lower for city in [
                    "hunza", "skardu", "swat", "murree", "naran", "kaghan", "gilgit",
                    "chitral", "lahore", "karachi", "peshawar", "islamabad", "kalam"
                ])
                if not mentions_city:
                    destination = context["destination"]
                    ai_logger.debug(f"Follow-up: inheriting destination {destination}")
            if not origin and context.get("origin"):
                origin = context["origin"]
        else:
            # Not a follow-up - treat as fresh question
            is_follow_up = False
            ai_logger.debug("Treating as new question (not a follow-up)")
        
        ai_logger.debug(f"Comprehensive request: {is_comprehensive_request}, Group type: {group_type}")

        # If only destination is found, assume Islamabad as default origin
        if destination and not origin:
            origin = "Islamabad"
            ai_logger.info(f"Origin not specified, defaulting to Islamabad for destination: {destination}")

        # For comprehensive requests, even without explicit destination, try to help
        if is_comprehensive_request and not destination:
            # Try harder to find destination from the query
            destination = self._extract_destination_from_query(query)
            if destination and not origin:
                origin = "Islamabad"

        # If only origin is found, provide helpful suggestions but don't ask follow-up questions
        if origin and not destination:
            # For comprehensive requests, assume a popular destination
            if is_comprehensive_request:
                destination = "Murree"  # Default popular destination
                ai_logger.info("Comprehensive request without destination, defaulting to Murree")
            else:
                return {
                    "query": query,
                    "response": f"I'd love to help you plan your trip from {origin}! Here are some popular destinations:\n\n"
                               f"🏔️ **Northern Areas**: Hunza, Skardu, Gilgit, Chitral\n"
                               f"🌲 **KPK**: Swat, Naran, Kaghan\n"
                               f"⛰️ **Hill Stations**: Murree, Ayubia\n\n"
                               f"Just tell me your destination and I'll give you complete guidance!",
                    "routes": [],
                    "safety_alerts": [],
                    "cost_estimate": None,
                    "recommendations": ["Consider Hunza for breathtaking views", "Swat is great for families", "Murree is closest to Islamabad"],
                    "uncertainty_notes": None,
                }

        # If neither origin nor destination found, still try to be helpful
        if not origin and not destination:
            # Check if it's a general question about traveling
            if is_comprehensive_request or self._is_general_travel_question(query):
                # Try to extract any destination mentioned
                destination = self._extract_destination_from_query(query)
                if destination:
                    origin = "Islamabad"
                else:
                    return {
                        "query": query,
                        "response": "I'm your AI travel consultant for Pakistan! 🧭\n\n"
                                   "I can help you with:\n"
                                   "- **Complete trip planning** - just tell me where you want to go\n"
                                   "- **Route guidance** - best ways to reach any destination\n"
                                   "- **Budget planning** - realistic costs for your trip\n"
                                   "- **Safety advice** - especially for families and female travelers\n"
                                   "- **Packing lists** - what to bring for different destinations\n\n"
                                   "Popular destinations I can help with: Hunza, Swat, Skardu, Murree, Naran\n\n"
                                   "Where would you like to explore?",
                        "routes": [],
                        "safety_alerts": [],
                        "cost_estimate": None,
                        "recommendations": [],
                        "uncertainty_notes": None,
                    }
            else:
                return {
                    "query": query,
                    "response": "I'm your AI travel consultant for Pakistan! 🧭\n\n"
                               "I can help you with:\n"
                               "- **Complete trip planning** - just tell me where you want to go\n"
                               "- **Route guidance** - best ways to reach any destination\n"
                               "- **Budget planning** - realistic costs for your trip\n"
                               "- **Safety advice** - especially for families and female travelers\n\n"
                               "Try asking something like:\n"
                               "- 'Tell me everything about going to Hunza'\n"
                               "- '4 girls going to Murree - what do we need to know?'\n"
                               "- 'Family trip to Swat - complete guide'\n",
                    "routes": [],
                    "safety_alerts": [],
                    "cost_estimate": None,
                    "recommendations": [],
                    "uncertainty_notes": None,
                }

        route_info = route_service.get_route_info(origin, destination)
        distance_km = route_info.get("distance_km")
        if not distance_km:
            return {
                "query": query,
                "response": f"I don't have route information for {origin} to {destination}. Please check the city names and try again.",
                "routes": [],
                "safety_alerts": [],
                "cost_estimate": None,
                "recommendations": [],
                "uncertainty_notes": "Route database is incomplete in this MVP; add more city pairs to improve coverage.",
            }

        weather_risks_origin = weather_service.assess_weather_risks(await weather_service.get_weather(origin))
        weather_risks_dest = weather_service.assess_weather_risks(await weather_service.get_weather(destination))
        combined_weather_risks = self._combine_weather_risks(weather_risks_origin, weather_risks_dest)

        time_of_day = self._extract_time_of_day(query, travel_date)
        safety_assessment = safety_service.calculate_safety_score(
            route_info, combined_weather_risks, time_of_day, user_profile
        )

        transport_options = route_service.get_transport_options(origin, destination, distance_km)
        safety_advice = safety_service.get_safety_advice(
            f"{origin} to {destination}", safety_assessment["risk_level"], user_profile
        )

        formatted_transport = self._format_transport_options(transport_options)
        formatted_weather = self._format_weather_risks(combined_weather_risks)
        
        # Format user profile with detected group type
        formatted_profile = self._format_user_profile_enhanced(user_profile, group_type, query)
        
        # Format conversation context for follow-up questions
        conversation_context = ""
        if is_follow_up and conversation_history:
            conversation_context = self._format_conversation_history(conversation_history)

        # Build the prompt with context awareness
        prompt = self.prompt_template.format_messages(
            query=query,
            origin=origin,
            destination=destination,
            travel_date=travel_date or "Flexible",
            user_profile=formatted_profile,
            distance_km=distance_km,
            estimated_time_hours=route_service.estimate_travel_time(distance_km),
            safety_score=safety_assessment["safety_score"],
            risk_level=self._humanize_risk_level(safety_assessment["risk_level"]),
            weather_risks=formatted_weather,
            transport_options=formatted_transport,
            safety_alerts="No active alerts",
            conversation_context=conversation_context,
            is_follow_up="YES - Give a concise, focused answer. Don't repeat information already provided." if is_follow_up else "NO - This is a new question.",
        )

        # Call LLM with error handling
        try:
            ai_logger.debug("Calling LLM for travel advice...")
            ai_response = await self.llm.ainvoke(prompt)
            response_content = ai_response.content
            ai_logger.debug(f"LLM response received: {len(response_content)} chars")
        except Exception as e:
            ai_logger.error(f"LLM call failed: {e}")
            # Provide a helpful fallback response
            travel_time = route_service.estimate_travel_time(distance_km)
            response_content = self._generate_fallback_response(
                origin, destination, distance_km, travel_time, 
                transport_options, safety_assessment, group_type
            )

        ai_logger.info(f"Query processed: {origin} -> {destination}")
        
        return {
            "query": query,
            "response": response_content,
            "routes": [
                {
                    "route_name": f"{origin} to {destination}",
                    "distance_km": distance_km,
                    "estimated_time_hours": route_service.estimate_travel_time(distance_km),
                    "safety_score": safety_assessment["safety_score"],
                    "risk_level": safety_assessment["risk_level"],
                    "transport_options": transport_options,
                    "warnings": combined_weather_risks.get("warnings", []),
                    "alternatives": [],
                }
            ],
            "safety_alerts": [],
            "cost_estimate": self._calculate_cost_estimate(transport_options),
            "recommendations": safety_advice,
            "uncertainty_notes": self._generate_uncertainty_notes(route_info, combined_weather_risks),
        }

    def _extract_travel_info(self, query: str) -> Dict[str, Optional[str]]:
        """Extract origin, destination and travel date from query."""
        query_lower = query.lower()
        
        # List of known cities/destinations
        cities = [
            "islamabad",
            "karachi",
            "lahore",
            "peshawar",
            "quetta",
            "swat",
            "murree",
            "gilgit",
            "hunza",
            "skardu",
            "chitral",
            "multan",
            "faisalabad",
            "rawalpindi",
            "naran",
            "kaghan",
            "kalam",
        ]
        
        # Find all cities mentioned
        found = [c for c in cities if c in query_lower]
        
        # Improved logic: check for directional keywords
        origin = None
        destination = None
        
        # Check for "from X to Y" pattern
        from_to_match = re.search(r'from\s+(\w+)\s+to\s+(\w+)', query_lower)
        if from_to_match:
            potential_origin = from_to_match.group(1)
            potential_dest = from_to_match.group(2)
            if potential_origin in cities:
                origin = potential_origin
            if potential_dest in cities:
                destination = potential_dest
        
        # Check for "X to Y" pattern
        if not origin and not destination:
            to_match = re.search(r'(\w+)\s+to\s+(\w+)', query_lower)
            if to_match:
                potential_origin = to_match.group(1)
                potential_dest = to_match.group(2)
                if potential_origin in cities:
                    origin = potential_origin
                if potential_dest in cities:
                    destination = potential_dest
        
        # If only one city found and no "from/to" pattern, treat it as destination
        if not origin and not destination and len(found) == 1:
            destination = found[0]
        elif not origin and not destination and len(found) >= 2:
            origin = found[0]
            destination = found[1]
        elif not destination and len(found) >= 1:
            destination = found[0] if found[0] != origin else (found[1] if len(found) > 1 else None)
        
        return {
            "origin": origin,
            "destination": destination,
            "travel_date": None,
        }

    def _is_comprehensive_request(self, query: str) -> bool:
        """Detect if user is asking for complete/comprehensive guidance."""
        query_lower = query.lower()
        
        # Keywords that indicate user wants everything
        comprehensive_keywords = [
            "everything", "complete", "full guide", "all info", "tell me about",
            "what do i need", "what should i", "plan my", "help me plan",
            "need to know", "guide me", "advise me", "everything necessary",
            "complete guide", "detailed", "all details", "comprehensive",
            "what all", "entire", "thorough", "a to z", "start to finish",
            "from scratch", "step by step", "how to go", "how can i go",
            "what's needed", "what is needed", "requirements", "checklist",
        ]
        
        # Check for comprehensive keywords
        for keyword in comprehensive_keywords:
            if keyword in query_lower:
                return True
        
        # Check for question patterns that imply comprehensive guidance
        comprehensive_patterns = [
            r"going to \w+ .*(what|how|need|should)",
            r"trip to \w+ .*(what|tips|advice|guide)",
            r"\d+ (girls?|boys?|people|friends|family) .*(going|trip|travel)",
            r"(female|women|ladies|girls) .*(group|trip|travel)",
            r"family .*(trip|going|travel)",
        ]
        
        for pattern in comprehensive_patterns:
            if re.search(pattern, query_lower):
                return True
        
        return False

    def _detect_group_type(self, query: str, user_profile: Optional[Dict] = None) -> str:
        """Detect the type of travel group from query and profile."""
        query_lower = query.lower()
        
        # Check for female group indicators
        female_keywords = ["girls", "girl", "female", "women", "ladies", "lady", "gal", "gals"]
        if any(kw in query_lower for kw in female_keywords):
            return "female_group"
        
        # Check for family indicators
        family_keywords = ["family", "families", "kids", "children", "baby", "parents", "elders"]
        if any(kw in query_lower for kw in family_keywords):
            return "family"
        
        # Check for couple
        couple_keywords = ["couple", "honeymoon", "romantic", "two of us", "me and my wife", "me and my husband"]
        if any(kw in query_lower for kw in couple_keywords):
            return "couple"
        
        # Check for solo
        solo_keywords = ["solo", "alone", "myself", "by myself", "single"]
        if any(kw in query_lower for kw in solo_keywords):
            return "solo"
        
        # Check for group
        group_keywords = ["group", "friends", "team", "colleagues", "gang", "squad"]
        if any(kw in query_lower for kw in group_keywords):
            return "group"
        
        # Check user profile
        if user_profile:
            if user_profile.get("travel_group"):
                return user_profile["travel_group"]
            if user_profile.get("gender") == "female":
                return "female_traveler"
        
        return "general"

    def _is_general_travel_question(self, query: str) -> bool:
        """Check if query is a general travel-related question."""
        query_lower = query.lower()
        
        travel_keywords = [
            "travel", "trip", "visit", "go to", "going to", "journey",
            "vacation", "holiday", "tour", "explore", "trek", "hike",
            "safe", "safety", "cost", "budget", "cheap", "expensive",
            "best time", "when to", "how to reach", "transport",
            "hotel", "stay", "accommodation", "food", "eat",
            "pack", "bring", "weather", "road", "route"
        ]
        
        return any(kw in query_lower for kw in travel_keywords)

    def _is_follow_up_question(self, query: str, conversation_history: Optional[List[Dict]]) -> bool:
        """Detect if the current query is a follow-up to previous conversation."""
        if not conversation_history or len(conversation_history) == 0:
            return False
        
        query_lower = query.lower()
        
        # List of known destinations
        all_destinations = [
            "islamabad", "karachi", "lahore", "peshawar", "quetta", "swat",
            "murree", "gilgit", "hunza", "skardu", "chitral", "multan",
            "faisalabad", "rawalpindi", "naran", "kaghan", "kalam",
            "fairy meadows", "attabad", "khunjerab", "babusar", "ayubia",
            "nathia gali", "shogran", "balakot", "mingora", "malam jabba",
            "neelum", "azad kashmir", "kumrat", "bahrain", "madyan"
        ]
        
        # Check if query mentions a NEW destination different from previous context
        query_destinations = [d for d in all_destinations if d in query_lower]
        
        # Get previous destination from history
        prev_destination = None
        for msg in reversed(conversation_history[-6:]):
            content = msg.get("content", "").lower()
            for dest in all_destinations:
                if dest in content:
                    prev_destination = dest
                    break
            if prev_destination:
                break
        
        # If query has a NEW destination that's different from previous, it's NOT a follow-up
        if query_destinations and prev_destination:
            if query_destinations[0] != prev_destination:
                return False  # New destination = new topic, not a follow-up
        
        # If query mentions a specific destination, treat as new question
        if query_destinations and len(query.split()) > 8:
            return False
        
        # Strong follow-up indicators (explicit references to previous conversation)
        strong_follow_up_keywords = [
            "what about", "how about", "tell me more", "more about",
            "elaborate", "explain more", "what else", "anything else",
            "also tell", "and what about", "regarding that",
        ]
        
        for keyword in strong_follow_up_keywords:
            if keyword in query_lower:
                return True
        
        # Very short queries without destinations are likely follow-ups
        if len(query.split()) <= 4 and not query_destinations:
            return True
        
        # Check for pronoun references (it, that, this, there) without new destination
        pronoun_refs = ["about it", "for it", "is it", "was it", "the trip", "the route", "the hotel", "the cost", "the budget"]
        if not query_destinations:
            for ref in pronoun_refs:
                if ref in query_lower:
                    return True
        
        return False

    def _extract_conversation_context(self, conversation_history: List[Dict]) -> Dict[str, Any]:
        """Extract relevant context from conversation history."""
        context = {
            "destination": None,
            "origin": None,
            "topics_discussed": [],
            "last_destination": None,
        }
        
        # Look through recent messages for context
        for msg in conversation_history[-6:]:  # Last 6 messages
            content = msg.get("content", "").lower()
            msg_type = msg.get("type", "")
            
            # Extract destinations mentioned
            cities = [
                "islamabad", "karachi", "lahore", "peshawar", "quetta", "swat",
                "murree", "gilgit", "hunza", "skardu", "chitral", "multan",
                "faisalabad", "rawalpindi", "naran", "kaghan", "kalam",
                "fairy meadows", "attabad", "khunjerab", "babusar", "ayubia",
                "nathia gali", "shogran", "balakot", "mingora", "malam jabba"
            ]
            
            for city in cities:
                if city in content:
                    context["last_destination"] = city
                    if not context["destination"]:
                        context["destination"] = city
            
            # Track topics discussed in AI responses
            if msg_type == "ai":
                topic_keywords = {
                    "budget": ["budget", "cost", "pkr", "price", "expense", "money"],
                    "transport": ["transport", "bus", "car", "drive", "flight", "hiace"],
                    "safety": ["safety", "safe", "caution", "avoid", "risk"],
                    "packing": ["pack", "bring", "clothes", "essentials"],
                    "weather": ["weather", "rain", "cold", "hot", "temperature"],
                    "accommodation": ["hotel", "stay", "accommodation", "lodge", "guest house"],
                    "food": ["food", "eat", "restaurant", "cuisine"],
                    "route": ["route", "road", "highway", "kkh", "way"],
                }
                
                for topic, keywords in topic_keywords.items():
                    if any(kw in content for kw in keywords):
                        if topic not in context["topics_discussed"]:
                            context["topics_discussed"].append(topic)
        
        return context

    def _format_conversation_history(self, conversation_history: List[Dict]) -> str:
        """Format conversation history for context in the prompt."""
        if not conversation_history:
            return ""
        
        # Take last 4 exchanges (8 messages max)
        recent = conversation_history[-8:]
        
        formatted = "PREVIOUS CONVERSATION:\n"
        for msg in recent:
            role = "User" if msg.get("type") == "user" else "Assistant"
            content = msg.get("content", "")
            # Truncate long messages
            if len(content) > 300:
                content = content[:300] + "..."
            formatted += f"{role}: {content}\n\n"
        
        return formatted

    def _extract_time_of_day(self, query: str, travel_date: Optional[str]) -> Optional[str]:
        q = query.lower()
        if "night" in q or "evening" in q:
            return "night"
        if "morning" in q:
            return "morning"
        if "afternoon" in q:
            return "afternoon"
        return None

    def _combine_weather_risks(self, risks1: Dict, risks2: Dict) -> Dict:
        risk_levels = [risks1.get("risk_level"), risks2.get("risk_level")]
        if "high" in risk_levels:
            combined_level = "high"
        elif "medium" in risk_levels:
            combined_level = "medium"
        else:
            combined_level = "low"
        return {
            "risk_level": combined_level,
            "risks": list(set(risks1.get("risks", []) + risks2.get("risks", []))),
            "warnings": list(set(risks1.get("warnings", []) + risks2.get("warnings", []))),
        }

    def _format_transport_options(self, options: List[Dict]) -> str:
        if not options:
            return "No transport options available"
        return "\n".join(
            [
                f"- {o['mode'].upper()}: PKR {o['estimated_fare_pkr']:.0f} (Time: {o['estimated_time_hours']}h, Risk: {o['risk_level']})"
                for o in options
            ]
        )

    def _format_weather_risks(self, risks: Dict) -> str:
        if risks.get("risk_level") == "unknown":
            return "Weather data not available"
        warnings = risks.get("warnings", [])
        return "\n".join([f"- {w}" for w in warnings]) if warnings else "No significant weather risks"

    def _format_user_profile(self, profile: Optional[Dict]) -> str:
        if not profile:
            return "Not specified"
        parts: List[str] = []
        if profile.get("gender"):
            parts.append(f"Gender: {profile['gender']}")
        if profile.get("travel_group"):
            parts.append(f"Travel Group: {profile['travel_group']}")
        return ", ".join(parts) if parts else "Not specified"

    def _format_user_profile_enhanced(self, profile: Optional[Dict], group_type: str, query: str) -> str:
        """Format user profile with enhanced group detection for better personalized advice."""
        parts: List[str] = []
        
        # Add detected group type
        group_descriptions = {
            "female_group": "Female group travelers - provide safety tips specific to women traveling in Pakistan",
            "female_traveler": "Female solo traveler - provide extra safety considerations",
            "family": "Family with children - recommend family-friendly options and shorter travel segments",
            "couple": "Couple traveling together",
            "solo": "Solo traveler",
            "group": "Group of friends/colleagues",
            "general": "General travelers"
        }
        
        parts.append(f"Group Type: {group_descriptions.get(group_type, 'General travelers')}")
        
        # Try to detect number of people from query
        num_match = re.search(r'(\d+)\s*(girls?|boys?|people|friends?|members?|persons?)', query.lower())
        if num_match:
            parts.append(f"Number of people: {num_match.group(1)}")
        
        # Add profile info if available
        if profile:
            if profile.get("gender"):
                parts.append(f"Gender: {profile['gender']}")
            if profile.get("travel_group"):
                parts.append(f"Travel style: {profile['travel_group']}")
            if profile.get("preferredBudget"):
                parts.append(f"Budget preference: {profile['preferredBudget']}")
            if profile.get("homeCity"):
                parts.append(f"Home city: {profile['homeCity']}")
        
        return " | ".join(parts)

    def _humanize_risk_level(self, risk_level: str) -> str:
        """Convert technical risk levels to human-friendly descriptions."""
        level_descriptions = {
            "low": "Generally safe and recommended for travel",
            "medium": "Safe with some precautions needed",
            "high": "Extra caution advised - check conditions before traveling",
            "critical": "Travel not recommended at this time",
            "recommended": "Great conditions for travel",
            "caution": "Proceed with awareness of current conditions",
            "avoid": "Consider postponing or alternative routes"
        }
        return level_descriptions.get(risk_level.lower(), risk_level)

    def _generate_fallback_response(
        self, 
        origin: str, 
        destination: str, 
        distance_km: float,
        travel_time: float,
        transport_options: List[Dict],
        safety_assessment: Dict,
        group_type: str
    ) -> str:
        """Generate a helpful human-style fallback response when LLM fails."""
        
        # Get cheapest and fastest options
        cheapest = min(transport_options, key=lambda x: x.get('estimated_fare_pkr', float('inf'))) if transport_options else None
        
        response = f"""## 🧭 Trip from {origin.title()} to {destination.title()}

### 📍 Quick Overview
- **Distance**: {distance_km} km
- **Travel Time**: ~{travel_time:.1f} hours
- **Conditions**: {self._humanize_risk_level(safety_assessment.get('risk_level', 'unknown'))}

### 🚗 Getting There
"""
        
        if transport_options:
            for opt in transport_options[:3]:
                response += f"- **{opt['mode'].title()}**: PKR {opt['estimated_fare_pkr']:,.0f} (~{opt['estimated_time_hours']}h)\n"
        else:
            response += "- Check local transport options when you arrive\n"
        
        response += f"""
### 💰 Budget Tips
- Carry cash as ATMs are limited in remote areas
- Book accommodations in advance during peak season
- {f'Budget-friendly option: {cheapest["mode"].title()} at PKR {cheapest["estimated_fare_pkr"]:,.0f}' if cheapest else 'Compare prices at local transport stands'}

### 🛡️ Safety Tips
"""
        
        if group_type == "female_group":
            response += """- Travel during daylight hours only
- Stay at well-reviewed, family-friendly hotels
- Dress conservatively in northern areas
- Keep emergency contacts saved offline
- Share your live location with family
"""
        elif group_type == "family":
            response += """- Plan shorter travel segments for children
- Carry snacks and entertainment for the journey
- Book family rooms in advance
- Allow extra time for rest stops
- Keep children's medications handy
"""
        else:
            response += """- Avoid night travel on mountain roads
- Keep your phone charged and save emergency numbers
- Register with tourism police if required
- Share your travel plan with family
- Carry a first aid kit
"""
        
        response += """
### ✅ Before You Go
- Download offline maps
- Save emergency contacts (Rescue 1122)
- Carry CNIC/ID for checkpoints
- Check weather conditions
- Pack appropriate clothing for the destination
"""
        
        return response

    def _calculate_cost_estimate(self, transport_options: List[Dict]) -> Optional[Dict[str, float]]:
        if not transport_options:
            return None
        costs = [float(o.get("estimated_fare_pkr", 0) or 0) for o in transport_options]
        return {"cheapest": min(costs), "most_expensive": max(costs), "average": sum(costs) / len(costs)}

    def _generate_uncertainty_notes(self, route_info: Dict, weather_risks: Dict) -> Optional[str]:
        notes: List[str] = []
        if weather_risks.get("risk_level") == "unknown":
            notes.append("Weather data may not be available for all locations")
        if not route_info.get("distance_km"):
            notes.append("Route distance is estimated and may vary")
        return ("Note: " + "; ".join(notes)) if notes else None

    # ==================== TRIP PLANNING METHODS ====================

    async def generate_trip_plan(
        self,
        destination: str,
        duration_days: int,
        travel_type: str,
        num_people: int,
        budget_pkr: int,
        travel_style: str = "comfort",
        origin_city: str = "Islamabad",
        start_date: Optional[str] = None,
        special_requirements: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Generate a complete trip plan with day-by-day itinerary."""
        ai_logger.info(
            f"Generating trip plan: {destination}, {duration_days} days, "
            f"{travel_type} ({num_people}), budget PKR {budget_pkr}"
        )
        
        # Gather route data for the destination
        try:
            route_data = self._gather_destination_routes(origin_city, destination)
        except Exception as e:
            ai_logger.warning(f"Route data gathering failed: {e}")
            route_data = {"main_route": {}, "intermediate_routes": [], "destination_info": {}}
        
        # Get weather data
        weather_data = await self._gather_weather_data(destination)
        
        # Get safety alerts
        safety_alerts = weather_service.get_active_alerts(destination)
        
        # Get transport options
        transport_options = route_service.get_transport_options(origin_city, destination)
        
        # Build prompt
        trip_prompt = get_trip_planner_prompt()
        
        prompt = trip_prompt.format_messages(
            destination=destination,
            duration_days=duration_days,
            travel_type=travel_type,
            num_people=num_people,
            budget_pkr=budget_pkr,
            travel_style=travel_style,
            origin_city=origin_city,
            start_date=start_date or "Flexible",
            special_requirements=", ".join(special_requirements) if special_requirements else "None",
            route_data=json.dumps(route_data, indent=2),
            weather_data=json.dumps(weather_data, indent=2),
            safety_alerts=json.dumps(safety_alerts, indent=2),
            transport_options=self._format_transport_options(transport_options),
            current_date=datetime.now().strftime("%Y-%m-%d"),
        )
        
        # Call LLM with error handling
        try:
            ai_logger.debug("Calling LLM for trip plan generation...")
            ai_response = await self.llm.ainvoke(prompt)
            ai_logger.debug(f"LLM response received: {len(ai_response.content)} chars")
        except Exception as e:
            ai_logger.error(f"LLM call failed for trip plan: {e}")
            raise RuntimeError(f"Failed to generate trip plan: {e}")
        
        # Parse JSON response
        trip_plan = self._parse_trip_plan_response(ai_response.content)
        ai_logger.info(f"Trip plan parsed: {len(trip_plan.get('daily_plan', []))} days")
        
        # Add request metadata
        trip_plan["destination"] = destination
        trip_plan["duration_days"] = duration_days
        trip_plan["travel_type"] = travel_type
        trip_plan["num_people"] = num_people
        trip_plan["budget_pkr"] = budget_pkr
        trip_plan["travel_style"] = travel_style
        trip_plan["origin_city"] = origin_city
        
        return trip_plan

    async def parse_quick_trip_request(self, query: str) -> Dict[str, Any]:
        """Parse a natural language trip request into structured format."""
        from langchain.prompts import ChatPromptTemplate
        
        prompt = ChatPromptTemplate.from_template(QUICK_TRIP_PARSE_PROMPT)
        messages = prompt.format_messages(query=query)
        
        response = await self.llm.ainvoke(messages)
        
        try:
            # Try to parse JSON from response
            content = response.content.strip()
            # Remove markdown code blocks if present
            if content.startswith("```"):
                content = re.sub(r"```(?:json)?\n?", "", content)
                content = content.strip()
            
            parsed = json.loads(content)
            
            # Set defaults for missing fields
            defaults = {
                "destination": "Hunza",
                "duration_days": 5,
                "travel_type": "family",
                "num_people": 4,
                "budget_pkr": 150000,
                "travel_style": "comfort",
                "origin_city": "Islamabad",
                "start_date": None,
                "special_requirements": None,
            }
            
            for key, default in defaults.items():
                if key not in parsed or parsed[key] is None:
                    parsed[key] = default
            
            return parsed
            
        except json.JSONDecodeError:
            # Return defaults if parsing fails
            return {
                "destination": self._extract_destination_from_query(query),
                "duration_days": self._extract_duration_from_query(query),
                "travel_type": self._extract_travel_type_from_query(query),
                "num_people": 4,
                "budget_pkr": self._extract_budget_from_query(query),
                "travel_style": "comfort",
                "origin_city": "Islamabad",
                "start_date": None,
                "special_requirements": None,
            }

    def _gather_destination_routes(self, origin: str, destination: str) -> Dict[str, Any]:
        """Gather route information for a destination."""
        route_info = route_service.get_route_info(origin, destination)
        
        # Also get routes between popular stops
        intermediate_cities = self._get_intermediate_cities(destination)
        intermediate_routes = []
        
        for city in intermediate_cities:
            info = route_service.get_route_info(origin, city)
            if info.get("distance_km"):
                intermediate_routes.append({
                    "from": origin,
                    "to": city,
                    "distance_km": info["distance_km"],
                    "time_hours": info.get("estimated_time_hours"),
                })
        
        return {
            "main_route": route_info,
            "intermediate_routes": intermediate_routes,
            "destination_info": self._get_destination_info(destination),
        }

    async def _gather_weather_data(self, destination: str) -> Dict[str, Any]:
        """Gather weather data for destination and route."""
        weather = await weather_service.get_weather(destination)
        risks = weather_service.assess_weather_risks(weather)
        
        return {
            "current_weather": weather,
            "risks": risks,
            "forecast_summary": "Check local weather before travel",
        }

    def _get_intermediate_cities(self, destination: str) -> List[str]:
        """Get intermediate cities for a destination route."""
        destination_lower = destination.lower()
        
        routes = {
            "hunza": ["Chilas", "Gilgit", "Karimabad"],
            "skardu": ["Chilas", "Gilgit"],
            "gilgit": ["Chilas"],
            "swat": ["Mingora", "Kalam"],
            "chitral": ["Dir", "Lowari Top"],
            "naran": ["Mansehra", "Kaghan"],
            "murree": ["Rawalpindi"],
        }
        
        return routes.get(destination_lower, [])

    def _get_destination_info(self, destination: str) -> Dict[str, Any]:
        """Get destination-specific information."""
        destination_lower = destination.lower()
        
        info_db = {
            "hunza": {
                "altitude_m": 2500,
                "best_season": "April to October",
                "highlights": ["Attabad Lake", "Eagle's Nest", "Baltit Fort", "Passu Cones"],
                "warnings": ["Altitude sickness risk", "Limited ATMs", "Cold nights"],
            },
            "skardu": {
                "altitude_m": 2228,
                "best_season": "May to September",
                "highlights": ["Shangrila Resort", "Upper Kachura Lake", "Deosai Plains"],
                "warnings": ["Remote area", "Long travel time", "Weather dependent flights"],
            },
            "swat": {
                "altitude_m": 980,
                "best_season": "March to October",
                "highlights": ["Malam Jabba", "Fizagat Park", "Swat Museum", "Kalam Valley"],
                "warnings": ["Road conditions vary", "Crowded in peak season"],
            },
            "gilgit": {
                "altitude_m": 1500,
                "best_season": "April to October",
                "highlights": ["Naltar Valley", "Kargah Buddha", "Gilgit River"],
                "warnings": ["Gateway to Hunza/Skardu", "Stock up supplies here"],
            },
            "naran": {
                "altitude_m": 2409,
                "best_season": "June to September",
                "highlights": ["Lake Saif ul Malook", "Lulusar Lake", "Babusar Pass"],
                "warnings": ["Crowded in summer", "Road closures in winter"],
            },
            "murree": {
                "altitude_m": 2291,
                "best_season": "Year round (snow in winter)",
                "highlights": ["Mall Road", "Pindi Point", "Kashmir Point"],
                "warnings": ["Very crowded on weekends", "Traffic jams common"],
            },
        }
        
        return info_db.get(destination_lower, {
            "altitude_m": 1000,
            "best_season": "Varies",
            "highlights": [],
            "warnings": ["Limited information available"],
        })

    def _parse_trip_plan_response(self, content: str) -> Dict[str, Any]:
        """Parse the AI response into a structured trip plan."""
        try:
            # Remove markdown code blocks if present
            content = content.strip()
            if content.startswith("```"):
                content = re.sub(r"```(?:json)?\n?", "", content)
                content = content.strip()
            if content.endswith("```"):
                content = content[:-3].strip()
            
            return json.loads(content)
            
        except json.JSONDecodeError as e:
            # Return a basic error structure
            return {
                "trip_title": "Trip Plan",
                "best_time_to_visit": "Varies by season",
                "weather_summary": "Check local conditions",
                "daily_plan": [],
                "cost_breakdown": {
                    "transport": 0,
                    "accommodation": 0,
                    "food": 0,
                    "activities": 0,
                    "miscellaneous": 0,
                    "total": 0,
                    "per_person": 0,
                    "buffer": 0,
                },
                "budget_status": "unknown",
                "cost_saving_tips": [],
                "safety_notes": ["Unable to generate detailed plan. Please try again."],
                "weather_warnings": [],
                "road_conditions": [],
                "altitude_warnings": [],
                "connectivity_notes": [],
                "fuel_stops": [],
                "packing_checklist": [],
                "documents_required": [],
                "emergency_contacts": [],
                "local_tips": [],
                "food_recommendations": [],
                "must_visit_spots": [],
                "uncertainty_notes": f"AI response parsing error: {str(e)}",
                "data_freshness": datetime.now().strftime("%Y-%m-%d"),
                "_raw_response": content[:500],  # Include partial response for debugging
            }

    def _extract_destination_from_query(self, query: str) -> Optional[str]:
        """Extract destination from natural language query."""
        query_lower = query.lower()
        # Extended list of destinations
        destinations = [
            "hunza", "skardu", "swat", "gilgit", "chitral", "naran", "murree", 
            "kaghan", "kalam", "malam jabba", "fairy meadows", "attabad", 
            "khunjerab", "ayubia", "nathia gali", "shogran", "balakot",
            "mingora", "bahrain", "madyan", "kumrat", "neelum", "azad kashmir",
            "lahore", "karachi", "peshawar", "quetta", "multan", "faisalabad"
        ]
        for dest in destinations:
            if dest in query_lower:
                return dest.title()
        return None  # Return None if no destination found

    def _extract_duration_from_query(self, query: str) -> int:
        """Extract trip duration from query."""
        match = re.search(r"(\d+)\s*(?:day|days)", query.lower())
        if match:
            return int(match.group(1))
        return 5

    def _extract_travel_type_from_query(self, query: str) -> str:
        """Extract travel type from query."""
        query_lower = query.lower()
        if "family" in query_lower:
            return "family"
        if "group" in query_lower:
            return "group"
        if "solo" in query_lower:
            return "solo"
        if "couple" in query_lower:
            return "couple"
        return "family"

    def _extract_budget_from_query(self, query: str) -> int:
        """Extract budget from query."""
        # Match patterns like "100k", "100000", "1 lakh"
        match = re.search(r"(\d+)\s*k\b", query.lower())
        if match:
            return int(match.group(1)) * 1000
        
        match = re.search(r"(\d+)\s*lakh", query.lower())
        if match:
            return int(match.group(1)) * 100000
        
        match = re.search(r"(\d{5,})", query)
        if match:
            return int(match.group(1))
        
        return 150000  # Default budget
