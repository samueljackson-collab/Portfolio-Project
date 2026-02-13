from tools.research_agent import build_dossier


def test_build_dossier_uses_private_instruction_bank():
    dossier = build_dossier("Observability Stack", "default")
    assert "Research Strategy" in dossier
    assert "Scope Definition" in dossier
    assert "Research Validation" in dossier
