FROM python:3.11-slim

WORKDIR /app
ENV PYTHONUNBUFFERED=1

COPY . /app

RUN pip install --no-cache-dir --upgrade pip     && if [ -f requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; fi

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3   CMD python -c "from src.health_check import check_health; assert check_health()['status'] == 'ok'"

CMD ["python", "-m", "src.health_check"]
