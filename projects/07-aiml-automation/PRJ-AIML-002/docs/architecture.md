# Architecture Documentation

## System Overview

The Tab Organizer is a distributed system consisting of multiple components working together to provide seamless tab management across browsers and platforms.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Browser Extensions                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                 │
│  │  Chrome  │  │ Firefox  │  │   Edge   │                 │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘                 │
│       │             │             │                         │
└───────┼─────────────┼─────────────┼─────────────────────────┘
        │             │             │
        └─────────────┼─────────────┘
                      │
              ┌───────▼────────┐
              │ Native Host    │  (Stdio/JSON)
              │   Bridge       │
              └───────┬────────┘
                      │
        ┌─────────────┼─────────────┐
        │             │             │
┌───────▼──────┐ ┌───▼────┐ ┌─────▼────────┐
│   Flutter    │ │   AI   │ │    Local     │
│     App      │ │ Model  │ │   Storage    │
│   (Main UI)  │ │(TFLite)│ │   (Hive)     │
└───────┬──────┘ └───┬────┘ └─────┬────────┘
        │             │             │
        └─────────────┼─────────────┘
                      │
              ┌───────▼────────┐
              │   Firebase     │
              │  (Cloud Sync)  │
              └────────────────┘
```

## Component Architecture

### 1. Browser Extensions

**Purpose**: Capture tab events and communicate with the native app

**Technologies**:
- Chrome/Edge: Manifest V3
- Firefox: Manifest V2/V3

**Key Files**:
- `manifest.json` - Extension configuration
- `background.js` - Service worker handling tab events
- `popup.js` - Extension UI logic
- `content.js` - Page content analysis

**Responsibilities**:
- Monitor tab creation, updates, and removal
- Capture tab metadata (URL, title, favicon)
- Analyze page content
- Communicate with native messaging host
- Create and manage tab groups

**Communication**:
- Browser API → Background Script
- Background Script → Native Host (JSON over stdio)
- Content Script → Background Script (Message passing)

### 2. Native Messaging Host

**Purpose**: Bridge between browser extensions and Flutter app

**Technology**: Node.js or Dart

**Key Features**:
- Stdin/stdout communication
- JSON message protocol
- Message routing and validation
- Error handling and logging

**Message Protocol**:
```json
{
  "type": "TAB_CREATED",
  "tab": {
    "id": 123,
    "title": "Example",
    "url": "https://example.com",
    "favIconUrl": "...",
    "browser": "chrome"
  },
  "timestamp": "2025-11-10T00:00:00Z"
}
```

### 3. Flutter Application

**Purpose**: Main user interface and business logic

**Architecture**: MVVM (Model-View-ViewModel)

**Layers**:

#### Presentation Layer
- **Screens**: UI pages (HomeScreen, SettingsScreen, etc.)
- **Widgets**: Reusable UI components
- **Providers**: State management (TabProvider, SettingsProvider)

#### Business Logic Layer
- **Services**: Core functionality
  - `TabService`: Tab and group management
  - `AIService`: ML-based classification
  - `SyncService`: Cloud synchronization
  - `NativeMessagingService`: Browser communication

#### Data Layer
- **Models**: Data structures (TabModel, TabGroup)
- **Storage**: Local persistence (Hive)
- **API**: Cloud backend (Firebase)

**State Management**: Provider pattern

**Navigation**: Flutter Router

### 4. AI/ML Model

**Purpose**: Classify tabs into categories

**Framework**: TensorFlow Lite

**Architecture**:
```
Input Layer (15 features)
    ↓
Dense Layer (128 neurons, ReLU)
    ↓
Dropout (0.3)
    ↓
Dense Layer (64 neurons, ReLU)
    ↓
Dropout (0.2)
    ↓
Dense Layer (32 neurons, ReLU)
    ↓
Output Layer (7 categories, Softmax)
```

**Input Features**:
1. Domain pattern matches (6 features)
2. Keyword scores (6 features)
3. URL structure (3 features)

**Output**: Category probabilities (7 classes)

**Model Size**: ~200 KB (optimized)

**Inference Time**: <100ms on device

### 5. Local Storage (Hive)

**Purpose**: Fast local data persistence

**Schema**:

```dart
// Tabs Box
Box<TabModel> tabs
  - id: String (primary key)
  - title: String
  - url: String
  - category: String
  - groupId: String?
  - createdAt: DateTime
  - lastAccessed: DateTime

// Groups Box
Box<TabGroup> groups
  - id: String (primary key)
  - name: String
  - category: String
  - tabIds: List<String>
  - colorHex: String
  - createdAt: DateTime
  - updatedAt: DateTime
```

**Advantages**:
- No SQL required
- Type-safe
- Fast read/write
- Small binary size
- Cross-platform

### 6. Cloud Sync (Firebase)

**Purpose**: Synchronize data across devices

**Services Used**:
- **Firestore**: Data storage
- **Authentication**: User management
- **Cloud Functions**: Backend logic (optional)

**Firestore Structure**:
```
users/
  {userId}/
    tabs/
      {tabId}/
        - id
        - title
        - url
        - category
        - ...
    groups/
      {groupId}/
        - id
        - name
        - category
        - tabIds
        - ...
    metadata/
      sync/
        - lastSync
        - deviceId
```

**Sync Strategy**:
- Periodic sync every 5 minutes
- Real-time listeners for updates
- Conflict resolution: Last-write-wins
- Offline support with local queue

## Data Flow

### Tab Creation Flow

```
1. User opens tab in browser
2. Browser extension detects tab created event
3. Extension serializes tab data
4. Extension sends message to native host
5. Native host forwards to Flutter app
6. Flutter app receives tab data
7. AI service classifies tab
8. Tab service stores tab locally (Hive)
9. Sync service uploads to Firebase (if enabled)
10. UI updates to show new tab
```

### Tab Grouping Flow

```
1. User triggers auto-group action
2. TabProvider requests classification for all tabs
3. AIService processes each tab
4. TabService creates groups by category
5. Groups stored in Hive
6. Browser extension creates native tab groups
7. Firebase sync updates cloud data
8. UI reflects grouped state
```

## Security Architecture

### Data Protection
- Local data encrypted at rest (Hive encryption)
- Cloud data encrypted in transit (HTTPS)
- Optional end-to-end encryption for sensitive data
- No telemetry or tracking

### Privacy Measures
- All tab content processed locally
- ML inference runs on-device
- Cloud sync is optional
- User can export/delete all data

### Authentication
- Firebase Anonymous Auth (default)
- Optional email/password auth
- OAuth support (Google, GitHub)

## Performance Considerations

### Optimization Strategies
1. **Lazy Loading**: Load tabs on-demand
2. **Pagination**: Display tabs in chunks
3. **Caching**: Cache frequently accessed data
4. **Background Processing**: Run ML inference in background
5. **Debouncing**: Throttle sync operations

### Resource Limits
- Max tabs in memory: 1000
- Max tabs per group: 50
- Sync batch size: 100 tabs
- Content analysis limit: 5000 characters

## Scalability

### Horizontal Scaling
- Multiple browser instances supported
- Multiple devices per user
- Cloud backend auto-scales (Firebase)

### Vertical Scaling
- Efficient data structures
- Indexed queries
- Compressed storage
- Optimized ML model

## Deployment Architecture

### Development
```
Local Machine
  - Flutter app (debug mode)
  - Browser extension (unpacked)
  - Local Firebase emulator (optional)
```

### Production
```
User Device
  - Flutter app (release build)
  - Browser extension (published)
  - Firebase production backend
```

## Technology Stack Summary

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Mobile/Desktop App | Flutter 3.x | Cross-platform UI |
| State Management | Provider | Reactive state |
| Local Storage | Hive | NoSQL persistence |
| Cloud Sync | Firebase | Backend services |
| AI/ML | TensorFlow Lite | Tab classification |
| Browser Extensions | JavaScript | Browser integration |
| Native Messaging | Dart/Node.js | Extension-app bridge |

## API Endpoints

### Browser Extension ↔ Native Host

```javascript
// Request types
GET_TABS
GET_ACTIVE_TAB
CREATE_TAB_GROUP
CLOSE_TAB
FOCUS_TAB
UPDATE_TAB
PING

// Event types
TAB_CREATED
TAB_UPDATED
TAB_REMOVED
TAB_ACTIVATED
WINDOW_FOCUS_CHANGED
PAGE_ANALYZED
```

### Flutter App ↔ Firebase

```
// Firestore Collections
/users/{userId}/tabs
/users/{userId}/groups
/users/{userId}/metadata

// Authentication
signInAnonymously()
signInWithEmailPassword()
signOut()
```

## Monitoring & Observability

### Metrics
- Tab count per category
- Classification accuracy
- Sync success rate
- Error rates
- Performance metrics (load time, inference time)

### Logging
- Application logs (debug, info, warning, error)
- Crash reports
- Usage analytics (opt-in)

### Error Handling
- Try-catch blocks around critical operations
- Graceful degradation (fallback to pattern matching if ML fails)
- User-friendly error messages
- Retry logic with exponential backoff

## Future Enhancements

### Planned Features
1. Collaborative workspaces
2. Tab sharing and collections
3. Browser history integration
4. Reading mode
5. Voice commands
6. Integration with productivity tools

### Architecture Evolution
1. Microservices backend (replacing Firebase)
2. GraphQL API
3. WebSocket for real-time updates
4. Edge computing for ML inference
5. Federated learning for model improvement

---

**Last Updated**: 2025-11-10
**Version**: 1.0.0
**Author**: Samuel Jackson
