#!/bin/bash

# Basisstruktur erstellen
mkdir -p kudos-blockchain/{blockchain/core,blockchain/consensus,tests,docker}

# Wichtige Dateien anlegen
touch kudos-blockchain/blockchain/__init__.py
touch kudos-blockchain/.env
touch kudos-blockchain/requirements.txt
touch kudos-blockchain/README.md

# Docker-Dateien
cat <<EOL > kudos-blockchain/docker/Dockerfile
# Minimaler Python-Container
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python", "-m", "blockchain.core"]
EOL

cat <<EOL > kudos-blockchain/docker/docker-compose.yml
version: "3.9"
services:
  kudos-blockchain:
    build:
      context: ..
      dockerfile: docker/Dockerfile
    container_name: kudos-blockchain
    environment:
      - PYTHONUNBUFFERED=1
    networks:
      - kudos-network
networks:
  kudos-network:
    name: kudos-network
EOL

echo "Projektstruktur erstellt. Du kannst nun mit der Entwicklung beginnen!"