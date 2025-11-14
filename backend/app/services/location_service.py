"""Reverse geocoding utilities with Nominatim-safe access."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Optional

from geopy.exc import GeopyError
from geopy.geocoders import Nominatim

from app.config import settings


@dataclass
class Location:
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    display_name: Optional[str] = None


class LocationService:
    """Wrapper around geopy that respects async best practices and rate limits."""

    def __init__(self) -> None:
        self._geocoder = Nominatim(user_agent=settings.nominatim_user_agent)

    async def reverse_geocode(self, latitude: Optional[float], longitude: Optional[float]) -> Optional[Location]:
        if latitude is None or longitude is None:
            return None

        try:
            location = await asyncio.to_thread(
                self._geocoder.reverse,
                f"{latitude}, {longitude}",
                exactly_one=True,
                language="en",
                timeout=settings.nominatim_request_timeout,
            )
            # Honor 1 request/second usage policy
            await asyncio.sleep(settings.nominatim_rate_limit_seconds)
        except GeopyError:
            return None

        if not location:
            return None

        address = (location.raw or {}).get("address", {})
        return Location(
            city=address.get("city")
            or address.get("town")
            or address.get("village")
            or address.get("hamlet"),
            state=address.get("state") or address.get("state_district"),
            country=address.get("country"),
            display_name=location.address,
        )

    @staticmethod
    def should_create_location_album(city: Optional[str]) -> bool:
        return bool(city)

    @staticmethod
    def format_location_name(city: Optional[str], state: Optional[str], country: Optional[str]) -> str:
        segments = [segment for segment in [city, state, country] if segment]
        return " · ".join(segments) if segments else "Unknown Location"


location_service = LocationService()
