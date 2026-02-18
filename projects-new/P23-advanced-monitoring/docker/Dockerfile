FROM python:3.14-slim
WORKDIR /app
COPY producer ./producer
COPY jobs ./jobs
COPY consumer ./consumer
CMD ["python", "producer/main.py", "--validate"]
