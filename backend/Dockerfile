FROM python:3.11-slim

WORKDIR /app

# Install dependencies first (cached layer)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Railway injects PORT env var (default 8000)
ENV PORT=8000
EXPOSE 8000

# Use shell form so $PORT is expanded at runtime
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port $PORT"]
