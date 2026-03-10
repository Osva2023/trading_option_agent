FROM python:3.13-slim

WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Copy requirements and install
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir python-dotenv

# Copy project files
COPY src/ ./src/
COPY web/ ./web/
COPY config/ ./config/
COPY data/ ./data/
COPY run.py ./
COPY .env ./

# Create data and logs directories
RUN mkdir -p data/logs && \
    chmod 755 data/logs

# Expose Flask port
EXPOSE 5001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5001')" || exit 1

# Default command
CMD ["python", "run.py"]
