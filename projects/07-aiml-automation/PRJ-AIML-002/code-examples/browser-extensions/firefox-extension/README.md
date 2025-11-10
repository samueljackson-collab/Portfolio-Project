# Tab Organizer - Firefox Extension

## Important Notes

### Tab Grouping Limitation

**Firefox does not support the `tabGroups` API** that is available in Chrome/Edge. This means:

- ❌ Native tab groups cannot be created in Firefox
- ❌ Auto-grouping in the browser is not available
- ✅ Tabs are still tracked and classified by the Flutter app
- ✅ Virtual groups are managed in the Flutter app
- ✅ All other features work normally

### Workarounds

The extension will:
1. Track all tab changes and send them to the Flutter app
2. Allow the Flutter app to manage virtual groups
3. Provide UI in the popup for manual organization
4. Sync tab state across devices via Firebase

### Compatibility

- **Manifest Version**: 2 (required for Firefox)
- **Minimum Firefox Version**: 78.0
- **Tested On**: Firefox 115+

### Installation

#### Development Mode
1. Open Firefox
2. Go to `about:debugging#/runtime/this-firefox`
3. Click "Load Temporary Add-on"
4. Select `manifest.json` from this directory

#### Production
Extension will be published to Firefox Add-ons store after testing.

### Feature Comparison

| Feature | Chrome/Edge | Firefox |
|---------|-------------|---------|
| Tab tracking | ✅ | ✅ |
| AI classification | ✅ | ✅ |
| Content analysis | ✅ | ✅ |
| Native tab groups | ✅ | ❌ |
| Virtual groups (in app) | ✅ | ✅ |
| Cloud sync | ✅ | ✅ |
| Native messaging | ✅ | ✅ |

### Future Improvements

When Firefox adds tab grouping support, the extension will be updated to include:
- Native tab group creation
- Auto-grouping in browser
- Visual group indicators

### Known Issues

1. Tab grouping commands will be ignored in Firefox
2. `CREATE_GROUP` message type returns an error
3. Auto-group feature works only in the Flutter app, not in browser

## Development

To make the extension cross-compatible:

```javascript
// Check if tabGroups API is available
if (typeof chrome.tabGroups !== 'undefined') {
  // Chrome/Edge: Use native tab groups
  await chrome.tabGroups.update(groupId, { ... });
} else {
  // Firefox: Handle in Flutter app only
  console.warn('Tab groups not supported in this browser');
}
```

## Support

For issues specific to Firefox, please file a bug report and include:
- Firefox version
- Extension version
- Console errors (if any)
- Steps to reproduce

---

**Note**: This limitation is due to Firefox not implementing the Chrome Tab Groups API. The core functionality of tab organization and AI classification works perfectly in both browsers.
