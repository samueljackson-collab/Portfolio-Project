"""
Photo management endpoints for upload and retrieval.

This module provides:
- Upload photos with automatic EXIF extraction and organization
- List photos with filtering (by date, location, album)
- Get single photo details
- Delete photos
- Calendar view (photos grouped by date)
- Album management (auto-created by location)
"""

import asyncio
from uuid import UUID
from typing import Optional
from datetime import datetime
from fastapi import (
    APIRouter,
    Depends,
    status,
    Query,
    UploadFile,
    File,
    Response,
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, extract
from sqlalchemy.exc import IntegrityError

from app.database import get_db
from app.models import User, Photo, Album
from app.config import settings
from app.schemas import (
    PhotoResponse,
    PhotoListResponse,
    PhotoUploadResponse,
    AlbumResponse,
    AlbumListResponse,
    CalendarMonthResponse,
    CalendarDateResponse,
)
from app.dependencies import (
    get_current_user,
    raise_not_found,
    raise_bad_request,
    raise_conflict,
    raise_server_error,
)
from app.services import photo_service, location_service, storage_service

router = APIRouter(
    prefix="/photos",
    tags=["Photos"],
)


@router.post(
    "/upload",
    response_model=PhotoUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload Photo",
    description="Upload a photo with automatic EXIF extraction and location-based organization",
)
async def upload_photo(
    file: UploadFile = File(..., description="Photo file to upload"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PhotoUploadResponse:
    """
    Upload a photo and automatically extract metadata.

    Process:
    1. Validate file is a valid image
    2. Extract EXIF metadata (date, GPS, camera info)
    3. Reverse geocode GPS to city/state/country
    4. Find or create location-based album
    5. Save photo and thumbnail to storage
    6. Create database record

    Args:
        file: Uploaded file
        db: Database session
        current_user: Authenticated user

    Returns:
        PhotoUploadResponse with photo details and assigned album
    """
    # Read file data
    file_data = await file.read()
    file_size = len(file_data)

    # Validate image
    if not photo_service.validate_image(file_data):
        raise_bad_request("Invalid image file. Supported formats: JPEG, PNG, GIF, WEBP")

    # Check file size against configuration
    if file_size > settings.max_photo_size_bytes:
        raise_bad_request(
            f"File size too large. Maximum {settings.max_photo_size_mb}MB allowed."
        )

    # Extract EXIF metadata
    metadata = await asyncio.to_thread(photo_service.extract_exif_data, file_data)

    # Reverse geocode GPS coordinates if available
    city = None
    state = None
    country = None
    if metadata.latitude and metadata.longitude:
        location_info = await location_service.reverse_geocode(
            metadata.latitude, metadata.longitude
        )
        city = location_info.city
        state = location_info.state
        country = location_info.country

    # Save photo to storage
    file_path = await storage_service.save_photo(
        user_id=str(current_user.id),
        filename=file.filename,
        file_data=file_data,
        capture_date=metadata.capture_date,
    )

    # Create and save thumbnail
    thumbnail_data = await photo_service.create_thumbnail(file_data)
    thumbnail_path = await storage_service.save_thumbnail(
        user_id=str(current_user.id),
        original_path=file_path,
        thumbnail_data=thumbnail_data,
    )

    # Find or create location-based album
    album = None
    if location_service.should_create_location_album(city):
        album_name = location_service.format_location_name(city, state, country)

        # Check if album exists
        album_query = select(Album).where(
            and_(Album.owner_id == current_user.id, Album.name == album_name)
        )
        result = await db.execute(album_query)
        album = result.scalar_one_or_none()

        # Create album if it doesn't exist
        if not album:
            album = Album(
                owner_id=current_user.id,
                name=album_name,
                type="location",
                photo_count=0,
            )
            db.add(album)
            try:
                await db.flush()  # Get album ID
            except IntegrityError:
                # Another request likely created the album concurrently
                await db.rollback()
                result = await db.execute(album_query)
                album = result.scalar_one_or_none()
                if not album:
                    raise_conflict("Could not create location album. Please retry.")

    # Create photo record
    photo = Photo(
        owner_id=current_user.id,
        album_id=album.id if album else None,
        filename=file.filename,
        file_path=file_path,
        thumbnail_path=thumbnail_path,
        file_size=file_size,
        mime_type=photo_service.get_mime_type(file_data),
        width=metadata.width,
        height=metadata.height,
        capture_date=metadata.capture_date,
        latitude=metadata.latitude,
        longitude=metadata.longitude,
        city=city,
        state=state,
        country=country,
        camera_make=metadata.camera_make,
        camera_model=metadata.camera_model,
    )

    db.add(photo)
    await db.flush()

    # Update album photo count and cover photo
    if album:
        album.photo_count += 1
        if not album.cover_photo_id:
            album.cover_photo_id = photo.id

    await db.commit()
    await db.refresh(photo)
    if album:
        await db.refresh(album)

    return PhotoUploadResponse(
        photo=PhotoResponse.model_validate(photo),
        album=AlbumResponse.model_validate(album) if album else None,
        message="Photo uploaded successfully",
    )


@router.get(
    "",
    response_model=PhotoListResponse,
    summary="List Photos",
    description="Get paginated list of photos with optional filtering",
)
async def list_photos(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    album_id: Optional[UUID] = Query(None, description="Filter by album"),
    city: Optional[str] = Query(None, description="Filter by city"),
    year: Optional[int] = Query(None, ge=1900, description="Filter by year"),
    month: Optional[int] = Query(None, ge=1, le=12, description="Filter by month"),
) -> PhotoListResponse:
    """
    List photos with pagination and filtering.

    Args:
        db: Database session
        current_user: Authenticated user
        page: Page number (1-indexed)
        page_size: Number of items per page
        album_id: Filter by album ID
        city: Filter by city name
        year: Filter by capture year
        month: Filter by capture month

    Returns:
        PhotoListResponse: Paginated photo list
    """
    # Build base query - only user's own photos
    query = select(Photo).where(Photo.owner_id == current_user.id)

    # Apply filters
    if album_id:
        query = query.where(Photo.album_id == album_id)

    if city:
        query = query.where(Photo.city.ilike(f"%{city}%"))

    if year:
        query = query.where(extract("year", Photo.capture_date) == year)

    if month:
        query = query.where(extract("month", Photo.capture_date) == month)

    # Count total items
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Apply pagination
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)

    # Order by capture date (newest first), fallback to upload date
    query = query.order_by(
        Photo.capture_date.desc().nullsfirst(), Photo.upload_date.desc()
    )

    # Execute query
    result = await db.execute(query)
    photos = result.scalars().all()

    # Calculate pages
    pages = (total + page_size - 1) // page_size

    return PhotoListResponse(
        items=[PhotoResponse.model_validate(p) for p in photos],
        total=total,
        page=page,
        page_size=page_size,
        pages=pages,
    )


@router.get(
    "/{photo_id}",
    response_model=PhotoResponse,
    summary="Get Photo",
    description="Get detailed information about a specific photo",
)
async def get_photo(
    photo_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PhotoResponse:
    """
    Get a single photo by ID.

    Args:
        photo_id: Photo UUID
        db: Database session
        current_user: Authenticated user

    Returns:
        PhotoResponse: Photo details
    """
    query = select(Photo).where(
        and_(Photo.id == photo_id, Photo.owner_id == current_user.id)
    )
    result = await db.execute(query)
    photo = result.scalar_one_or_none()

    if not photo:
        raise_not_found("Photo")

    return PhotoResponse.model_validate(photo)


@router.get(
    "/{photo_id}/file",
    summary="Get Photo File",
    description="Download the original photo file",
)
async def get_photo_file(
    photo_id: UUID,
    thumbnail: bool = Query(False, description="Return thumbnail instead of original"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Download photo file.

    Args:
        photo_id: Photo UUID
        thumbnail: Return thumbnail if True, original if False
        db: Database session
        current_user: Authenticated user

    Returns:
        Photo file bytes with appropriate content type
    """
    query = select(Photo).where(
        and_(Photo.id == photo_id, Photo.owner_id == current_user.id)
    )
    result = await db.execute(query)
    photo = result.scalar_one_or_none()

    if not photo:
        raise_not_found("Photo")

    # Determine which file to serve
    file_path = photo.thumbnail_path if thumbnail else photo.file_path

    if not file_path:
        raise_not_found("File")

    # Read file data
    try:
        file_data = await storage_service.get_photo_data(file_path)
    except Exception:
        raise_server_error("Failed to read photo file")

    # Return file with appropriate content type
    return Response(content=file_data, media_type=photo.mime_type)


@router.delete(
    "/{photo_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Photo",
    description="Delete a photo and its files",
)
async def delete_photo(
    photo_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Delete a photo.

    Args:
        photo_id: Photo UUID
        db: Database session
        current_user: Authenticated user
    """
    query = select(Photo).where(
        and_(Photo.id == photo_id, Photo.owner_id == current_user.id)
    )
    result = await db.execute(query)
    photo = result.scalar_one_or_none()

    if not photo:
        raise_not_found("Photo")

    # Get album for count update
    album = None
    if photo.album_id:
        album_query = select(Album).where(Album.id == photo.album_id)
        album_result = await db.execute(album_query)
        album = album_result.scalar_one_or_none()

    # Delete files
    await storage_service.delete_photo(photo.file_path)
    if photo.thumbnail_path:
        await storage_service.delete_thumbnail(photo.thumbnail_path)

    # Update album count
    if album:
        album.photo_count = max(0, album.photo_count - 1)
        if album.cover_photo_id == photo.id:
            album.cover_photo_id = None

    # Delete database record
    await db.delete(photo)
    await db.commit()


@router.get(
    "/calendar/{year}/{month}",
    response_model=CalendarMonthResponse,
    summary="Calendar View",
    description="Get photos grouped by date for calendar view",
)
async def get_calendar_month(
    year: int,
    month: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CalendarMonthResponse:
    """
    Get photos for a specific month, grouped by date.

    Args:
        year: Year (YYYY)
        month: Month (1-12)
        db: Database session
        current_user: Authenticated user

    Returns:
        CalendarMonthResponse: Photos grouped by date
    """
    # Validate month
    if month < 1 or month > 12:
        raise_bad_request("Invalid month")

    # Query photos for this month
    query = (
        select(Photo)
        .where(
            and_(
                Photo.owner_id == current_user.id,
                extract("year", Photo.capture_date) == year,
                extract("month", Photo.capture_date) == month,
            )
        )
        .order_by(Photo.capture_date.asc())
    )

    result = await db.execute(query)
    photos = result.scalars().all()

    # Group photos by date
    dates_dict = {}
    for photo in photos:
        if photo.capture_date:
            date_key = photo.capture_date.date()
            if date_key not in dates_dict:
                dates_dict[date_key] = []
            dates_dict[date_key].append(photo)

    # Build response
    date_responses = []
    for date_key, date_photos in dates_dict.items():
        # Get up to 4 preview photos
        preview_photos = date_photos[:4]

        date_responses.append(
            CalendarDateResponse(
                date=datetime.combine(date_key, datetime.min.time()),
                photo_count=len(date_photos),
                preview_photos=[
                    PhotoResponse.model_validate(p) for p in preview_photos
                ],
            )
        )

    return CalendarMonthResponse(
        year=year, month=month, dates=date_responses, total_photos=len(photos)
    )


@router.get(
    "/albums",
    response_model=AlbumListResponse,
    summary="List Albums",
    description="Get list of photo albums",
)
async def list_albums(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    album_type: Optional[str] = Query(None, description="Filter by type: location, date, custom"),
) -> AlbumListResponse:
    """
    List albums with pagination.

    Args:
        db: Database session
        current_user: Authenticated user
        page: Page number
        page_size: Items per page
        album_type: Filter by album type

    Returns:
        AlbumListResponse: List of albums
    """
    query = select(Album).where(Album.owner_id == current_user.id)

    if album_type:
        query = query.where(Album.type == album_type)

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Paginate
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)

    # Order by most recent
    query = query.order_by(Album.updated_at.desc())

    result = await db.execute(query)
    albums = result.scalars().all()

    pages = (total + page_size - 1) // page_size

    return AlbumListResponse(
        items=[AlbumResponse.model_validate(a) for a in albums],
        total=total,
        page=page,
        page_size=page_size,
        pages=pages,
    )
