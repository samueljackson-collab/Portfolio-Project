import json
import runpy
from collections import Counter
from pathlib import Path


def load_module():
    module_path = Path(__file__).resolve().parents[1] / "src" / "process_events.py"
    return module_path


def test_sample_event_distribution():
    module = runpy.run_path(str(load_module()))
    counts = Counter(event["status"] for event in module["SAMPLE_EVENTS"])
    assert counts == {"success": 2, "failure": 1}


def test_main_outputs_expected_counts(capsys):
    runpy.run_path(str(load_module()), run_name="__main__")
    output = capsys.readouterr().out
    parsed = json.loads(output)
    assert parsed == {"success": 2, "failure": 1}
