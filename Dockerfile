FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install ONLY slim dependencies (exclude heavy/unused packages)
# This keeps image < 4 GB for Railway. App uses HF Inference API when packages are missing.
COPY requirements.txt .
RUN python3 -c "\
import re; \
exclude = {'torch', 'transformers', 'sentence-transformers', 'accelerate', 'lxml', 'psycopg2-binary', 'sqlalchemy', 'redis', 'google-api-python-client', 'google-auth-httplib2', 'google-auth-oauthlib', 'pytest', 'pytest-asyncio'}; \
lines = [l for l in open('requirements.txt') if not l.strip() or l.strip().startswith('#') or re.split(r'[>=<!=]', l.strip())[0].strip() not in exclude]; \
open('/tmp/req-slim.txt', 'w').writelines(lines)" && \
    pip install --no-cache-dir -r /tmp/req-slim.txt && \
    rm /tmp/req-slim.txt

# Copy application code
COPY backend/ ./backend/

# Set Python path
ENV PYTHONPATH=/app

# Expose port (Railway uses PORT at runtime)
EXPOSE 8000

# Run the application (use $PORT for Railway/Vercel compat)
CMD ["sh", "-c", "uvicorn backend.app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
