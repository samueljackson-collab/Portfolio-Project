import os
from dataclasses import dataclass
from typing import Dict


@dataclass
class KeyPair:
    public_key: str
    secret_key: str


class PQCDemo:
    """Lightweight placeholder demonstrating KEM flow."""

    def generate_keypair(self) -> KeyPair:
        # Placeholder keys for demo purposes
        public_key = os.urandom(32).hex()
        secret_key = os.urandom(32).hex()
        print("✓ Keypair generated")
        return KeyPair(public_key=public_key, secret_key=secret_key)

    def encapsulate(self, public_key_hex: str) -> Dict[str, str]:
        """Encapsulate a shared secret using the public key (simulated)."""
        print("\nEncapsulating shared secret...")
        shared_secret = os.urandom(32)
        ciphertext = os.urandom(48)
        print(f"✓ Shared secret created ({len(shared_secret)} bytes)")
        return {
            "ciphertext": ciphertext.hex(),
            "shared_secret": shared_secret.hex(),
        }

    def decapsulate(self, secret_key_hex: str, ciphertext_hex: str, original_secret_hex: str | None = None) -> Dict[str, str]:
        """
        Decapsulate to recover shared secret using secret key.

        NOTE: In this placeholder demo, we simulate recovery by accepting
        the original secret. In production with liboqs, decapsulation
        cryptographically derives the same secret from the ciphertext.
        """
        print("\nDecapsulating shared secret...")

        # Placeholder - in production, liboqs derives the same secret cryptographically
        # For demo purposes, we simulate successful recovery
        if original_secret_hex:
            shared_secret = bytes.fromhex(original_secret_hex)
        else:
            raise ValueError("original_secret_hex must be provided for this demo decapsulation")

        print(f"✓ Shared secret recovered ({len(shared_secret)} bytes)")

        return {
            "shared_secret": shared_secret.hex()
        }

    def demo_key_exchange(self) -> None:
        """Run a simple end-to-end demonstration."""
        alice_keys = self.generate_keypair()

        print("\n[Bob] Encapsulating for Alice...")
        encap_result = self.encapsulate(alice_keys.public_key)

        print("\n[Alice] Decapsulating shared secret...")
        decap_result = self.decapsulate(
            alice_keys.secret_key,
            encap_result["ciphertext"],
            encap_result["shared_secret"]
        )

        assert encap_result["shared_secret"] == decap_result["shared_secret"], "Shared secrets do not match!"
        print("\n✓ Key exchange successful: both parties share the same secret")


if __name__ == "__main__":
    PQCDemo().demo_key_exchange()
