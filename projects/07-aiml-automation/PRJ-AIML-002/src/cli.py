"""Command line entry point for PRJ-AIML-002."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable, List, Optional

from . import adapters, prompt_builder, workflow


def default_runner(prompt: str) -> str:
    """Default model runner that simply returns the rendered prompt."""

    return prompt


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Document packaging helper")
    parser.add_argument("dataset", type=Path, help="Path to the dataset file (CSV, TSV, or JSON array)")
    parser.add_argument("template", type=Path, help="Prompt template file (.json or plain text)")
    parser.add_argument("output", type=Path, nargs="?", help="Optional output file to write results to")
    parser.add_argument("--dataset-kind", choices=["delimited", "json"], help="Override dataset type detection")
    parser.add_argument("--uppercase", action="store_true", help="Apply uppercase post-processing to outputs")
    parser.add_argument("--dry-run", action="store_true", help="Render prompts without invoking the model runner")
    return parser


def load_template(path: Path) -> prompt_builder.PromptTemplate:
    if path.suffix.lower() == ".json":
        return prompt_builder.PromptTemplate.from_json(str(path))
    body = path.read_text(encoding="utf-8")
    return prompt_builder.PromptTemplate(name=path.stem, body=body, description=None)


def render_prompts(records: Iterable[dict], template: prompt_builder.PromptTemplate) -> List[str]:
    return [prompt for prompt in prompt_builder.render_batch(template, records)]


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    dataset_spec = adapters.DatasetSpec(path=args.dataset, kind=args.dataset_kind)
    records = adapters.load_records(dataset_spec)
    template = load_template(args.template)

    if args.dry_run:
        for prompt in render_prompts(records, template):
            print("--- Prompt ---")
            print(prompt)
        return 0

    postprocessors = []
    if args.uppercase:
        postprocessors.append(workflow.uppercase_postprocessor)

    job = workflow.PackagingJob(
        template=template,
        records=records,
        model_runner=default_runner,
        postprocessors=tuple(postprocessors),
    )

    if args.output:
        job.write_outputs(args.output)
    else:
        for output in job.run():
            print("--- Output ---")
            print(output)
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    raise SystemExit(main())
