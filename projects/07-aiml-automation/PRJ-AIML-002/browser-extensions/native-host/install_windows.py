#!/usr/bin/env python3
"""
Install native messaging host for Windows
"""

import os
import sys
import json
import winreg

HOST_NAME = 'com.taborganizer.native_host'
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
HOST_PATH = os.path.join(SCRIPT_DIR, 'native_host.py')


def install_chrome():
    """Install for Chrome"""
    manifest = {
        'name': HOST_NAME,
        'description': 'Tab Organizer Native Messaging Host',
        'path': HOST_PATH,
        'type': 'stdio',
        'allowed_origins': [
            'chrome-extension://EXTENSION_ID_HERE/'
        ]
    }

    manifest_path = os.path.join(SCRIPT_DIR, f'{HOST_NAME}_chrome.json')
    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2)

    # Register in Windows registry
    key_path = r'Software\Google\Chrome\NativeMessagingHosts\{}'.format(HOST_NAME)
    key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path)
    winreg.SetValue(key, '', winreg.REG_SZ, manifest_path)
    winreg.CloseKey(key)

    print(f'Chrome manifest installed at: {manifest_path}')


def install_firefox():
    """Install for Firefox"""
    manifest = {
        'name': HOST_NAME,
        'description': 'Tab Organizer Native Messaging Host',
        'path': HOST_PATH,
        'type': 'stdio',
        'allowed_extensions': [
            'tab-organizer@taborganizer.app'
        ]
    }

    manifest_path = os.path.join(SCRIPT_DIR, f'{HOST_NAME}_firefox.json')
    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2)

    # Register in Windows registry
    key_path = r'Software\Mozilla\NativeMessagingHosts\{}'.format(HOST_NAME)
    key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path)
    winreg.SetValue(key, '', winreg.REG_SZ, manifest_path)
    winreg.CloseKey(key)

    print(f'Firefox manifest installed at: {manifest_path}')


def main():
    print('Installing Tab Organizer native messaging host for Windows...')

    try:
        install_chrome()
        install_firefox()
        print('\nInstallation complete!')
        print('\nNext steps:')
        print('1. Replace EXTENSION_ID_HERE in Chrome manifest with your extension ID')
        print('2. Restart your browser')
        print('3. Test the connection')
    except Exception as e:
        print(f'Installation failed: {e}', file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
