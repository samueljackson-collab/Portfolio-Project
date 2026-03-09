"""Threat intelligence enrichment adapters for SOAR engine."""
from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional

import aiohttp

LOGGER = logging.getLogger(__name__)


class ThreatCategory(Enum):
    """Threat classification categories."""
    MALWARE = "malware"
    PHISHING = "phishing"
    C2 = "command_and_control"
    BOTNET = "botnet"
    SPAM = "spam"
    SCANNER = "scanner"
    BRUTEFORCE = "bruteforce"
    TOR_EXIT = "tor_exit"
    PROXY = "proxy"
    UNKNOWN = "unknown"


@dataclass
class EnrichmentResult:
    """Result from threat intelligence lookup."""
    source: str
    indicator: str
    indicator_type: str
    is_malicious: bool
    confidence: float
    categories: List[ThreatCategory] = field(default_factory=list)
    reputation_score: float = 0.0
    first_seen: Optional[datetime] = None
    last_seen: Optional[datetime] = None
    related_indicators: List[str] = field(default_factory=list)
    raw_data: Dict[str, Any] = field(default_factory=dict)
    cached: bool = False
    lookup_time_ms: float = 0.0


class EnrichmentCache:
    """Simple in-memory cache for enrichment results."""

    def __init__(self, ttl_seconds: int = 3600):
        self.ttl = ttl_seconds
        self._cache: Dict[str, tuple] = {}

    def _key(self, source: str, indicator: str) -> str:
        return hashlib.md5(f"{source}:{indicator}".encode()).hexdigest()

    def get(self, source: str, indicator: str) -> Optional[EnrichmentResult]:
        key = self._key(source, indicator)
        if key in self._cache:
            result, timestamp = self._cache[key]
            if time.time() - timestamp < self.ttl:
                result.cached = True
                return result
            del self._cache[key]
        return None

    def set(self, source: str, indicator: str, result: EnrichmentResult) -> None:
        key = self._key(source, indicator)
        self._cache[key] = (result, time.time())

    def clear(self) -> None:
        self._cache.clear()


class BaseEnrichmentAdapter(ABC):
    """Abstract base class for enrichment adapters."""

    def __init__(self, api_key: Optional[str] = None, cache: Optional[EnrichmentCache] = None):
        self.api_key = api_key
        self.cache = cache or EnrichmentCache()
        self.rate_limit_remaining = 1000
        self.rate_limit_reset = 0

    @property
    @abstractmethod
    def source_name(self) -> str:
        """Return the name of this enrichment source."""
        pass

    @abstractmethod
    async def lookup_ip(self, ip: str) -> EnrichmentResult:
        """Look up an IP address."""
        pass

    @abstractmethod
    async def lookup_domain(self, domain: str) -> EnrichmentResult:
        """Look up a domain."""
        pass

    @abstractmethod
    async def lookup_hash(self, file_hash: str) -> EnrichmentResult:
        """Look up a file hash."""
        pass

    def _check_rate_limit(self) -> bool:
        """Check if we're within rate limits."""
        if self.rate_limit_remaining <= 0:
            if time.time() < self.rate_limit_reset:
                return False
        return True


class VirusTotalAdapter(BaseEnrichmentAdapter):
    """VirusTotal threat intelligence adapter."""

    BASE_URL = "https://www.virustotal.com/api/v3"

    @property
    def source_name(self) -> str:
        return "virustotal"

    async def _request(self, endpoint: str) -> Dict[str, Any]:
        """Make authenticated request to VirusTotal API."""
        if not self.api_key:
            raise ValueError("VirusTotal API key required")

        headers = {"x-apikey": self.api_key}
        start = time.time()

        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.BASE_URL}/{endpoint}", headers=headers) as resp:
                self.rate_limit_remaining = int(resp.headers.get("X-Api-Quota-Remaining", 1000))

                if resp.status == 429:
                    LOGGER.warning("VirusTotal rate limit exceeded")
                    raise Exception("Rate limit exceeded")

                if resp.status != 200:
                    LOGGER.error(f"VirusTotal API error: {resp.status}")
                    return {}

                return await resp.json()

    async def lookup_ip(self, ip: str) -> EnrichmentResult:
        cached = self.cache.get(self.source_name, ip)
        if cached:
            return cached

        start = time.time()
        try:
            data = await self._request(f"ip_addresses/{ip}")
            attrs = data.get("data", {}).get("attributes", {})
            stats = attrs.get("last_analysis_stats", {})

            malicious = stats.get("malicious", 0)
            total = sum(stats.values()) or 1
            confidence = malicious / total

            result = EnrichmentResult(
                source=self.source_name,
                indicator=ip,
                indicator_type="ip",
                is_malicious=malicious > 2,
                confidence=confidence,
                reputation_score=attrs.get("reputation", 0),
                categories=self._parse_categories(attrs),
                raw_data=data,
                lookup_time_ms=(time.time() - start) * 1000,
            )
        except Exception as e:
            LOGGER.error(f"VirusTotal lookup failed for {ip}: {e}")
            result = EnrichmentResult(
                source=self.source_name,
                indicator=ip,
                indicator_type="ip",
                is_malicious=False,
                confidence=0.0,
                lookup_time_ms=(time.time() - start) * 1000,
            )

        self.cache.set(self.source_name, ip, result)
        return result

    async def lookup_domain(self, domain: str) -> EnrichmentResult:
        cached = self.cache.get(self.source_name, domain)
        if cached:
            return cached

        start = time.time()
        try:
            data = await self._request(f"domains/{domain}")
            attrs = data.get("data", {}).get("attributes", {})
            stats = attrs.get("last_analysis_stats", {})

            malicious = stats.get("malicious", 0)
            total = sum(stats.values()) or 1

            result = EnrichmentResult(
                source=self.source_name,
                indicator=domain,
                indicator_type="domain",
                is_malicious=malicious > 2,
                confidence=malicious / total,
                reputation_score=attrs.get("reputation", 0),
                categories=self._parse_categories(attrs),
                raw_data=data,
                lookup_time_ms=(time.time() - start) * 1000,
            )
        except Exception as e:
            LOGGER.error(f"VirusTotal lookup failed for {domain}: {e}")
            result = EnrichmentResult(
                source=self.source_name,
                indicator=domain,
                indicator_type="domain",
                is_malicious=False,
                confidence=0.0,
                lookup_time_ms=(time.time() - start) * 1000,
            )

        self.cache.set(self.source_name, domain, result)
        return result

    async def lookup_hash(self, file_hash: str) -> EnrichmentResult:
        cached = self.cache.get(self.source_name, file_hash)
        if cached:
            return cached

        start = time.time()
        try:
            data = await self._request(f"files/{file_hash}")
            attrs = data.get("data", {}).get("attributes", {})
            stats = attrs.get("last_analysis_stats", {})

            malicious = stats.get("malicious", 0)
            total = sum(stats.values()) or 1

            result = EnrichmentResult(
                source=self.source_name,
                indicator=file_hash,
                indicator_type="hash",
                is_malicious=malicious > 3,
                confidence=malicious / total,
                categories=[ThreatCategory.MALWARE] if malicious > 0 else [],
                first_seen=datetime.fromisoformat(attrs.get("first_submission_date", "")) if attrs.get("first_submission_date") else None,
                raw_data=data,
                lookup_time_ms=(time.time() - start) * 1000,
            )
        except Exception as e:
            LOGGER.error(f"VirusTotal lookup failed for {file_hash}: {e}")
            result = EnrichmentResult(
                source=self.source_name,
                indicator=file_hash,
                indicator_type="hash",
                is_malicious=False,
                confidence=0.0,
                lookup_time_ms=(time.time() - start) * 1000,
            )

        self.cache.set(self.source_name, file_hash, result)
        return result

    def _parse_categories(self, attrs: Dict) -> List[ThreatCategory]:
        """Parse VirusTotal categories to threat categories."""
        categories = []
        vt_categories = attrs.get("categories", {})

        category_map = {
            "malware": ThreatCategory.MALWARE,
            "phishing": ThreatCategory.PHISHING,
            "c2": ThreatCategory.C2,
            "botnet": ThreatCategory.BOTNET,
        }

        for cat in vt_categories.values():
            cat_lower = cat.lower()
            for key, threat_cat in category_map.items():
                if key in cat_lower:
                    categories.append(threat_cat)

        return list(set(categories))


class AbuseIPDBAdapter(BaseEnrichmentAdapter):
    """AbuseIPDB threat intelligence adapter."""

    BASE_URL = "https://api.abuseipdb.com/api/v2"

    @property
    def source_name(self) -> str:
        return "abuseipdb"

    async def lookup_ip(self, ip: str) -> EnrichmentResult:
        cached = self.cache.get(self.source_name, ip)
        if cached:
            return cached

        start = time.time()

        if not self.api_key:
            return EnrichmentResult(
                source=self.source_name,
                indicator=ip,
                indicator_type="ip",
                is_malicious=False,
                confidence=0.0,
                lookup_time_ms=(time.time() - start) * 1000,
            )

        headers = {
            "Key": self.api_key,
            "Accept": "application/json",
        }
        params = {"ipAddress": ip, "maxAgeInDays": 90, "verbose": "true"}

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.BASE_URL}/check", headers=headers, params=params
                ) as resp:
                    if resp.status != 200:
                        raise Exception(f"API error: {resp.status}")

                    data = await resp.json()
                    abuse_data = data.get("data", {})

            abuse_score = abuse_data.get("abuseConfidenceScore", 0)
            total_reports = abuse_data.get("totalReports", 0)

            categories = self._parse_abuse_categories(abuse_data.get("reports", []))

            result = EnrichmentResult(
                source=self.source_name,
                indicator=ip,
                indicator_type="ip",
                is_malicious=abuse_score > 50,
                confidence=abuse_score / 100,
                reputation_score=-abuse_score,
                categories=categories,
                last_seen=datetime.fromisoformat(abuse_data["lastReportedAt"]) if abuse_data.get("lastReportedAt") else None,
                raw_data={"abuse_score": abuse_score, "total_reports": total_reports},
                lookup_time_ms=(time.time() - start) * 1000,
            )
        except Exception as e:
            LOGGER.error(f"AbuseIPDB lookup failed for {ip}: {e}")
            result = EnrichmentResult(
                source=self.source_name,
                indicator=ip,
                indicator_type="ip",
                is_malicious=False,
                confidence=0.0,
                lookup_time_ms=(time.time() - start) * 1000,
            )

        self.cache.set(self.source_name, ip, result)
        return result

    async def lookup_domain(self, domain: str) -> EnrichmentResult:
        # AbuseIPDB is IP-focused, return empty result for domains
        return EnrichmentResult(
            source=self.source_name,
            indicator=domain,
            indicator_type="domain",
            is_malicious=False,
            confidence=0.0,
        )

    async def lookup_hash(self, file_hash: str) -> EnrichmentResult:
        # AbuseIPDB doesn't support hash lookups
        return EnrichmentResult(
            source=self.source_name,
            indicator=file_hash,
            indicator_type="hash",
            is_malicious=False,
            confidence=0.0,
        )

    def _parse_abuse_categories(self, reports: List[Dict]) -> List[ThreatCategory]:
        """Parse AbuseIPDB category codes to threat categories."""
        # AbuseIPDB category mapping
        category_map = {
            3: ThreatCategory.SCANNER,
            4: ThreatCategory.SCANNER,
            5: ThreatCategory.BRUTEFORCE,
            6: ThreatCategory.SPAM,
            7: ThreatCategory.C2,
            14: ThreatCategory.SCANNER,
            18: ThreatCategory.BRUTEFORCE,
            21: ThreatCategory.MALWARE,
        }

        categories = set()
        for report in reports[:10]:  # Check first 10 reports
            for cat_id in report.get("categories", []):
                if cat_id in category_map:
                    categories.add(category_map[cat_id])

        return list(categories)


class MISPAdapter(BaseEnrichmentAdapter):
    """MISP threat intelligence platform adapter."""

    def __init__(self, base_url: str, api_key: Optional[str] = None, cache: Optional[EnrichmentCache] = None):
        super().__init__(api_key, cache)
        self.base_url = base_url.rstrip("/")

    @property
    def source_name(self) -> str:
        return "misp"

    async def _search(self, indicator: str, indicator_type: str) -> Dict[str, Any]:
        """Search MISP for an indicator."""
        if not self.api_key:
            return {}

        headers = {
            "Authorization": self.api_key,
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

        payload = {
            "returnFormat": "json",
            "value": indicator,
            "type": indicator_type,
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/attributes/restSearch",
                headers=headers,
                json=payload,
                ssl=False,
            ) as resp:
                if resp.status != 200:
                    return {}
                return await resp.json()

    async def lookup_ip(self, ip: str) -> EnrichmentResult:
        return await self._lookup(ip, "ip-dst")

    async def lookup_domain(self, domain: str) -> EnrichmentResult:
        return await self._lookup(domain, "domain")

    async def lookup_hash(self, file_hash: str) -> EnrichmentResult:
        hash_type = "md5" if len(file_hash) == 32 else "sha256" if len(file_hash) == 64 else "sha1"
        return await self._lookup(file_hash, hash_type)

    async def _lookup(self, indicator: str, indicator_type: str) -> EnrichmentResult:
        cached = self.cache.get(self.source_name, indicator)
        if cached:
            return cached

        start = time.time()
        try:
            data = await self._search(indicator, indicator_type)
            attributes = data.get("response", {}).get("Attribute", [])

            if attributes:
                # Found in MISP - likely malicious
                events = set(attr.get("event_id") for attr in attributes)
                result = EnrichmentResult(
                    source=self.source_name,
                    indicator=indicator,
                    indicator_type=indicator_type,
                    is_malicious=True,
                    confidence=min(0.9, 0.5 + len(events) * 0.1),
                    categories=[ThreatCategory.MALWARE],
                    raw_data={"event_count": len(events)},
                    lookup_time_ms=(time.time() - start) * 1000,
                )
            else:
                result = EnrichmentResult(
                    source=self.source_name,
                    indicator=indicator,
                    indicator_type=indicator_type,
                    is_malicious=False,
                    confidence=0.0,
                    lookup_time_ms=(time.time() - start) * 1000,
                )
        except Exception as e:
            LOGGER.error(f"MISP lookup failed for {indicator}: {e}")
            result = EnrichmentResult(
                source=self.source_name,
                indicator=indicator,
                indicator_type=indicator_type,
                is_malicious=False,
                confidence=0.0,
                lookup_time_ms=(time.time() - start) * 1000,
            )

        self.cache.set(self.source_name, indicator, result)
        return result


class EnrichmentAggregator:
    """Aggregates results from multiple enrichment sources."""

    def __init__(self, adapters: List[BaseEnrichmentAdapter]):
        self.adapters = adapters

    async def enrich_ip(self, ip: str) -> Dict[str, EnrichmentResult]:
        """Enrich an IP address using all adapters."""
        tasks = [adapter.lookup_ip(ip) for adapter in self.adapters]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        return {
            adapter.source_name: result
            for adapter, result in zip(self.adapters, results)
            if not isinstance(result, Exception)
        }

    async def enrich_domain(self, domain: str) -> Dict[str, EnrichmentResult]:
        """Enrich a domain using all adapters."""
        tasks = [adapter.lookup_domain(domain) for adapter in self.adapters]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        return {
            adapter.source_name: result
            for adapter, result in zip(self.adapters, results)
            if not isinstance(result, Exception)
        }

    async def enrich_hash(self, file_hash: str) -> Dict[str, EnrichmentResult]:
        """Enrich a file hash using all adapters."""
        tasks = [adapter.lookup_hash(file_hash) for adapter in self.adapters]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        return {
            adapter.source_name: result
            for adapter, result in zip(self.adapters, results)
            if not isinstance(result, Exception)
        }

    def aggregate_verdict(self, results: Dict[str, EnrichmentResult]) -> Dict[str, Any]:
        """Calculate aggregate verdict from multiple sources."""
        if not results:
            return {"is_malicious": False, "confidence": 0.0, "sources": 0}

        malicious_count = sum(1 for r in results.values() if r.is_malicious)
        total_confidence = sum(r.confidence for r in results.values())
        avg_confidence = total_confidence / len(results)

        all_categories = []
        for r in results.values():
            all_categories.extend(r.categories)

        return {
            "is_malicious": malicious_count > len(results) / 2,
            "confidence": avg_confidence,
            "malicious_sources": malicious_count,
            "total_sources": len(results),
            "categories": list(set(all_categories)),
            "sources": list(results.keys()),
        }
