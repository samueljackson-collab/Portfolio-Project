"""Lightweight orchestration helpers for PRJ-AIML-002."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Iterable, List, Mapping, MutableSequence, Sequence

from . import prompt_builder

ModelRunner = Callable[[str], str]
PostProcessor = Callable[[str], str]


@dataclass
class PackagingJob:
    """A minimal orchestration primitive for the document packaging pipeline."""

    template: prompt_builder.PromptTemplate
    records: Sequence[Mapping[str, object]]
    model_runner: ModelRunner
    postprocessors: Sequence[PostProcessor] = field(default_factory=tuple)

    def run(self) -> List[str]:
        """Execute the job and return processed model outputs."""

        outputs: MutableSequence[str] = []
        for rendered_prompt in prompt_builder.render_batch(self.template, self.records):
            raw = self.model_runner(rendered_prompt)
            outputs.append(self._apply_postprocessors(raw))
        return list(outputs)

    def write_outputs(self, destination: Path) -> None:
        """Persist ``run`` outputs to ``destination`` as UTF-8 text."""

        results = self.run()
        destination.parent.mkdir(parents=True, exist_ok=True)
        with destination.open("w", encoding="utf-8") as handle:
            for index, entry in enumerate(results, start=1):
                handle.write(f"# Output {index}\n\n{entry}\n\n")

    def _apply_postprocessors(self, payload: str) -> str:
        processed = payload
        for processor in self.postprocessors:
            processed = processor(processed)
        return processed


def uppercase_postprocessor(payload: str) -> str:
    """Example post-processor used by documentation and tests."""

    return payload.upper()
