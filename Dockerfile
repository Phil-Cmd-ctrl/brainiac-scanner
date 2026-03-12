FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    nmap \
    curl \
    procps \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt

# Add capabilities to nmap binary (no root needed)
RUN setcap cap_net_raw,cap_net_bind_service,cap_net_admin+eip /usr/bin/nmap

EXPOSE 5000
ENTRYPOINT ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
