# DupeFinder Tool (Stub)

Lightweight duplicate detection utility with optional integrations for perceptual hashes, audio fingerprints, and CLIP embeddings. Heavy dependencies are optional; fallbacks rely on file hashes.

## Usage

```bash
python -m tools.dupefinder.cli index /path/to/media
python -m tools.dupefinder.cli match --threshold 0.9
```

## Requirements
- Python 3.11
- Optional: `imagehash`, `chromaprint`, `transformers`, `torch`

