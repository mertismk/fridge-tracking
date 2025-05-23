FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .

RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential libssl-dev wget && \
    pip install --no-cache-dir -r requirements.txt && \
    apt-get purge -y --auto-remove build-essential libssl-dev && \
    wget -O /usr/local/bin/wait-for-it.sh https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh && \
    chmod +x /usr/local/bin/wait-for-it.sh && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    mkdir -p /app/prometheus_metrics_data && \
    chmod 777 /app/prometheus_metrics_data

COPY . .

RUN sed -i 's/build: \./image: mertismk\/fridge_planner/' docker-compose.yml && \
    sed -i 's/volumes:/# volumes:/' docker-compose.yml && \
    sed -i 's/  - .\/app/  # - .\/app/' docker-compose.yml && \
    chmod +x start.sh

EXPOSE 5000

CMD ["./start.sh"]