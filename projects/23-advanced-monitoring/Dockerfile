FROM python:3.14-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir --upgrade pip \
    && if [ -f requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; fi

ENV PYTHONUNBUFFERED=1

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD python src/health_check.py || exit 1

CMD ["python", "src/health_check.py"]
