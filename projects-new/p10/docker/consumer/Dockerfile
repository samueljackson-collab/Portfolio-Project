FROM python:3.11-slim
WORKDIR /app
COPY service.py /app/service.py
RUN pip install fastapi==0.110.0 uvicorn==0.29.0
EXPOSE 8100
CMD ["uvicorn", "service:app", "--host", "0.0.0.0", "--port", "8100"]
