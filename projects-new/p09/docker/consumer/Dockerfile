FROM python:3.11-slim
WORKDIR /app
COPY consumer.py /app/consumer.py
RUN pip install fastapi==0.110.0 uvicorn==0.29.0 sqlite-utils==3.36
EXPOSE 8090
CMD ["uvicorn", "consumer:app", "--host", "0.0.0.0", "--port", "8090"]
