# Deployment Guide

Comprehensive deployment guide for Tab Organizer across all platforms.

## Prerequisites

- Flutter SDK 3.16+
- Firebase project configured
- Developer accounts for app stores
- Code signing certificates

## Browser Extensions

### Chrome Web Store

1. **Build Extension**
   ```bash
   cd browser-extensions/chrome
   npm install
   npm run build:production
   ```

2. **Create ZIP Archive**
   ```bash
   cd dist
   zip -r tab-organizer-chrome.zip *
   ```

3. **Upload to Chrome Web Store**
   - Go to [Chrome Web Store Developer Dashboard](https://chrome.google.com/webstore/devconsole)
   - Click "New Item"
   - Upload `tab-organizer-chrome.zip`
   - Fill in store listing details
   - Submit for review

### Firefox Add-ons

1. **Build Extension**
   ```bash
   cd browser-extensions/firefox
   npm install
   npm run build:production
   ```

2. **Sign Extension**
   ```bash
   web-ext sign --api-key=$AMO_KEY --api-secret=$AMO_SECRET
   ```

3. **Upload to AMO**
   - Go to [Firefox Add-ons Developer Hub](https://addons.mozilla.org/developers/)
   - Click "Submit New Add-on"
   - Upload signed XPI file
   - Submit for review

### Edge Add-ons

1. **Build Extension**
   ```bash
   cd browser-extensions/edge
   npm install
   npm run build:production
   ```

2. **Upload to Microsoft Partner Center**
   - Go to [Microsoft Partner Center](https://partner.microsoft.com/dashboard)
   - Click "New submission"
   - Upload extension package
   - Submit for review

## Mobile Apps

### Android (Google Play)

1. **Build APK/AAB**
   ```bash
   cd mobile-app
   flutter build appbundle --release
   ```

2. **Sign App**
   - Already signed with keystore during build

3. **Upload to Google Play Console**
   - Go to [Google Play Console](https://play.google.com/console)
   - Create new release
   - Upload AAB file
   - Fill in release notes
   - Submit for review

### iOS (App Store)

Coming soon - requires iOS implementation.

## Desktop Apps

### Windows (Microsoft Store)

1. **Build MSIX**
   ```bash
   cd mobile-app
   flutter build windows --release
   flutter pub run msix:create
   ```

2. **Upload to Microsoft Store**
   - Go to Microsoft Partner Center
   - Create new app submission
   - Upload MSIX package
   - Submit for review

### macOS (App Store)

1. **Build macOS App**
   ```bash
   cd mobile-app
   flutter build macos --release
   ```

2. **Sign and Notarize**
   ```bash
   codesign --deep --force --verify --verbose \
     --sign "Developer ID Application: YOUR_NAME" \
     build/macos/Build/Products/Release/TabOrganizer.app

   xcrun notarytool submit \
     build/macos/Build/Products/Release/TabOrganizer.app.zip \
     --keychain-profile "AC_PASSWORD"
   ```

3. **Upload to App Store**
   - Open Xcode
   - Archive app
   - Distribute to App Store
   - Submit for review

## Backend Services

### Firebase

1. **Deploy Firestore Rules**
   ```bash
   firebase deploy --only firestore:rules
   ```

2. **Deploy Cloud Functions**
   ```bash
   cd backend
   firebase deploy --only functions
   ```

3. **Deploy Hosting** (if applicable)
   ```bash
   firebase deploy --only hosting
   ```

## CI/CD

### GitHub Actions

See `.github/workflows/` for automated deployment workflows:

- `deploy-extensions.yml` - Deploy browser extensions
- `deploy-android.yml` - Deploy Android app
- `deploy-windows.yml` - Deploy Windows app
- `deploy-macos.yml` - Deploy macOS app

## Monitoring

- Firebase Console: https://console.firebase.google.com
- Google Play Console: https://play.google.com/console
- Chrome Web Store Dashboard: https://chrome.google.com/webstore/devconsole
- Firefox Add-ons Dashboard: https://addons.mozilla.org/developers/

## Rollback Procedures

If issues are detected post-deployment:

1. **Extensions**: Submit hotfix version immediately
2. **Mobile Apps**: Roll back to previous version in store console
3. **Backend**: `firebase deploy --only functions` with previous version

## Support

For deployment issues, contact: support@taborganizer.app
