import argparse
import requests


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="http://localhost:8000")
    args = parser.parse_args()

    r = requests.get(f"{args.base_url}/health", timeout=5)
    r.raise_for_status()
    print("Health ok", r.json())

    r = requests.post(f"{args.base_url}/todos", json={"title": "demo"}, timeout=5)
    r.raise_for_status()
    print("Created", r.json())

    r = requests.get(f"{args.base_url}/todos", timeout=5)
    r.raise_for_status()
    print("Todos", r.json())


if __name__ == "__main__":
    main()
