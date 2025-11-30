FROM python:3.11-slim
WORKDIR /app
COPY jobs /app/jobs
COPY producer.py /app/producer.py
RUN pip install kafka-python==2.0.2 pyyaml==6.0.1
ENTRYPOINT ["python", "producer.py"]
