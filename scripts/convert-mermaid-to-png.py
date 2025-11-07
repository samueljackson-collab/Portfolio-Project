#!/usr/bin/env python3
"""
Mermaid to PNG Converter
========================
Converts all Mermaid diagram files (.mmd, .mermaid) to PNG images using mermaid.ink API

Usage:
    python3 convert-mermaid-to-png.py [directory]

If no directory is specified, searches entire Portfolio-Project
"""

import base64
import os
import sys
import urllib.request
import urllib.parse
from pathlib import Path
import zlib

def find_mermaid_files(root_dir):
    """Find all .mmd and .mermaid files in the directory tree"""
    mermaid_files = []
    root_path = Path(root_dir)

    # Find .mmd files
    mermaid_files.extend(root_path.rglob("*.mmd"))
    # Find .mermaid files
    mermaid_files.extend(root_path.rglob("*.mermaid"))

    return sorted(mermaid_files)

def encode_mermaid(mermaid_code):
    """
    Prepare Mermaid diagram source for use with the mermaid.ink API by trimming, compressing, and URL-safe Base64-encoding the content.
    
    Parameters:
        mermaid_code (str): Mermaid diagram source text.
    
    Returns:
        encoded (str): URL-safe Base64 string of the compressed Mermaid source suitable for appending to a mermaid.ink API URL.
    """
    # Remove any leading/trailing whitespace
    mermaid_code = mermaid_code.strip()

    # Encode to bytes
    encoded = mermaid_code.encode('utf-8')

    # Compress with zlib
    compressed = zlib.compress(encoded, level=9)

    # Base64 encode
    b64 = base64.urlsafe_b64encode(compressed).decode('utf-8')

    return b64

def convert_to_png(mermaid_file, output_file):
    """
    Convert a Mermaid source file into a PNG image using the mermaid.ink API.
    
    Reads the Mermaid text from `mermaid_file`, requests a rendered PNG from mermaid.ink, writes the result to `output_file`, and performs a basic size check to detect error responses.
    
    Parameters:
        mermaid_file (str): Path to the Mermaid source file (.mmd, .mermaid).
        output_file (str): Destination path for the generated PNG.
    
    Returns:
        tuple: `(success, message)` where `success` is `True` on successful conversion and `message` is the file size in KB (e.g., "12.3 KB"); on failure `success` is `False` and `message` contains an error description.
    """
    try:
        # Read Mermaid file
        with open(mermaid_file, 'r', encoding='utf-8') as f:
            mermaid_code = f.read()

        # Encode for API
        encoded = encode_mermaid(mermaid_code)

        # Build API URL
        # Using mermaid.ink - free, no auth required
        api_url = f"https://mermaid.ink/img/{encoded}?type=png&theme=default&scale=2"

        # Download PNG
        print(f"  Downloading from API...")
        urllib.request.urlretrieve(api_url, output_file)

        # Check file size
        file_size = os.path.getsize(output_file)
        if file_size < 100:
            # Likely an error response
            return False, "File too small - may be error response"

        size_kb = file_size / 1024
        return True, f"{size_kb:.1f} KB"

    except Exception as e:
        return False, str(e)

def main():
    # Determine root directory
    """
    Run the conversion process: locate Mermaid files, convert each to a PNG, and print per-file progress and a summary.
    
    The root directory is taken from the first command-line argument if provided; otherwise it defaults to the parent of the script directory. The function prints status messages to standard output while it searches for Mermaid files (*.mmd, *.mermaid), converts each file to a .png alongside the source, and reports counts of successful and failed conversions.
    
    Returns:
        int: 0 if all files were converted successfully or no Mermaid files were found, 1 if any conversion failed.
    """
    if len(sys.argv) > 1:
        root_dir = sys.argv[1]
    else:
        # Default to Portfolio-Project root
        script_dir = Path(__file__).parent
        root_dir = script_dir.parent

    root_dir = Path(root_dir).resolve()

    print("=" * 60)
    print("  Mermaid to PNG Converter (using mermaid.ink API)")
    print("=" * 60)
    print(f"\nSearching for Mermaid files in: {root_dir}\n")

    # Find all Mermaid files
    mermaid_files = find_mermaid_files(root_dir)

    if not mermaid_files:
        print("No Mermaid files (.mmd or .mermaid) found!")
        return 0

    print(f"Found {len(mermaid_files)} Mermaid diagram(s) to convert\n")

    success_count = 0
    fail_count = 0

    for mermaid_file in mermaid_files:
        # Generate output filename
        output_file = mermaid_file.with_suffix('.png')

        # Display relative path
        try:
            rel_path = mermaid_file.relative_to(root_dir)
            rel_output = output_file.relative_to(root_dir)
        except ValueError:
            rel_path = mermaid_file
            rel_output = output_file

        print(f"Converting: {rel_path}")
        print(f"  → {rel_output}")

        success, message = convert_to_png(mermaid_file, output_file)

        if success:
            print(f"  ✓ Success ({message})")
            success_count += 1
        else:
            print(f"  ✗ Failed: {message}")
            fail_count += 1

        print()

    # Summary
    print("=" * 60)
    print("Conversion Summary:")
    print(f"  ✓ Success: {success_count}")
    if fail_count > 0:
        print(f"  ✗ Failed: {fail_count}")
    print("=" * 60)

    return 0 if fail_count == 0 else 1

if __name__ == "__main__":
    sys.exit(main())