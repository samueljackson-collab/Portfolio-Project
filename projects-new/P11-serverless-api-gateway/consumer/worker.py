"""Consumer prints enriched payload."""

from pathlib import Path
import json


def consume(enriched_path: Path) -> None:
    data = json.loads(enriched_path.read_text())
    message = f"Delivered {data.get('project')}::{data.get('slug')} event='{data.get('event')}' checksum={data.get('checksum')}"
    log_path = enriched_path.parent / "consumer.log"
    log_path.open("a").write(message + "\n")
    print(message)


if __name__ == "__main__":
    consume(Path("artifacts/enriched.json"))
