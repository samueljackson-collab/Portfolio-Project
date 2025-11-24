FROM python:3.11-slim
WORKDIR /app
COPY . /app
RUN pip install psycopg2-binary==2.9.9 pyyaml==6.0.1
CMD ["python", "anomaly_scan.py"]
