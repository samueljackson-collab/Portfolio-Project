# DupeFinder tools

A minimal, testable toolkit for experimenting with media duplicate detection. The
package avoids mandatory heavyweight dependencies by providing graceful fallbacks
when advanced libraries such as Pillow, Chromaprint or OpenAI CLIP are not
available.

## Features

- Lightweight Typer CLI: `index <path>` and `match --threshold 0.85`.
- SQLite storage through SQLAlchemy when available, with an in-memory fallback.
- Perceptual hashing, audio fingerprinting and embedding extraction with
  deterministic fallbacks so that the toolkit remains usable without optional
  libraries.
- Pure Python similarity index with hooks for FAISS/HNSW if present.

## Installation

The core requirements are intentionally small:

```bash
pip install -r tools/dupefinder/requirements.txt
```

Optional enhancements are discovered automatically at runtime:

- [imagehash](https://github.com/JohannesBuchner/imagehash) + Pillow for higher
  quality perceptual hashing.
- [pyacoustid](https://github.com/beetbox/pyacoustid) and Chromaprint for audio
  fingerprinting.
- [OpenAI CLIP](https://github.com/openai/CLIP) (plus PyTorch) for semantic
  embeddings.
- [FAISS](https://github.com/facebookresearch/faiss) or
  [hnswlib](https://github.com/nmslib/hnswlib) for accelerated similarity search.

## Usage

```bash
python -m tools.dupefinder.cli index /path/to/media --database /tmp/dupes.db
python -m tools.dupefinder.cli match --threshold 0.9 --database /tmp/dupes.db
```

The commands emit informative warnings whenever a feature falls back to a stub so
that you are aware of the capabilities currently in use.

## Development

Run the dedicated test suite via the repository make target:

```bash
make tools-test
```

This executes `pytest tools/dupefinder/tests` ensuring the package works with the
fallback implementations.
