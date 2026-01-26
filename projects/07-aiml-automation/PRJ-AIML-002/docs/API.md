# API Documentation

## Native Messaging Protocol

### Browser Extension → Native Host

#### Connect
```json
{
  "type": "connect",
  "timestamp": 1234567890
}
```

#### Tabs Update
```json
{
  "type": "tabs_update",
  "tabs": [
    {
      "id": "123",
      "url": "https://example.com",
      "title": "Example Page",
      "favIconUrl": "https://example.com/favicon.ico",
      "windowId": 1,
      "index": 0,
      "active": true,
      "pinned": false
    }
  ],
  "timestamp": 1234567890
}
```

#### Tab Closed
```json
{
  "type": "tab_closed",
  "tabId": "123",
  "timestamp": 1234567890
}
```

#### Organize Request
```json
{
  "type": "organize_request",
  "timestamp": 1234567890
}
```

### Native Host → Browser Extension

#### Connected
```json
{
  "type": "connected",
  "status": "ok",
  "timestamp": 1234567890
}
```

#### Organize Response
```json
{
  "type": "organize_request",
  "groups": [
    {
      "name": "Work - LinkedIn",
      "tabIds": ["123", "456"],
      "color": "blue",
      "category": "work"
    }
  ]
}
```

#### Close Tab
```json
{
  "type": "close_tab",
  "tabId": "123"
}
```

#### Focus Tab
```json
{
  "type": "focus_tab",
  "tabId": "123"
}
```

#### Group Tabs
```json
{
  "type": "group_tabs",
  "tabIds": ["123", "456", "789"],
  "groupName": "Research Papers",
  "color": "purple"
}
```

## Firebase API

### Collections Structure

```
/users/{userId}
  /profile
    - email: string
    - displayName: string
    - createdAt: timestamp
    - settings: map

  /devices/{deviceId}
    - deviceName: string
    - platform: string
    - lastSynced: timestamp
    - encryptionPublicKey: string

  /tabGroups/{groupId}
    - name: string
    - category: string
    - color: number
    - createdAt: timestamp
    - updatedAt: timestamp
    - encryptedData: string

    /tabs/{tabId}
      - url: string
      - title: string
      - favicon: string
      - lastAccessed: timestamp
      - metadata: map

  /syncQueue/{syncId}
    - operation: string (create|update|delete)
    - timestamp: timestamp
    - data: map
```

### Security Rules

- Users can only access their own data
- All reads/writes require authentication
- Encryption keys are never stored on server
- Zero-knowledge architecture

## ML Model API

### Classification

**Input:**
```dart
Tab tab = Tab(
  id: '1',
  url: 'https://example.com',
  title: 'Example Page',
  description: 'Page description',
  createdAt: DateTime.now(),
);
```

**Output:**
```dart
ClassificationResult result = await classifier.classifyTab(tab);

// Result properties:
result.category         // TabCategory enum
result.confidence       // double (0.0 - 1.0)
result.probabilities    // Map<TabCategory, double>
result.inferenceTimeMs  // int
```

### Batch Classification

```dart
List<Tab> tabs = [...];
List<ClassificationResult> results = await classifier.classifyBatch(tabs);
```

## WebSocket API (Native Host ↔ Flutter App)

### Connection
```
ws://localhost:8765
```

### Message Format
All messages are JSON-encoded.

### Example Messages

**From Native Host:**
```json
{
  "type": "tabs_update",
  "tabs": [...]
}
```

**From Flutter App:**
```json
{
  "type": "organize_request",
  "groups": [...]
}
```

## Error Handling

All APIs use standard error codes:

- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `500` - Internal Server Error

Error response format:
```json
{
  "error": {
    "code": "invalid_request",
    "message": "Detailed error message",
    "timestamp": 1234567890
  }
}
```
