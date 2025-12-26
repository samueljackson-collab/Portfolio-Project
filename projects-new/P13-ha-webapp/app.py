from __future__ import annotations
from pathlib import Path
from datetime import datetime, timezone

ARTIFACT = Path("artifacts/ha_healthcheck.txt")
ARTIFACT.parent.mkdir(exist_ok=True)


class Node:
    def __init__(self, name: str, healthy: bool = True):
        self.name = name
        self.healthy = healthy

    def heartbeat(self) -> str:
        status = "healthy" if self.healthy else "unhealthy"
        return f"{self.name}:{status}"


def simulate_failover(primary: Node, replica: Node) -> list[str]:
    log: list[str] = []
    log.append(f"[{datetime.now(timezone.utc).isoformat()}Z] Checking primary: {primary.heartbeat()}")
    if primary.healthy:
        log.append("Traffic remains on primary")
    else:
        log.append("Primary failed. Promoting replica…")
        replica.healthy = True
        log.append(f"Replica promotion complete: {replica.heartbeat()}")
    return log


def main():
    primary = Node("app-primary", healthy=False)
    replica = Node("app-replica")
    log = simulate_failover(primary, replica)
    ARTIFACT.write_text("\n".join(log))
    print("HA webapp demo complete. See artifacts/ha_healthcheck.txt")


if __name__ == "__main__":
    main()
