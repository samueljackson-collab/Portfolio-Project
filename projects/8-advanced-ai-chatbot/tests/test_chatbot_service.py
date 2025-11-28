import importlib.util
import json
from pathlib import Path

import pytest


class EagerLLM:
    async def stream_answer(self, prompt: str):
        for token in ["response", "complete"]:
            yield token + " "


def _load_module():
    module_path = Path(__file__).resolve().parents[1] / "src" / "chatbot_service.py"
    spec = importlib.util.spec_from_file_location("chatbot_service", module_path)
    module = importlib.util.module_from_spec(spec)
    import sys

    sys.modules["chatbot_service"] = module
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


@pytest.mark.asyncio
async def test_prompt_formatter_builds_context():
    module = _load_module()
    docs = [module.RetrievedDocument(content="Details", score=0.9, metadata={"source": "guide"})]

    prompt = module.PromptFormatter().build_prompt("How?", docs)

    assert "Details" in prompt
    assert "guide" in prompt
    assert "Question: How?" in prompt


@pytest.mark.asyncio
async def test_service_answer_returns_streaming_response():
    module = _load_module()
    documents = [module.RetrievedDocument(content="Doc", score=0.8, metadata={"source": "s1"})]
    service = module.ChatbotService(module.VectorStore(documents), EagerLLM())

    response = await service.answer("What is new?")
    body = b"".join([chunk async for chunk in response.body_iterator])
    sources = json.loads(response.headers["X-Chatbot-Sources"])

    assert body.decode("utf-8").strip().endswith("complete")
    assert sources == [{"source": "s1"}]


@pytest.mark.asyncio
async def test_websocket_answer_streams_until_disconnect():
    module = _load_module()

    class DummyWebSocket:
        def __init__(self):
            self.accepted = False
            self.sent = []
            self._messages = ["ping"]

        async def accept(self):
            self.accepted = True

        async def receive_text(self):
            if self._messages:
                return self._messages.pop(0)
            raise module.WebSocketDisconnect()

        async def send_text(self, text: str):
            self.sent.append(text)

    docs = [module.RetrievedDocument(content="Doc", score=0.9, metadata={"source": "ws"})]
    service = module.ChatbotService(module.VectorStore(docs), EagerLLM())
    websocket = DummyWebSocket()

    await service.websocket_answer(websocket)

    assert websocket.accepted
    assert websocket.sent  # streamed at least one token
