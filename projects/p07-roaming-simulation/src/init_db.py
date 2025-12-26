#!/usr/bin/env python3
"""Initialize subscriber database."""
import os

# Create necessary directories
os.makedirs("data", exist_ok=True)
os.makedirs("logs", exist_ok=True)

print("✓ Database directories created")
print("✓ Ready to run simulations")
