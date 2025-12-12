from datetime import datetime, timedelta
from typing import Tuple


def window_bounds(duration_minutes: int) -> Tuple[datetime, datetime]:
    """Return (start_time, end_time) for a drill window using safe arithmetic."""
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(minutes=duration_minutes)
    return start_time, end_time


if __name__ == "__main__":
    start, end = window_bounds(30)
    print(f"Drill window from {start.isoformat()} to {end.isoformat()}")
