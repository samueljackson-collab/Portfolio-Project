import os
import requests

BASE_URL = os.getenv("PORTFOLIO_API_BASE", "https://api.portfolio.example.com/api/v1")
TOKEN = os.environ["PORTFOLIO_API_TOKEN"]

session = requests.Session()
session.headers.update({
    "Authorization": f"Bearer {TOKEN}",
    "Accept": "application/json",
})

resp = session.get(f"{BASE_URL}/portfolio", params={"page": 1, "limit": 10})
resp.raise_for_status()

for entry in resp.json()["data"]:
    print(f"{entry['id']}: {entry['title']} ({entry['status']})")
