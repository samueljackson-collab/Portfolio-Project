"""Utilities for validating photos and extracting metadata."""

from __future__ import annotations

import asyncio
import imghdr
import io
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Optional, Tuple

from PIL import Image, ExifTags


SUPPORTED_IMAGE_TYPES = {"jpeg", "png", "heic", "tiff"}


@dataclass
class PhotoMetadata:
    width: Optional[int] = None
    height: Optional[int] = None
    capture_date: Optional[datetime] = None
    camera_make: Optional[str] = None
    camera_model: Optional[str] = None
    focal_length: Optional[str] = None
    aperture: Optional[str] = None
    iso: Optional[int] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    mime_type: Optional[str] = None


def detect_mime_type(data: bytes) -> str:
    """Best-effort MIME type detection using imghdr and Pillow."""

    detected = imghdr.what(None, data)
    if detected and detected.lower() in SUPPORTED_IMAGE_TYPES:
        if detected.lower() == "jpeg":
            return "image/jpeg"
        if detected.lower() == "png":
            return "image/png"
        if detected.lower() == "tiff":
            return "image/tiff"
        if detected.lower() == "heic":
            return "image/heic"
    # Fallback to Pillow inspection
    with Image.open(io.BytesIO(data)) as img:
        return Image.MIME.get(img.format, "application/octet-stream")


def _get_if_exist(data: Dict[int, Any], key: int) -> Any:
    return data.get(key)


def _convert_to_degrees(value: Tuple) -> float:
    """Convert GPS coordinates stored as rational numbers to float."""

    d = float(value[0][0]) / float(value[0][1])
    m = float(value[1][0]) / float(value[1][1])
    s = float(value[2][0]) / float(value[2][1])
    return d + (m / 60.0) + (s / 3600.0)


async def create_thumbnail(image_data: bytes, *, max_size: Tuple[int, int] = (512, 512), quality: int = 85) -> bytes:
    """Generate a thumbnail asynchronously to avoid blocking the event loop."""

    return await asyncio.to_thread(_create_thumbnail_sync, image_data, max_size, quality)


def _create_thumbnail_sync(image_data: bytes, max_size: Tuple[int, int], quality: int) -> bytes:
    with Image.open(io.BytesIO(image_data)) as image:
        if image.mode not in ("RGB", "L"):
            image = image.convert("RGB")
        image.thumbnail(max_size, Image.Resampling.LANCZOS)

        output = io.BytesIO()
        image.save(output, format="JPEG", quality=quality, optimize=True)
    output.seek(0)
    return output.read()


def extract_exif_data(image_data: bytes) -> PhotoMetadata:
    """Extract metadata from EXIF synchronously."""

    with Image.open(io.BytesIO(image_data)) as image:
        metadata = PhotoMetadata(width=image.width, height=image.height)
        exif = image.getexif()
        if exif:
            exif_dict = {ExifTags.TAGS.get(k, k): v for k, v in exif.items()}

            datetime_original = exif_dict.get("DateTimeOriginal")
            if datetime_original:
                try:
                    metadata.capture_date = datetime.strptime(datetime_original, "%Y:%m:%d %H:%M:%S")
                except ValueError:
                    pass

            metadata.camera_make = exif_dict.get("Make")
            metadata.camera_model = exif_dict.get("Model")

            focal = exif_dict.get("FocalLength")
            if isinstance(focal, tuple) and focal[1]:
                metadata.focal_length = f"{focal[0] / focal[1]:.1f}mm"

            aperture = exif_dict.get("FNumber")
            if isinstance(aperture, tuple) and aperture[1]:
                metadata.aperture = f"f/{aperture[0] / aperture[1]:.1f}"

            iso = exif_dict.get("ISOSpeedRatings") or exif_dict.get("PhotographicSensitivity")
            if isinstance(iso, int):
                metadata.iso = iso

            gps_info = exif_dict.get("GPSInfo")
            if isinstance(gps_info, dict):
                gps_latitude = _get_if_exist(gps_info, 2)
                gps_latitude_ref = _get_if_exist(gps_info, 1)
                gps_longitude = _get_if_exist(gps_info, 4)
                gps_longitude_ref = _get_if_exist(gps_info, 3)

                if gps_latitude and gps_latitude_ref and gps_longitude and gps_longitude_ref:
                    lat = _convert_to_degrees(gps_latitude)
                    if gps_latitude_ref != "N":
                        lat = -lat
                    lon = _convert_to_degrees(gps_longitude)
                    if gps_longitude_ref != "E":
                        lon = -lon
                    metadata.latitude = lat
                    metadata.longitude = lon

    metadata.mime_type = detect_mime_type(image_data)
    return metadata
