#!/bin/bash

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="backups/backup_${TIMESTAMP}"

echo "Creating backup in ${BACKUP_DIR}..."

mkdir -p ${BACKUP_DIR}

# Backup workspace and projects
cp -r workspace ${BACKUP_DIR}/
cp -r projects ${BACKUP_DIR}/
cp -r logs ${BACKUP_DIR}/

# Backup configuration
cp .env ${BACKUP_DIR}/
cp docker-compose.yml ${BACKUP_DIR}/

echo "Backup complete: ${BACKUP_DIR}"
