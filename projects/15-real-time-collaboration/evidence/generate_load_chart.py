import csv
from pathlib import Path

import matplotlib.pyplot as plt


def main() -> None:
    csv_path = Path("projects/15-real-time-collaboration/evidence/load_test_results.csv")
    output_path = Path("projects/15-real-time-collaboration/evidence/load_test_chart.png")

    rows = []
    with csv_path.open() as file:
        reader = csv.DictReader(file)
        for row in reader:
            rows.append((int(row["concurrent_users"]), float(row["avg_latency_ms"])))

    users = [row[0] for row in rows]
    latencies = [row[1] for row in rows]

    plt.figure(figsize=(6, 4))
    plt.plot(users, latencies, marker="o", color="#3b82f6")
    plt.title("Load Test: Concurrent Users vs Avg Latency")
    plt.xlabel("Concurrent Users")
    plt.ylabel("Avg Ack Latency (ms)")
    plt.grid(True, linestyle="--", linewidth=0.5, alpha=0.6)
    plt.tight_layout()
    plt.savefig(output_path, dpi=160)


if __name__ == "__main__":
    main()
