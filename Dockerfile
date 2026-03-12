FROM python:3.11-slim

# Full nmap install + security tools
RUN apt-get update && apt-get install -y \
    nmap \
    curl \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt

# Nmap config: disable raw sockets where possible, enable IPv4
RUN echo "target_ipv4_wait_times=1000" > /root/.nmap/nmap.conf \
    && echo "target_ipv6_wait_times=1000" >> /root/.nmap/nmap.conf

EXPOSE 5000
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers=1", "--threads=4", "app:app"]
