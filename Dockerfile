FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    nmap \
    curl \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt
RUN echo 'vm.max_map_count=262144' >> /etc/sysctl.conf && \
    echo 'ulimit -v 500000' >> /etc/profile && \
    sysctl -p

ENV PYTHONUNBUFFERED=1
ENV NMAP_ARGS="--unprivileged --max-parallelism 50"

# Your existing:
CMD ["gunicorn", "app:app", "-w", "1", "--threads", "4", "--timeout", "300", "-b", "0.0.0.0:10000"]
EXPOSE 5000
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers=1", "--threads=4", "app:app"]
