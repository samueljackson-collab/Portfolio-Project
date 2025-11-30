import os
import requests

a = os.getenv("REGION_A_URL", "http://region-a:8100/health")
b = os.getenv("REGION_B_URL", "http://region-b:8100/health")

for target in (a, b):
    try:
        resp = requests.get(target, timeout=2)
        if resp.status_code == 200:
            print(f"routing to {target}")
            break
    except Exception as exc:  # noqa: BLE001
        print(f"probe failed for {target}: {exc}")
else:
    print("no healthy regions")
