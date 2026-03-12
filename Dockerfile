FROM python:3.11-slim

# Install nmap + curl + procps (for ps/top)
RUN apt-get update && apt-get install -y \
    nmap \
    curl \
    procps \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m -u 1000 appuser
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt
RUN chown -R appuser:appuser /app

# Switch to non-root
USER appuser

# Expose port
EXPOSE 5000

# Capabilities: RAW sockets + bind privileged ports
ENTRYPOINT ["gunicorn", "--bind", "0.0.0.0:5000", "--worker-tmp-dir", "/dev/shm", "app:app"]
