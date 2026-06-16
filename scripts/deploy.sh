#!/bin/bash
set -e

echo "Starting deployment process on EC2..."

# 1. Login to ECR
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $ECR_REGISTRY

# 2. Pull the latest image
echo "Pulling latest docker images..."
docker-compose -f docker-compose.prod.yml pull

# 3. Run Database Migrations in a temporary container
echo "Running database migrations..."
docker-compose -f docker-compose.prod.yml run --rm backend alembic upgrade head

# 4. Restart services
echo "Starting production services..."
docker-compose -f docker-compose.prod.yml up -d --remove-orphans

echo "Deployment complete! Checking health..."
sleep 5
docker ps | grep attendance_backend_prod
