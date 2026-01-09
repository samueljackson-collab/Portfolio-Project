"""Lightweight scheduler stub for roaming simulations."""

import subprocess
import time


def run(profile: str, batch_size: int):
    cmd = [
        "python",
        "producer/main.py",
        "--profile",
        profile,
        "--events",
        str(batch_size),
    ]
    subprocess.check_call(cmd)
    subprocess.check_call(
        ["python", "consumer/main.py", "--ingest-file", "out/events.jsonl"]
    )


def schedule():
    for profile in ("urban", "rural", "cross_border"):
        print(f"Running profile {profile}")
        run(profile, 50)
        time.sleep(1)


if __name__ == "__main__":
    schedule()
