FROM python:3.11-slim
WORKDIR /app
COPY producer.py /app/producer.py
RUN pip install requests==2.31.0
CMD ["python", "producer.py"]
