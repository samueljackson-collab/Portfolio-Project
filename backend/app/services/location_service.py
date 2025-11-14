"""
Location service for reverse geocoding GPS coordinates to city names.

Uses the Nominatim geocoder (OpenStreetMap) to convert latitude/longitude
coordinates into human-readable location names.
"""

import asyncio
from typing import Optional, Dict
from geopy.geocoders import Nominatim
from geopy.exc import GeopyError
import logging

logger = logging.getLogger(__name__)

# Initialize geocoder with a custom user agent
# Nominatim requires a unique user agent per application
geocoder = Nominatim(user_agent="elderphoto_portfolio_app/1.0")
_rate_limit_lock = asyncio.Lock()
_last_geocode_time: float = 0.0


class LocationInfo:
    """Container for location information from reverse geocoding."""

    def __init__(self):
        self.city: Optional[str] = None
        self.state: Optional[str] = None
        self.country: Optional[str] = None
        self.full_address: Optional[str] = None


async def reverse_geocode(
    latitude: float, longitude: float, timeout: int = 5
) -> LocationInfo:
    """
    Convert GPS coordinates to human-readable location information.

    Args:
        latitude: GPS latitude
        longitude: GPS longitude
        timeout: Request timeout in seconds

    Returns:
        LocationInfo object with city, state, country
    """
    location_info = LocationInfo()

    try:
        async with _rate_limit_lock:
            global _last_geocode_time
            loop = asyncio.get_running_loop()
            elapsed = loop.time() - _last_geocode_time
            if elapsed < 1:
                await asyncio.sleep(1 - elapsed)

            location = await asyncio.to_thread(
                geocoder.reverse,
                f"{latitude}, {longitude}",
                exactly_one=True,
                language="en",
                timeout=timeout,
            )
            _last_geocode_time = loop.time()

        if not location:
            logger.warning(
                f"No location found for coordinates: ({latitude}, {longitude})"
            )
            return location_info

        # Extract address components
        address = location.raw.get("address", {})

        # Try to get city from various possible fields
        location_info.city = (
            address.get("city")
            or address.get("town")
            or address.get("village")
            or address.get("municipality")
            or address.get("hamlet")
        )

        # Get state/region
        location_info.state = (
            address.get("state")
            or address.get("region")
            or address.get("province")
            or address.get("county")
        )

        # Get country
        location_info.country = address.get("country")

        # Store full formatted address
        location_info.full_address = location.address

        logger.info(
            f"Geocoded ({latitude}, {longitude}) -> "
            f"{location_info.city}, {location_info.state}, {location_info.country}"
        )

    except GeopyError as e:
        logger.error(f"Geocoding error: {e}")
    except Exception as e:
        logger.error(f"Unexpected error during geocoding: {e}")

    return location_info


def format_location_name(city: Optional[str], state: Optional[str], country: Optional[str]) -> str:
    """
    Format location components into a display name.

    Args:
        city: City name
        state: State/region name
        country: Country name

    Returns:
        Formatted location string (e.g., "San Francisco, CA" or "Paris, France")
    """
    parts = []

    if city:
        parts.append(city)

    # For US locations, include state abbreviation
    # For international, include country
    if state and country == "United States":
        # Try to use state abbreviation if it's short
        state_abbrev = _get_state_abbreviation(state)
        parts.append(state_abbrev)
    elif country and country != "United States":
        parts.append(country)

    return ", ".join(parts) if parts else "Unknown Location"


def _get_state_abbreviation(state: str) -> str:
    """
    Convert US state name to abbreviation.

    Args:
        state: Full state name

    Returns:
        State abbreviation or original name if not found
    """
    us_states = {
        "Alabama": "AL", "Alaska": "AK", "Arizona": "AZ", "Arkansas": "AR",
        "California": "CA", "Colorado": "CO", "Connecticut": "CT", "Delaware": "DE",
        "Florida": "FL", "Georgia": "GA", "Hawaii": "HI", "Idaho": "ID",
        "Illinois": "IL", "Indiana": "IN", "Iowa": "IA", "Kansas": "KS",
        "Kentucky": "KY", "Louisiana": "LA", "Maine": "ME", "Maryland": "MD",
        "Massachusetts": "MA", "Michigan": "MI", "Minnesota": "MN", "Mississippi": "MS",
        "Missouri": "MO", "Montana": "MT", "Nebraska": "NE", "Nevada": "NV",
        "New Hampshire": "NH", "New Jersey": "NJ", "New Mexico": "NM", "New York": "NY",
        "North Carolina": "NC", "North Dakota": "ND", "Ohio": "OH", "Oklahoma": "OK",
        "Oregon": "OR", "Pennsylvania": "PA", "Rhode Island": "RI", "South Carolina": "SC",
        "South Dakota": "SD", "Tennessee": "TN", "Texas": "TX", "Utah": "UT",
        "Vermont": "VT", "Virginia": "VA", "Washington": "WA", "West Virginia": "WV",
        "Wisconsin": "WI", "Wyoming": "WY"
    }

    return us_states.get(state, state)


def should_create_location_album(city: Optional[str]) -> bool:
    """
    Determine if a location-based album should be created.

    Args:
        city: City name

    Returns:
        True if album should be created, False otherwise
    """
    # Only create album if we have a valid city name
    return bool(city and city.strip())
