FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy and install requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Uninstall heavy ML packages to keep image < 4 GB for Railway
# The app uses Hugging Face Inference API when these packages are missing
RUN pip uninstall -y torch transformers sentence-transformers accelerate || true

# Copy application code
COPY backend/ ./backend/

# Set Python path
ENV PYTHONPATH=/app

# Expose port (Railway uses PORT at runtime)
EXPOSE 8000

# Run the application (use $PORT for Railway/Vercel compat)
CMD ["sh", "-c", "uvicorn backend.app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
