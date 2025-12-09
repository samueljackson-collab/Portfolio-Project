FROM python:3.11-slim
WORKDIR /app
COPY router /app/router
RUN pip install requests==2.31.0
CMD ["python", "router/failover.py"]
