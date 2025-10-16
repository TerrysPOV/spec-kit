#!/bin/bash
set -euo pipefail

# AI Resume Assistant Deployment Script
# Supports staging and production deployments with health checks

ENVIRONMENT="${1:-staging}"
COMPOSE_FILE=""

echo "🚀 Deploying AI Resume Assistant to $ENVIRONMENT"

# Determine compose file based on environment
case "$ENVIRONMENT" in
  staging)
    COMPOSE_FILE="infra/compose/compose.staging.yaml"
    ;;
  production)
    COMPOSE_FILE="infra/compose/compose.prod.yaml"
    ;;
  *)
    echo "❌ Invalid environment: $ENVIRONMENT"
    echo "Usage: $0 [staging|production]"
    exit 1
    ;;
esac

# Check if compose file exists
if [[ ! -f "$COMPOSE_FILE" ]]; then
  echo "❌ Compose file not found: $COMPOSE_FILE"
  exit 1
fi

# Load environment variables
if [[ -f ".env" ]]; then
  source .env
  echo "✅ Loaded environment variables from .env"
else
  echo "⚠️  No .env file found, using system environment variables"
fi

# Pre-deployment checks
echo "🔍 Running pre-deployment checks..."

# Check required environment variables
REQUIRED_VARS=(
  "OPENROUTER_API_KEY"
  "NEXTAUTH_SECRET"
  "DATABASE_URL"
  "REDIS_URL"
)

for var in "${REQUIRED_VARS[@]}"; do
  if [[ -z "${!var:-}" ]]; then
    echo "❌ Required environment variable $var is not set"
    exit 1
  fi
done

echo "✅ All required environment variables are set"

# Database migration
echo "🗄️  Running database migrations..."
cd apps/ai_resume_builder/gateway
if command -v alembic &> /dev/null; then
  alembic upgrade head
  echo "✅ Database migrations completed"
else
  echo "⚠️  Alembic not found, skipping migrations"
fi
cd ../../..

# Deploy services
echo "🐳 Deploying services with Docker Compose..."
docker compose -f "$COMPOSE_FILE" up -d

# Wait for services to be healthy
echo "⏳ Waiting for services to become healthy..."

# Function to check service health
check_service_health() {
  local service=$1
  local max_attempts=30
  local attempt=1

  while [[ $attempt -le $max_attempts ]]; do
    echo "  Checking $service health (attempt $attempt/$max_attempts)..."

    case "$service" in
      gateway)
        if curl -f http://localhost:8080/healthz &>/dev/null; then
          echo "    ✅ Gateway is healthy"
          return 0
        fi
        ;;
      postgres)
        if docker compose -f "$COMPOSE_FILE" exec -T postgres pg_isready -U postgres &>/dev/null; then
          echo "    ✅ PostgreSQL is healthy"
          return 0
        fi
        ;;
      redis)
        if docker compose -f "$COMPOSE_FILE" exec -T redis redis-cli ping | grep -q PONG; then
          echo "    ✅ Redis is healthy"
          return 0
        fi
        ;;
    esac

    sleep 10
    ((attempt++))
  done

  echo "    ❌ $service failed to become healthy"
  return 1
}

# Check core services
CORE_SERVICES=("postgres" "redis" "gateway")
for service in "${CORE_SERVICES[@]}"; do
  if ! check_service_health "$service"; then
    echo "❌ Deployment failed: $service is not healthy"
    echo "🔍 Checking logs..."
    docker compose -f "$COMPOSE_FILE" logs "$service"
    exit 1
  fi
done

echo "✅ All core services are healthy"

# Post-deployment validation
echo "🧪 Running post-deployment validation..."

# Test API endpoints
API_TESTS=(
  "http://localhost:8080/healthz"
  "http://localhost:8080/v1/models"
)

for endpoint in "${API_TESTS[@]}"; do
  if curl -f "$endpoint" &>/dev/null; then
    echo "  ✅ $endpoint is accessible"
  else
    echo "  ❌ $endpoint is not accessible"
    exit 1
  fi
done

# Test database connectivity
if docker compose -f "$COMPOSE_FILE" exec -T postgres psql -U postgres -d ai_resume -c "SELECT 1;" &>/dev/null; then
  echo "  ✅ Database connectivity verified"
else
  echo "  ❌ Database connectivity failed"
  exit 1
fi

echo "🎉 Deployment completed successfully!"
echo ""
echo "📊 Service Status:"
docker compose -f "$COMPOSE_FILE" ps

echo ""
echo "🔗 Access URLs:"
if [[ "$ENVIRONMENT" == "staging" ]]; then
  echo "  • Application: http://localhost:8081"
  echo "  • Traefik Dashboard: http://localhost:8080"
  echo "  • Grafana: http://localhost:3001"
  echo "  • Prometheus: http://localhost:9090"
else
  echo "  • Application: https://your-domain.com"
  echo "  • Traefik Dashboard: https://traefik.your-domain.com"
  echo "  • Grafana: https://grafana.your-domain.com"
  echo "  • Prometheus: https://prometheus.your-domain.com"
fi

echo ""
echo "📋 Next Steps:"
echo "  1. Update DNS records to point to your server"
echo "  2. Configure SSL certificates in Traefik dashboard"
echo "  3. Set up monitoring alerts in Grafana"
echo "  4. Test the full user journey"
echo "  5. Set up log aggregation and backup strategies"

echo ""
echo "✅ Deployment script completed successfully!"