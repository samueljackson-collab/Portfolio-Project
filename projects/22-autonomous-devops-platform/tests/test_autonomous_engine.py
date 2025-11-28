from importlib import util
from pathlib import Path


def load_module():
    path = Path(__file__).resolve().parents[1] / "src" / "autonomous_engine.py"
    spec = util.spec_from_file_location("autonomous_engine", path)
    module = util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)  # type: ignore[call-arg]
    return module


autonomous_engine = load_module()


def test_registry_executes_registered_runbooks(capsys):
    registry = autonomous_engine.RunbookRegistry()
    registry.register("ping", lambda event: print(event.type))

    registry.execute(autonomous_engine.Event("ping", "low", {}))
    captured = capsys.readouterr()
    assert "ping" in captured.out


def test_scale_service_handler_uses_metadata(capsys):
    event = autonomous_engine.Event("latency_alert", "high", {"service": "api"})
    autonomous_engine.scale_service(event)
    output = capsys.readouterr().out
    assert "api" in output
