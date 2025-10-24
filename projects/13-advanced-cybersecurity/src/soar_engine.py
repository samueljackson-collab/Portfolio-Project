"""Simplified SOAR engine that enriches alerts and executes response playbooks."""
from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from typing import Dict, Iterable, List


@dataclass
class Alert:
    id: str
    severity: str
    source_ip: str
    asset_id: str
    description: str
    tags: List[str]


class ThreatIntelService:
    def lookup(self, ip: str) -> Dict[str, str]:
        return {"ip": ip, "reputation": "suspicious", "confidence": "0.72"}


class AssetInventory:
    def criticality(self, asset_id: str) -> str:
        return "high" if asset_id.startswith("prod") else "medium"


class PlaybookExecutor:
    def isolate_host(self, asset_id: str) -> None:
        print(f"[ACTION] Isolating host {asset_id}")

    def open_ticket(self, alert_id: str, severity: str) -> None:
        print(f"[ACTION] Opening ticket for {alert_id} severity={severity}")


class SoarEngine:
    def __init__(self) -> None:
        self.intel = ThreatIntelService()
        self.inventory = AssetInventory()
        self.executor = PlaybookExecutor()

    def process_alerts(self, alerts: Iterable[Alert]) -> None:
        for alert in alerts:
            context = self._enrich(alert)
            score = self._score(context)
            print(f"Alert {alert.id} score={score:.2f}")
            if score >= 0.7:
                self.executor.isolate_host(alert.asset_id)
            self.executor.open_ticket(alert.id, alert.severity)

    def _enrich(self, alert: Alert) -> Dict[str, str]:
        intel = self.intel.lookup(alert.source_ip)
        criticality = self.inventory.criticality(alert.asset_id)
        return {**alert.__dict__, **intel, "criticality": criticality}

    def _score(self, context: Dict[str, str]) -> float:
        severity_weight = {"low": 0.2, "medium": 0.5, "high": 0.8, "critical": 1.0}
        base = severity_weight.get(context.get("severity", "low").lower(), 0.3)
        criticality_bonus = 0.2 if context.get("criticality") == "high" else 0.0
        reputation_bonus = float(context.get("confidence", "0")) * 0.3
        return min(1.0, base + criticality_bonus + reputation_bonus)


def load_alerts(path: str) -> List[Alert]:
    payload = json.loads(open(path, "r", encoding="utf-8").read())
    return [Alert(**item) for item in payload]


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--alerts", required=True)
    args = parser.parse_args()

    engine = SoarEngine()
    engine.process_alerts(load_alerts(args.alerts))
