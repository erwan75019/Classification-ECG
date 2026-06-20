#!/bin/bash

set -e

echo "Stopping containers..."
docker compose down

echo "Building images..."
docker compose build

echo "Starting application..."
docker compose up
