FROM python:3.14-slim AS build
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.14-slim
WORKDIR /app
COPY --from=build /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY src ./src
ENV PYTHONPATH=/app
EXPOSE 8085
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8085"]
