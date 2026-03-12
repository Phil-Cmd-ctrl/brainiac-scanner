FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    nmap \
    curl \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers=1", "--threads=4", "app:app"]
