---
title: ElderPhoto - Elderly-Friendly Photo Management System
description: ElderPhoto is a Google Photos/iCloud-style photo management application specifically designed for elderly users. It features large, clear UI elements, automatic organization by location, and intuitive
tags: [documentation, portfolio]
path: portfolio/general/elderphoto-readme
created: 2026-03-08T22:19:14.061569+00:00
updated: 2026-03-08T22:04:37.773902+00:00
---

# ElderPhoto - Elderly-Friendly Photo Management System

## Overview

ElderPhoto is a Google Photos/iCloud-style photo management application specifically designed for elderly users. It features large, clear UI elements, automatic organization by location, and intuitive navigation inspired by Windows XP.

## Key Features

### 🎯 Elderly-Friendly Design
- **Large Touch Targets**: Minimum 48x48px buttons (up to 60px)
- **Clear Text Labels**: 18-24px fonts, no icon-only buttons
- **High Contrast**: WCAG AAA compliant color schemes
- **Simple Navigation**: Windows XP-style folder hierarchy
- **Keyboard Accessible**: Tab navigation with visible focus indicators

### 📸 Photo Management
- **Automatic Organization**: Photos auto-organized by location (city-based albums)
- **EXIF Metadata**: Extracts date, GPS, camera info from photos
- **Smart Albums**: Location-based albums created automatically (e.g., "San Francisco, CA")
- **Large Thumbnails**: 240x240px thumbnails for easy viewing
- **Multiple Upload**: Drag-and-drop or file picker with progress indication

### 📅 Calendar View
- **Date-Based Discovery**: Find photos by the date they were taken
- **Photo Counts**: See how many photos were taken each day
- **Preview Thumbnails**: Hover over dates to see photo previews
- **Month Navigation**: Easy navigation between months and years

### 📂 Location Organization
- **GPS Reverse Geocoding**: Converts GPS coordinates to city names
- **Auto-Created Albums**: Albums like "New York, NY" or "Paris, France"
- **Folder Tree**: Expandable/collapsible folder navigation
- **Photo Counts**: Shows number of photos in each location

## Architecture

### Backend (FastAPI + Python)

#### Database Schema
```
photos
├── id (uuid)
├── owner_id (fk → users.id)
├── album_id (fk → albums.id)
├── filename, file_path, thumbnail_path
├── file_size, mime_type
├── width, height
├── capture_date, upload_date
├── latitude, longitude (GPS)
├── city, state, country (geocoded)
└── camera_make, camera_model

albums
├── id (uuid)
├── owner_id (fk → users.id)
├── name (e.g., "San Francisco, CA")
├── type (location | date | custom)
├── photo_count
└── cover_photo_id
```

#### Services
- **photo_service.py**: EXIF extraction, thumbnail generation, validation
- **location_service.py**: GPS reverse geocoding (Nominatim/OpenStreetMap)
- **storage_service.py**: File storage organized by user/date

#### API Endpoints
```
POST   /photos/upload              - Upload photo with EXIF extraction
GET    /photos                     - List photos (filterable)
GET    /photos/{id}                - Get photo details
GET    /photos/{id}/file           - Download photo/thumbnail
DELETE /photos/{id}                - Delete photo
GET    /photos/calendar/{y}/{m}    - Calendar view with counts
GET    /photos/albums              - List albums
```

### Frontend (React + TypeScript)

#### Component Structure
```
src/
├── components/
│   ├── elderly/              # Accessibility components
│   │   ├── LargeButton.tsx   # Large touch-target buttons
│   │   └── SidebarNav.tsx    # Windows XP-style navigation
│   └── photos/               # Photo-specific components
│       ├── PhotoGrid.tsx     # Grid view with large thumbnails
│       ├── PhotoUpload.tsx   # Drag-and-drop upload
│       └── PhotoCalendar.tsx # Calendar with photo counts
├── pages/
│   └── Photos/
│       └── PhotosPage.tsx    # Main photo management page
└── api/
    ├── types.ts              # TypeScript interfaces
    └── services.ts           # API service functions
```

#### Design System
- **Colors**: Deep blue primary (#1e3a8a) with 7.2:1 contrast against white text
- **Typography**: 18px base, 24px+ headings, semibold weights
- **Spacing**: Generous padding (12-24px)
- **Borders**: 2-4px for visibility
- **Focus Rings**: 4px blue outline with 2px offset

## Installation & Setup

### Prerequisites
- Node.js 18+
- Python 3.11+
- PostgreSQL 15+

### Backend Setup
```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your database credentials

# Run migrations
alembic upgrade head

# Start server
uvicorn app.main:app --reload --port 8000
```

### Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

### Environment Variables

#### Backend (.env)
```
DATABASE_URL=postgresql://user:pass@localhost:5432/elderphoto
SECRET_KEY=your-secret-key-here
PHOTO_STORAGE_PATH=/path/to/photo/storage
```

#### Frontend (.env)
```
VITE_API_URL=http://localhost:8000
```

## Usage Guide

### For Elderly Users

#### Uploading Photos
1. Click "Upload Photos" in the sidebar
2. Either:
   - Drag photos from your computer to the upload area
   - Click "Choose Photos" button to select files
3. Photos are automatically organized by location

#### Finding Photos
1. **By Location**: Click "By Location" in sidebar, then select a city
2. **By Date**: Click "Calendar" to see photos by date
3. **All Photos**: Click "All Photos" to see everything

#### Viewing Photos
- Photos displayed in large, clear grid
- Date and location shown below each photo
- Click any photo to see it larger (future feature)

### For Developers

#### Adding New Photo Services
```python
# backend/app/services/photo_service.py
def extract_exif_data(image_data: bytes) -> PhotoMetadata:
    # Add custom EXIF parsing logic
    pass
```

#### Customizing UI Components
```tsx
// frontend/src/components/elderly/LargeButton.tsx
<LargeButton
  variant="primary"      // primary | secondary | danger | success
  size="large"          // medium | large
  icon="📷"             // Optional emoji icon
  onClick={handleClick}
>
  Button Text
</LargeButton>
```

## Technical Specifications

### Image Processing
- **Supported Formats**: JPEG, PNG, GIF, WEBP
- **Max File Size**: 20MB per photo
- **Thumbnail Size**: 400x400px
- **Thumbnail Quality**: 85% JPEG compression

### Geocoding
- **Provider**: Nominatim (OpenStreetMap)
- **Rate Limit**: 1 request/second (compliant)
- **Timeout**: 5 seconds per request
- **Fallback**: "Unknown Location" if geocoding fails

### Performance
- **Lazy Loading**: Images loaded as you scroll
- **Thumbnail First**: Shows thumbnail, loads full on click
- **Pagination**: 20 photos per page by default
- **Caching**: Browser caching for thumbnails

### Accessibility (WCAG AAA)
- **Color Contrast**: 7:1 for normal text (primary #1e3a8a on white), 4.5:1 for large text
- **Keyboard Navigation**: Full keyboard support
- **Screen Readers**: ARIA labels on all interactive elements
- **Focus Indicators**: 4px visible focus rings
- **Text Scaling**: Supports browser zoom up to 200%

## Roadmap

### Phase 1 (Completed ✅)
- ✅ Backend API with EXIF extraction
- ✅ Location-based auto-organization
- ✅ Calendar view
- ✅ Upload interface
- ✅ Elderly-friendly UI components

### Phase 2 (Future)
- ⏳ Photo editing (rotate, crop, brightness)
- ⏳ Photo detail modal with full-screen view
- ⏳ Timeline scrolling by month/year
- ⏳ Search functionality (by location, date range)
- ⏳ Favorites/starred photos

### Phase 3 (Future)
- ⏳ Sharing albums with family members
- ⏳ Print ordering integration
- ⏳ Slideshow mode
- ⏳ Import from Google Photos/iCloud
- ⏳ Facial recognition (optional, privacy-respecting)

## Privacy & Security

- **User Data**: Photos stored locally on server (not cloud by default)
- **Authentication**: JWT-based with bcrypt password hashing
- **File Isolation**: Each user has separate storage directory
- **EXIF Privacy**: GPS data only used for organization, not shared
- **GDPR Compliant**: User can delete all photos and data

## Testing

### Backend Tests
```bash
cd backend
pytest tests/test_photos.py
pytest --cov=app tests/
```

### Frontend Tests
```bash
cd frontend
npm test
npm run test:coverage
```

## Contributing

This is a portfolio project demonstrating:
- Elderly-friendly UX design
- Full-stack development (FastAPI + React)
- EXIF metadata processing
- Location-based organization
- Accessible UI components

## License

MIT License - Free to use and modify

## Support

For issues or questions about this portfolio project:
- GitHub Issues: [Your Repo URL]
- Email: [Your Email]

## Credits

- **Icons**: Emoji (universally recognized)
- **Geocoding**: Nominatim (OpenStreetMap)
- **Image Processing**: Pillow (PIL)
- **Calendar**: react-calendar
- **Design Inspiration**: Windows XP, Google Photos

---

Built with ❤️ for accessibility and ease of use
