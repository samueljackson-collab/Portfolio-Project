"""
Photo service for EXIF metadata extraction and image processing.

Handles extraction of metadata from uploaded photos including:
- Capture date and time
- GPS coordinates (latitude/longitude)
- Camera information (make/model)
- Image dimensions
"""

import io
import asyncio
from datetime import datetime
from typing import Optional, Dict, Any
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
import logging

logger = logging.getLogger(__name__)


class PhotoMetadata:
    """Container for photo metadata extracted from EXIF."""

    def __init__(self):
        self.width: Optional[int] = None
        self.height: Optional[int] = None
        self.capture_date: Optional[datetime] = None
        self.latitude: Optional[float] = None
        self.longitude: Optional[float] = None
        self.camera_make: Optional[str] = None
        self.camera_model: Optional[str] = None


def extract_exif_data(image_data: bytes) -> PhotoMetadata:
    """
    Extract EXIF metadata from image bytes.

    Args:
        image_data: Raw image file bytes

    Returns:
        PhotoMetadata object with extracted information
    """
    metadata = PhotoMetadata()

    try:
        # Open image from bytes
        image = Image.open(io.BytesIO(image_data))

        # Get image dimensions
        metadata.width, metadata.height = image.size

        # Extract EXIF data
        exif_data = image._getexif()
        if not exif_data:
            logger.info("No EXIF data found in image")
            return metadata

        # Parse EXIF tags
        exif_dict = {}
        for tag_id, value in exif_data.items():
            tag_name = TAGS.get(tag_id, tag_id)
            exif_dict[tag_name] = value

        # Extract capture date
        date_str = exif_dict.get("DateTime") or exif_dict.get("DateTimeOriginal")
        if date_str:
            try:
                # EXIF date format: "YYYY:MM:DD HH:MM:SS"
                metadata.capture_date = datetime.strptime(date_str, "%Y:%m:%d %H:%M:%S")
            except ValueError as e:
                logger.warning(f"Failed to parse date '{date_str}': {e}")

        # Extract camera information
        metadata.camera_make = exif_dict.get("Make")
        metadata.camera_model = exif_dict.get("Model")

        # Clean up camera strings (remove extra whitespace/null chars)
        if metadata.camera_make:
            metadata.camera_make = metadata.camera_make.strip().replace("\x00", "")
        if metadata.camera_model:
            metadata.camera_model = metadata.camera_model.strip().replace("\x00", "")

        # Extract GPS data
        gps_info = exif_dict.get("GPSInfo")
        if gps_info:
            gps_data = _parse_gps_info(gps_info)
            metadata.latitude = gps_data.get("latitude")
            metadata.longitude = gps_data.get("longitude")

        logger.info(
            f"Extracted metadata: {metadata.width}x{metadata.height}, "
            f"date={metadata.capture_date}, "
            f"location=({metadata.latitude}, {metadata.longitude})"
        )

    except Exception as e:
        logger.error(f"Error extracting EXIF data: {e}")

    return metadata


def _parse_gps_info(gps_info: Dict[int, Any]) -> Dict[str, float]:
    """
    Parse GPS information from EXIF GPSInfo tag.

    Args:
        gps_info: Raw GPS info dictionary from EXIF

    Returns:
        Dictionary with 'latitude' and 'longitude' keys
    """
    gps_data = {}

    try:
        # Convert GPS tag IDs to names
        gps_dict = {}
        for key, val in gps_info.items():
            tag_name = GPSTAGS.get(key, key)
            gps_dict[tag_name] = val

        # Extract latitude
        if "GPSLatitude" in gps_dict and "GPSLatitudeRef" in gps_dict:
            lat = _convert_to_degrees(gps_dict["GPSLatitude"])
            if gps_dict["GPSLatitudeRef"] == "S":
                lat = -lat
            gps_data["latitude"] = lat

        # Extract longitude
        if "GPSLongitude" in gps_dict and "GPSLongitudeRef" in gps_dict:
            lon = _convert_to_degrees(gps_dict["GPSLongitude"])
            if gps_dict["GPSLongitudeRef"] == "W":
                lon = -lon
            gps_data["longitude"] = lon

    except Exception as e:
        logger.error(f"Error parsing GPS info: {e}")

    return gps_data


def _convert_to_degrees(value: tuple) -> float:
    """
    Convert GPS coordinates from degrees/minutes/seconds to decimal degrees.

    Args:
        value: Tuple of (degrees, minutes, seconds) as ratios

    Returns:
        Decimal degrees
    """
    d = float(value[0])
    m = float(value[1])
    s = float(value[2])
    return d + (m / 60.0) + (s / 3600.0)


async def create_thumbnail(
    image_data: bytes, max_size: tuple = (400, 400), quality: int = 85
) -> bytes:
    """
    Create a thumbnail from the original image.

    Args:
        image_data: Original image bytes
        max_size: Maximum dimensions (width, height) for thumbnail
        quality: JPEG quality (1-100)

    Returns:
        Thumbnail image bytes
    """

    def _generate_thumbnail() -> bytes:
        try:
            # Open original image
            image = Image.open(io.BytesIO(image_data))

            # Convert to RGB if necessary (handles RGBA, P, etc.)
            if image.mode not in ("RGB", "L"):
                image = image.convert("RGB")

            # Create thumbnail (maintains aspect ratio)
            image.thumbnail(max_size, Image.Resampling.LANCZOS)

            # Save to bytes
            output = io.BytesIO()
            image.save(output, format="JPEG", quality=quality, optimize=True)
            output.seek(0)

            return output.read()

        except Exception as e:
            logger.error(f"Error creating thumbnail: {e}")
            raise

    return await asyncio.to_thread(_generate_thumbnail)


def validate_image(image_data: bytes) -> bool:
    """
    Validate that the provided bytes represent a valid image.

    Args:
        image_data: Image bytes to validate

    Returns:
        True if valid image, False otherwise
    """
    try:
        image = Image.open(io.BytesIO(image_data))
        image.verify()
        return True
    except Exception as e:
        logger.warning(f"Invalid image: {e}")
        return False


def get_mime_type(image_data: bytes) -> str:
    """
    Detect MIME type from image data.

    Args:
        image_data: Image bytes

    Returns:
        MIME type string (e.g., "image/jpeg", "image/png")
    """
    try:
        image = Image.open(io.BytesIO(image_data))
        format_to_mime = {
            "JPEG": "image/jpeg",
            "PNG": "image/png",
            "GIF": "image/gif",
            "WEBP": "image/webp",
            "BMP": "image/bmp",
            "TIFF": "image/tiff",
        }
        return format_to_mime.get(image.format, "image/jpeg")
    except Exception as e:
        logger.error(f"Error detecting MIME type: {e}")
        return "image/jpeg"
