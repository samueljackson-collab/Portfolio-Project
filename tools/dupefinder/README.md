# DupeFinder

Minimal toolkit for indexing media libraries and surfacing potential duplicates.

## Installation

```bash
pip install -r tools/dupefinder/requirements.txt
```

Optional extras (CLIP, pHash, Chromaprint, FAISS) are detected automatically when installed.

## Usage

```bash
python -m tools.dupefinder.cli index /mnt/media --db dupefinder.db
python -m tools.dupefinder.cli match --threshold 0.85 --db dupefinder.db
```

## Development

- Database models live in `tools/dupefinder/models.py`
- Matching heuristics are in `tools/dupefinder/service.py`
- CLI entrypoint is `tools/dupefinder/cli.py`

Run tests with:

```bash
pytest -q
```
