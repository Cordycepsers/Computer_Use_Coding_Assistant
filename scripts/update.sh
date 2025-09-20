#!/bin/bash

echo "Updating Computer Use Coding Assistant..."

# Pull latest images
docker-compose pull

# Rebuild custom image
docker-compose build --no-cache

# Restart services
docker-compose down
docker-compose up -d

echo "Update complete!"
