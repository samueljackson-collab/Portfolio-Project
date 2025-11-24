FROM python:3.11-slim
WORKDIR /app
COPY api.py /app/api.py
RUN pip install fastapi==0.110.0 uvicorn==0.29.0
EXPOSE 8080
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8080"]
