FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt && \
    apt-get update && apt-get install -y wget && \
    wget -O /usr/local/bin/wait-for-it.sh https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh && \
    chmod +x /usr/local/bin/wait-for-it.sh && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY . .

RUN sed -i 's/build: \./image: mertismk\/fridge_planner/' docker-compose.yml && \
    sed -i 's/volumes:/# volumes:/' docker-compose.yml && \
    sed -i 's/  - .\/app/  # - .\/app/' docker-compose.yml && \
    chmod +x start.sh

EXPOSE 5000

CMD ["./start.sh"] 