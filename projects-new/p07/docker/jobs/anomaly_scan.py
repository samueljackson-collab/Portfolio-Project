import os
import time
import psycopg2

DSN = os.getenv("POSTGRES_DSN")
QUERY = """
select imsi, count(*) as events
from roaming_events
where event = 'attach' and created_at > now() - interval '1 hour'
group by imsi
having count(*) > 50;
"""

while True:
    try:
        conn = psycopg2.connect(DSN)
        cur = conn.cursor()
        cur.execute(QUERY)
        rows = cur.fetchall()
        if rows:
            print("ALERT: high attach volume", rows, flush=True)
        conn.close()
    except Exception as exc:  # noqa: BLE001
        print(f"anomaly scan error: {exc}", flush=True)
    time.sleep(300)
