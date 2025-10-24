"""Ensure service modules import and expose expected classes."""

import twistedmonk
from twistedmonk.ads import AdAutomationService
from twistedmonk.automation import AutomationOrchestrator
from twistedmonk.competitors import CompetitorIntelEngine
from twistedmonk.seo import ContentAISuite
from twistedmonk.video import VideoAIPipeline


def test_namespace_exports():
    assert hasattr(twistedmonk, "load_config")
    assert hasattr(twistedmonk, "configure_logging")


def test_service_instantiation():
    assert ContentAISuite(project_name="demo").publish_to_cms("slug")
    assert VideoAIPipeline(channel="primary").publish_video("yt")
    assert AdAutomationService(account_id="acct").compile_reports("weekly")
    assert CompetitorIntelEngine(market="global").summarize_findings() == "Summary pending"
    assert AutomationOrchestrator(workflow_name="ops").trigger_pipeline("deploy")
