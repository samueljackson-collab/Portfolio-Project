FROM python:3.11-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential libffi-dev libxml2-dev libxslt1-dev zlib1g-dev curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir scrapyd==1.4.3 scrapy==2.11.1 scrapyd-client==1.2.2

WORKDIR /opt/scrapy
VOLUME ["/opt/scrapy/projects"]
EXPOSE 6800

HEALTHCHECK --interval=30s --timeout=10s --retries=5 CMD curl -f http://localhost:6800/ || exit 1

CMD ["scrapyd"]
