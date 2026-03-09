from __future__ import annotations
from pathlib import Path
import json
import secrets

ARTIFACT = Path("artifacts/kyber_key_material.json")
ARTIFACT.parent.mkdir(exist_ok=True)


def generate_keypair() -> dict:
    public = secrets.token_hex(16)
    private = secrets.token_hex(32)
    return {"public_key": public, "private_key": private}


def main():
    keypair = generate_keypair()
    envelope = {"algorithm": "kyber-mock", "keypair": keypair}
    ARTIFACT.write_text(json.dumps(envelope, indent=2))
    print("Quantum-safe crypto demo complete. See artifacts/kyber_key_material.json")


if __name__ == "__main__":
    main()
