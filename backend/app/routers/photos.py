"""Photo management endpoints for ElderPhoto."""

from __future__ import annotations

import asyncio
from datetime import datetime
from pathlib import Path
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy import and_, func, select
from sqlalchemy.exc import IntegrityError

from app import schemas
from app.config import settings
from app.dependencies import CurrentUser, DatabaseSession
from app.models import Album, Photo
from app.services import photo_service, storage_service
from app.services.location_service import location_service

router = APIRouter(prefix="/photos", tags=["Photos"])


async def _get_photo(db: DatabaseSession, owner_id: UUID, photo_id: UUID) -> Photo:
    stmt = select(Photo).where(and_(Photo.id == photo_id, Photo.owner_id == owner_id))
    result = await db.execute(stmt)
    photo = result.scalar_one_or_none()
    if not photo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Photo not found")
    return photo


def _to_photo_response(photo: Photo) -> schemas.PhotoResponse:
    response = schemas.PhotoResponse.model_validate(photo)
    response.file_url = f"/photos/{photo.id}/file"
    if photo.thumbnail_path:
        response.thumbnail_url = f"/photos/{photo.id}/file?thumbnail=true"
    return response


async def _get_or_create_location_album(db: DatabaseSession, owner_id: UUID, name: str) -> Album:
    stmt = select(Album).where(and_(Album.owner_id == owner_id, Album.name == name))
    result = await db.execute(stmt)
    album = result.scalar_one_or_none()
    if album:
        return album

    album = Album(owner_id=owner_id, name=name, type="location", photo_count=0)
    db.add(album)
    try:
        await db.flush()
        return album
    except IntegrityError:
        await db.rollback()
        result = await db.execute(stmt)
        existing = result.scalar_one()
        return existing


@router.get("/albums", response_model=schemas.AlbumListResponse)
async def list_albums(current_user: CurrentUser = Depends(), db: DatabaseSession = Depends()):
    stmt = select(Album).where(Album.owner_id == current_user.id).order_by(Album.created_at.desc())
    result = await db.execute(stmt)
    albums = result.scalars().all()
    return schemas.AlbumListResponse(items=albums)


@router.post(
    "/upload",
    response_model=schemas.PhotoUploadResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_photo(
    file: UploadFile = File(...),
    current_user: CurrentUser = Depends(),
    db: DatabaseSession = Depends(),
):
    file_data = await file.read()
    file_size = len(file_data)
    if file_size == 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Empty file")
    if file_size > settings.max_photo_size_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File size too large. Maximum {settings.max_photo_size_bytes // 1024 // 1024}MB allowed.",
        )

    metadata = await asyncio.to_thread(photo_service.extract_exif_data, file_data)
    mime_type = metadata.mime_type or file.content_type or "application/octet-stream"
    if not mime_type.startswith("image/"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported file type")

    location = await location_service.reverse_geocode(metadata.latitude, metadata.longitude)
    album: Optional[Album] = None
    if location_service.should_create_location_album(location.city if location else None):
        album_name = location_service.format_location_name(
            location.city if location else None,
            location.state if location else None,
            location.country if location else None,
        )
        album = await _get_or_create_location_album(db, current_user.id, album_name)

    file_path = await storage_service.save_photo_bytes(current_user.id, metadata.capture_date, file.filename, file_data)
    thumbnail_path: Optional[str] = None
    try:
        thumbnail_bytes = await photo_service.create_thumbnail(file_data)
        thumbnail_path = await storage_service.save_thumbnail_bytes(
            current_user.id,
            metadata.capture_date,
            file.filename,
            thumbnail_bytes,
        )
    except Exception:
        thumbnail_path = None

    photo = Photo(
        owner_id=current_user.id,
        album_id=album.id if album else None,
        file_name=file.filename,
        mime_type=mime_type,
        file_size=file_size,
        width=metadata.width,
        height=metadata.height,
        capture_date=metadata.capture_date,
        camera_make=metadata.camera_make,
        camera_model=metadata.camera_model,
        focal_length=metadata.focal_length,
        aperture=metadata.aperture,
        iso=metadata.iso,
        latitude=metadata.latitude,
        longitude=metadata.longitude,
        location_name=location.display_name if location else None,
        city=location.city if location else None,
        state=location.state if location else None,
        country=location.country if location else None,
        storage_path=file_path,
        thumbnail_path=thumbnail_path,
    )
    db.add(photo)
    await db.flush()

    if album:
        album.photo_count += 1
        if not album.cover_photo_id:
            album.cover_photo_id = photo.id

    base = _to_photo_response(photo)
    return schemas.PhotoUploadResponse(**base.model_dump(), message="Photo uploaded successfully")


@router.get("", response_model=schemas.PhotoListResponse)
async def list_photos(
    skip: int = Query(0, ge=0),
    limit: int = Query(25, ge=1, le=100),
    album_id: Optional[UUID] = Query(None),
    current_user: CurrentUser = Depends(),
    db: DatabaseSession = Depends(),
):
    filters = [Photo.owner_id == current_user.id]
    if album_id:
        filters.append(Photo.album_id == album_id)

    stmt = (
        select(Photo)
        .where(*filters)
        .order_by(Photo.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(stmt)
    photos = result.scalars().all()

    count_stmt = select(func.count()).select_from(Photo).where(*filters)
    total = (await db.execute(count_stmt)).scalar_one()

    return schemas.PhotoListResponse(
        items=[_to_photo_response(photo) for photo in photos],
        total=total,
    )


@router.get("/{photo_id}", response_model=schemas.PhotoResponse)
async def get_photo(photo_id: UUID, current_user: CurrentUser = Depends(), db: DatabaseSession = Depends()):
    photo = await _get_photo(db, current_user.id, photo_id)
    return _to_photo_response(photo)


@router.delete("/{photo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_photo(photo_id: UUID, current_user: CurrentUser = Depends(), db: DatabaseSession = Depends()):
    photo = await _get_photo(db, current_user.id, photo_id)
    album_id = photo.album_id
    await storage_service.delete_file(photo.storage_path)
    await storage_service.delete_file(photo.thumbnail_path)
    await db.delete(photo)

    if album_id:
        stmt = select(Album).where(and_(Album.id == album_id, Album.owner_id == current_user.id))
        result = await db.execute(stmt)
        album = result.scalar_one_or_none()
        if album and album.photo_count > 0:
            album.photo_count -= 1
            if album.cover_photo_id == photo.id:
                cover_stmt = (
                    select(Photo.id)
                    .where(and_(Photo.owner_id == current_user.id, Photo.album_id == album_id))
                    .order_by(Photo.created_at.desc())
                    .limit(1)
                )
                cover_result = await db.execute(cover_stmt)
                album.cover_photo_id = cover_result.scalar_one_or_none()


@router.get("/{photo_id}/file")
async def get_photo_file(
    photo_id: UUID,
    thumbnail: bool = Query(False),
    current_user: CurrentUser = Depends(),
    db: DatabaseSession = Depends(),
):
    photo = await _get_photo(db, current_user.id, photo_id)
    path = Path(photo.thumbnail_path if thumbnail and photo.thumbnail_path else photo.storage_path)
    if not path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")

    media_type = "image/jpeg" if thumbnail and photo.thumbnail_path else photo.mime_type
    return FileResponse(path, media_type=media_type)


@router.get("/calendar", response_model=schemas.CalendarMonthResponse)
async def calendar_view(
    year: int = Query(..., ge=1970),
    month: int = Query(..., ge=1, le=12),
    current_user: CurrentUser = Depends(),
    db: DatabaseSession = Depends(),
):
    start = datetime(year, month, 1)
    end = datetime(year + 1, 1, 1) if month == 12 else datetime(year, month + 1, 1)

    counts_stmt = (
        select(func.date(Photo.capture_date).label("day"), func.count(Photo.id))
        .where(
            Photo.owner_id == current_user.id,
            Photo.capture_date.isnot(None),
            Photo.capture_date >= start,
            Photo.capture_date < end,
        )
        .group_by(func.date(Photo.capture_date))
        .order_by(func.date(Photo.capture_date))
    )
    counts = await db.execute(counts_stmt)
    count_rows = counts.all()

    preview_stmt = (
        select(Photo)
        .where(
            Photo.owner_id == current_user.id,
            Photo.capture_date.isnot(None),
            Photo.capture_date >= start,
            Photo.capture_date < end,
        )
        .order_by(Photo.capture_date.asc())
    )
    preview_result = await db.execute(preview_stmt)
    preview_photos = preview_result.scalars().all()

    preview_map: dict[str, list[schemas.PhotoResponse]] = {}
    for photo in preview_photos:
        if not photo.capture_date:
            continue
        key = photo.capture_date.date().isoformat()
        preview_map.setdefault(key, [])
        if len(preview_map[key]) < 3:
            preview_map[key].append(_to_photo_response(photo))

    dates = []
    total = 0
    for day, count in count_rows:
        total += count
        key = day.isoformat()
        dates.append(
            schemas.CalendarDateResponse(
                date=datetime.fromisoformat(key),
                photo_count=count,
                preview_photos=preview_map.get(key, []),
            )
        )

    return schemas.CalendarMonthResponse(total_photos=total, dates=dates)
