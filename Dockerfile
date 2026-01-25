FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN python3 -c "\
import re; \
exclude = {'torch', 'transformers', 'sentence-transformers', 'accelerate', 'lxml', 'psycopg2-binary', 'sqlalchemy', 'redis', 'google-api-python-client', 'google-auth-httplib2', 'google-auth-oauthlib', 'pytest', 'pytest-asyncio'}; \
lines = [l for l in open('requirements.txt') if not l.strip() or l.strip().startswith('#') or re.split(r'[>=<!=]', l.strip())[0].strip() not in exclude]; \
open('/tmp/req-slim.txt', 'w').writelines(lines)" && \
    pip install --no-cache-dir -r /tmp/req-slim.txt && \
    rm /tmp/req-slim.txt

COPY backend/ ./backend/

ENV PYTHONPATH=/app

EXPOSE 8000

CMD ["sh", "-c", "uvicorn backend.app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
