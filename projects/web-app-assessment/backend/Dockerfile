FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY app ./app
# Create a non-root user and group
RUN addgroup --system appuser && adduser --system --ingroup appuser appuser
# Give ownership of the app directory to the non-root user
RUN chown -R appuser:appuser /app
# Switch to the non-root user
USER appuser
# Create a non-root user and group
RUN addgroup --system appuser && adduser --system --ingroup appuser appuser
# Give ownership of the app directory to the non-root user
RUN chown -R appuser:appuser /app
# Switch to the non-root user
USER appuser
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
