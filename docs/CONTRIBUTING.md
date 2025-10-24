# Contributing Guide

Thanks for helping improve this portfolio project. The sections below outline how to propose changes, document work, and maintain consistent standards.

## General Workflow
1. Open an issue or describe the change you intend to make.
2. Create a feature branch and ensure commits have descriptive messages.
3. Update documentation alongside code changes when relevant.
4. Run available tests or linters before submitting a pull request.

## Commit Conventions
- Use imperative, present-tense commit subjects (e.g., "Add research automation CLI").
- Reference issue IDs when applicable.
- Keep commits focused; avoid bundling unrelated changes together.

## Documentation Standards
- Prefer Markdown for guides, runbooks, and research artifacts.
- Store diagrams or large media files in `assets/` folders close to their related documents.
- Include a short summary at the top of longer documents to orient readers quickly.

---

## Research Contribution Standards
To keep research artifacts reproducible and easy to review, follow these guidelines when adding material under `prompts/` or `docs/`:

### File Naming & Structure
- Use the format `YYYY-MM-DD_topic_artifact-type.md` for dossiers, notes, or logs.
- Organize supporting data in `artifacts/YYYY/MM/topic/` folders.
- Document automation scripts in `tools/` or `scripts/` with usage examples in the header comments.

### Metadata & Date Stamps
- Include a metadata block near the top of each research document with topic, author, date (UTC), version, and confidentiality level if applicable.
- Update the metadata date whenever a material change is made; log revisions in a change history table or Git commit message.

### Citations & Evidence
- Use inline citations formatted as `[Author, Year]` or numeric footnotes—be consistent across the document.
- Each citation should include: title, author(s), publication, date, URL/DOI, access date, source type, and evidence grade (see `prompts/research/01_strategy.md`).
- Capture direct quotes with page numbers or timestamps.
- Store archived copies of cited sources when licensing allows.

### Validation & Review
- Run the checklist in `prompts/research/05_validation.md` before publishing a dossier.
- Document open questions and counter-arguments alongside recommendations.
- When feasible, request a peer review or "red team" pass, recording reviewer name and date.

Following these steps keeps research contributions auditable and ready for automation by the ResearchOrchestrator agent.
