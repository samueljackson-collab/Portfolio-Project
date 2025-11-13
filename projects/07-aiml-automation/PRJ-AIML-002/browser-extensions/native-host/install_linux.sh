#!/bin/bash
# Install native messaging host for Linux

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
HOST_NAME="com.taborganizer.native_host"
CHROME_DIR="$HOME/.config/google-chrome/NativeMessagingHosts"
FIREFOX_DIR="$HOME/.mozilla/native-messaging-hosts"

echo "Installing Tab Organizer native messaging host..."

# Make native_host.py executable
chmod +x "$SCRIPT_DIR/native_host.py"

# Create manifest for Chrome
mkdir -p "$CHROME_DIR"
cat > "$CHROME_DIR/$HOST_NAME.json" << EOF
{
  "name": "$HOST_NAME",
  "description": "Tab Organizer Native Messaging Host",
  "path": "$SCRIPT_DIR/native_host.py",
  "type": "stdio",
  "allowed_origins": [
    "chrome-extension://EXTENSION_ID_HERE/"
  ]
}
EOF

echo "Chrome manifest created at: $CHROME_DIR/$HOST_NAME.json"

# Create manifest for Firefox
mkdir -p "$FIREFOX_DIR"
cat > "$FIREFOX_DIR/$HOST_NAME.json" << EOF
{
  "name": "$HOST_NAME",
  "description": "Tab Organizer Native Messaging Host",
  "path": "$SCRIPT_DIR/native_host.py",
  "type": "stdio",
  "allowed_extensions": [
    "tab-organizer@taborganizer.app"
  ]
}
EOF

echo "Firefox manifest created at: $FIREFOX_DIR/$HOST_NAME.json"

echo "Installation complete!"
echo ""
echo "Next steps:"
echo "1. Replace EXTENSION_ID_HERE in Chrome manifest with your extension ID"
echo "2. Restart your browser"
echo "3. Test the connection"
