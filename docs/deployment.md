# Deployment Guide

## Overview

This guide covers deploying the AI Resume Assistant to staging and production environments using Docker Compose with comprehensive monitoring, security, and observability features.

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Next.js App   │    │   FastAPI       │    │   Rust          │
│   (Frontend)    │◄──►│   Gateway       │◄──►│   Services      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Traefik       │    │  PostgreSQL     │    │     Redis       │
│   (Reverse      │    │   Database      │    │   Cache/Rate    │
│    Proxy)       │    └─────────────────┘    │    Limit        │
└─────────────────┘                          └─────────────────┘
         │
         ▼
┌─────────────────┐    ┌─────────────────┐
│   Prometheus    │    │    Grafana      │
│   Metrics       │    │  Dashboards     │
└─────────────────┘    └─────────────────┘
```

## Quick Start

### Prerequisites

- Docker and Docker Compose
- OpenRouter API key
- Google OAuth credentials (for NextAuth)
- Domain name (for production)

### 1. Environment Setup

```bash
# Copy environment template
cp apps/ai_resume_builder/.env.example .env

# Edit .env with your values
nano .env
```

Required environment variables:
```bash
OPENROUTER_API_KEY=your_openrouter_api_key
NEXTAUTH_SECRET=your_nextauth_secret
DATABASE_URL=postgresql://postgres:password@localhost:5432/ai_resume
REDIS_URL=redis://localhost:6379/0
NEXTAUTH_URL=http://localhost:3000
```

### 2. Deploy to Staging

```bash
# Deploy with health checks and validation
bash scripts/deploy.sh staging

# Or manually
docker compose -f infra/compose/compose.staging.yaml up -d
```

### 3. Deploy to Production

```bash
# Deploy with full monitoring stack
bash scripts/deploy.sh production

# Or manually
docker compose -f infra/compose/compose.prod.yaml up -d
```

## Environment Configurations

### Staging Environment

- **Database**: PostgreSQL on port 5433
- **Redis**: On port 6380
- **Gateway**: On port 8081
- **Monitoring**: Grafana on port 3001, Prometheus on port 9090
- **Lower resource limits** for cost optimization

### Production Environment

- **Database**: PostgreSQL with optimized settings
- **Redis**: Memory limits and LRU eviction
- **Gateway**: Load balanced across multiple replicas
- **Full monitoring stack** with Loki and Promtail
- **SSL/TLS** with Let's Encrypt certificates
- **Health checks** and restart policies

## Monitoring & Observability

### Accessing Dashboards

| Service | Staging URL | Production URL |
|---------|-------------|----------------|
| Application | http://localhost:8081 | https://your-domain.com |
| Grafana | http://localhost:3001 | https://grafana.your-domain.com |
| Prometheus | http://localhost:9090 | https://prometheus.your-domain.com |
| Traefik | http://localhost:8080 | https://traefik.your-domain.com |

### Default Credentials

- **Grafana**: admin / admin (change in production!)

### Key Metrics to Monitor

1. **API Performance**
   - Response times (p50, p95, p99)
   - Request rate and error rate
   - Database connection pool usage

2. **AI Costs**
   - OpenRouter API usage and costs
   - Token consumption per user
   - Monthly quota utilization

3. **System Health**
   - Service uptime and restarts
   - Resource utilization (CPU, memory, disk)
   - Database and Redis performance

4. **Security**
   - Authentication failures
   - Rate limit violations
   - GDPR request volume

## SSL/TLS Configuration

### Automatic Certificate Management

The production setup includes Traefik with Let's Encrypt integration:

```yaml
# In compose.prod.yaml
traefik:
  command:
    - "--certificatesresolvers.letsencrypt.acme.tlschallenge=true"
    - "--certificatesresolvers.letsencrypt.acme.email=admin@yourdomain.com"
```

### Manual Certificate Setup

For custom certificates:

```bash
# Place certificates in ./certs/
docker compose -f infra/compose/compose.prod.yaml up -d
```

## Scaling

### Horizontal Scaling

```bash
# Scale specific services
docker compose -f infra/compose/compose.prod.yaml up -d --scale gateway=3 --scale intel-svc=2

# Update services with zero downtime
docker compose -f infra/compose/compose.prod.yaml up -d --no-deps gateway
```

### Database Scaling

For high-traffic scenarios, consider:

- **Read replicas** for analytics queries
- **Connection pooling** with PgBouncer
- **Database sharding** for user data

## Backup & Recovery

### Database Backups

```bash
# Create backup
docker compose -f infra/compose/compose.prod.yaml exec postgres pg_dump -U postgres ai_resume_prod > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore from backup
docker compose -f infra/compose/compose.prod.yaml exec -T postgres psql -U postgres ai_resume_prod < backup.sql
```

### Volume Backups

```bash
# Backup all volumes
docker run --rm -v ai_resume_postgres_prod_data:/data -v $(pwd)/backups:/backup alpine tar czf /backup/postgres_backup.tar.gz /data

# Restore volumes
docker run --rm -v ai_resume_postgres_prod_data:/data -v $(pwd)/backups:/backup alpine sh -c "cd / && tar xzf /backup/postgres_backup.tar.gz"
```

## Troubleshooting

### Common Issues

1. **Database Connection Failed**
   ```bash
   # Check database logs
   docker compose -f infra/compose/compose.prod.yaml logs postgres

   # Verify environment variables
   docker compose -f infra/compose/compose.prod.yaml exec postgres env
   ```

2. **Service Won't Start**
   ```bash
   # Check service logs
   docker compose -f infra/compose/compose.prod.yaml logs [service-name]

   # Restart specific service
   docker compose -f infra/compose/compose.prod.yaml restart [service-name]
   ```

3. **High Memory Usage**
   ```bash
   # Check resource usage
   docker stats

   # Scale down if needed
   docker compose -f infra/compose/compose.prod.yaml up -d --scale [service]=1
   ```

### Health Checks

```bash
# Check all services
docker compose -f infra/compose/compose.prod.yaml ps

# Verify health endpoints
curl http://localhost:8080/healthz
curl http://localhost:8080/v1/models
```

## Security Considerations

### Production Security

1. **Secrets Management**
   - Use Docker secrets or external secret managers
   - Rotate API keys regularly
   - Never commit secrets to version control

2. **Network Security**
   - Use internal networks for service communication
   - Expose only necessary ports
   - Implement firewall rules

3. **Access Control**
   - Configure strong passwords for databases
   - Use SSH keys for server access
   - Implement proper user permissions

### Compliance

- **GDPR**: Data export and deletion endpoints available
- **Data Retention**: Automated cleanup policies
- **Audit Logging**: All access and changes logged
- **Encryption**: TLS for all external communications

## Performance Optimization

### Database Optimization

```sql
-- Add recommended indexes
CREATE INDEX CONCURRENTLY idx_usage_events_user_created ON usage_events(user_id, created_at DESC);
CREATE INDEX CONCURRENTLY idx_resumes_user_created ON resumes(user_id, created_at DESC);
CREATE INDEX CONCURRENTLY idx_rate_limits_user ON rate_limits(user_id);

-- Analyze query performance
EXPLAIN ANALYZE SELECT * FROM usage_events WHERE user_id = $1 ORDER BY created_at DESC LIMIT 10;
```

### Caching Strategy

- **API responses**: Cache model lists and static data
- **Database queries**: Cache frequently accessed user data
- **AI responses**: Cache similar prompts (with privacy considerations)

### CDN Configuration

For global performance:

```bash
# Configure CDN for static assets
# Update Next.js config for CDN base path
# Set up geo-replication for uploads
```

## Cost Optimization

### Monitoring Costs

1. **Database**: Right-size instances based on usage
2. **Redis**: Monitor memory usage and hit rates
3. **AI APIs**: Track token usage and optimize prompts
4. **Bandwidth**: Implement caching and compression

### Auto-scaling

```bash
# Scale based on CPU/memory usage
docker compose -f infra/compose/compose.prod.yaml up -d --scale gateway=5
```

## Support & Maintenance

### Regular Tasks

1. **Weekly**
   - Review error logs and metrics
   - Check database performance
   - Update dependencies

2. **Monthly**
   - Review cost reports
   - Update SSL certificates
   - Backup verification

3. **Quarterly**
   - Security audit
   - Performance review
   - Dependency updates

### Getting Help

- **Logs**: `docker compose logs [service-name]`
- **Metrics**: Grafana dashboards
- **Health**: `/healthz` endpoint
- **Documentation**: This deployment guide

## Emergency Procedures

### Service Recovery

```bash
# Stop all services
docker compose -f infra/compose/compose.prod.yaml down

# Start core services first
docker compose -f infra/compose/compose.prod.yaml up -d postgres redis

# Wait for healthy state
sleep 30

# Start application services
docker compose -f infra/compose/compose.prod.yaml up -d
```

### Data Recovery

```bash
# From backup
docker compose -f infra/compose/compose.prod.yaml down
# Restore volumes from backup
# Restart services
docker compose -f infra/compose/compose.prod.yaml up -d
```

## API Reference

### Gateway Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/healthz` | GET | Health check |
| `/v1/apply` | POST | Create resume application |
| `/v1/models` | GET | List available AI models |
| `/v1/costs` | GET | Get usage statistics |
| `/v1/export` | GET | Export user data (GDPR) |
| `/v1/delete` | DELETE | Delete user data (GDPR) |

### Authentication

- **Frontend**: NextAuth with Google OAuth
- **API**: JWT bearer tokens
- **Admin**: Email-based access control

---

*For questions or issues, please refer to the troubleshooting section or check the service logs.*