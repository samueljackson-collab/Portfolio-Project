FROM python:3.14-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy exporter script
COPY app_exporter.py .

# Make script executable
RUN chmod +x app_exporter.py

# Expose metrics port
EXPOSE 8000

# Run exporter
CMD ["python", "app_exporter.py"]
