FROM python:3.11-slim
WORKDIR /app
COPY tests /app/tests
RUN pip install pytest==8.0.0 requests==2.31.0
CMD ["pytest", "tests"]
