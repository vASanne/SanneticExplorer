# Infrastructure Testing Guide

This guide covers how to build, test, and validate the Sannetic Explorer Docker infrastructure.

## Overview

The infrastructure consists of:
- **PostgreSQL Database** - Stores celestial body data and system logs
- **Redis Cache** - Handles rate limiting and job queues
- **FastAPI Backend** - REST API for data access and system management
- **SvelteKit Frontend** - 3D visualization and dashboard
- **Worker Container** - Background tasks and data updates

## Quick Start

### 1. Build and Test Infrastructure

```bash
# Complete infrastructure test (build, test, cleanup)
make infrastructure-test

# Or step by step:
make docker-build    # Build containers
make docker-test     # Start and test
make docker-clean    # Cleanup
```

### 2. Manual Testing

```bash
# Start test environment
docker-compose -f docker-compose.test.yml up -d

# Check container health
make docker-health

# Run infrastructure tests
python scripts/test_infrastructure.py

# Stop and cleanup
docker-compose -f docker-compose.test.yml down -v
```

## Test Configuration

### Ports Used
- **Database**: `5433` (PostgreSQL)
- **Redis**: `6380` (Cache)
- **Backend**: `8001` (API)
- **Frontend**: `3001` (Web UI)

### Environment Variables
The test environment uses simplified configuration:
- Database: `sannetic_explorer_test`
- User: `postgres`
- Password: `postgres`
- Debug mode enabled

## Test Coverage

### 1. Docker Container Tests
- ✅ Container accessibility
- ✅ Port availability
- ✅ Health checks
- ✅ Service dependencies

### 2. Database Tests
- ✅ Connection establishment
- ✅ Table existence
- ✅ Data availability
- ✅ Query performance
- ✅ Data integrity

### 3. Redis Tests
- ✅ Connection ping
- ✅ Basic operations (set/get/delete)
- ✅ Cache functionality

### 4. API Tests
- ✅ Health endpoint (`/health`)
- ✅ System statistics (`/stats`)
- ✅ Celestial bodies (`/bodies`)
- ✅ Planets (`/bodies/planets`)
- ✅ Moons (`/bodies/moons`)
- ✅ Stars (`/bodies/stars`)
- ✅ Update status (`/updates/status`)
- ✅ Latest updates (`/updates/latest`)

### 5. Frontend Tests
- ✅ Web accessibility
- ✅ HTTP response codes
- ✅ Content loading

### 6. Performance Tests
- ✅ API response time (< 1s)
- ✅ Database query time (< 0.1s)
- ✅ System resource usage

### 7. Data Integrity Tests
- ✅ Data consistency
- ✅ Referential integrity
- ✅ No orphaned records

## Test Reports

### JSON Report
Tests generate a detailed JSON report (`infrastructure_test_report.json`):
```json
{
  "summary": {
    "total_tests": 25,
    "passed": 23,
    "failed": 2,
    "success_rate": 92.0,
    "timestamp": "2024-01-15T10:30:00"
  },
  "results": [...],
  "recommendations": [...]
}
```

### Console Output
Real-time test results with emojis and status indicators:
```
✅ Container test-db: PostgreSQL accessible on port 5433
❌ Container test-backend: Not accessible on port 8001
   Details: Connection refused
```

## Troubleshooting

### Common Issues

#### 1. Port Conflicts
```bash
# Check if ports are in use
lsof -i :5433
lsof -i :6380
lsof -i :8001
lsof -i :3001

# Kill processes using ports
sudo kill -9 <PID>
```

#### 2. Docker Build Failures
```bash
# Clean Docker cache
docker system prune -a

# Rebuild without cache
docker-compose -f docker-compose.test.yml build --no-cache
```

#### 3. Database Connection Issues
```bash
# Check database logs
docker-compose -f docker-compose.test.yml logs test-db

# Test database connection manually
psql -h localhost -p 5433 -U postgres -d sannetic_explorer_test
```

#### 4. API Timeout Issues
```bash
# Check backend logs
docker-compose -f docker-compose.test.yml logs test-backend

# Test API manually
curl http://localhost:8001/health
```

### Performance Optimization

#### 1. Database Performance
```sql
-- Check slow queries
SELECT query, mean_time, calls 
FROM pg_stat_statements 
ORDER BY mean_time DESC 
LIMIT 10;

-- Analyze table statistics
ANALYZE celestial_bodies;
```

#### 2. Redis Performance
```bash
# Check Redis memory usage
docker exec -it <redis_container> redis-cli info memory

# Monitor Redis operations
docker exec -it <redis_container> redis-cli monitor
```

#### 3. Container Resource Usage
```bash
# Monitor container resources
docker stats

# Check container logs
docker-compose -f docker-compose.test.yml logs -f
```

## Continuous Integration

### GitHub Actions Integration
The infrastructure tests are integrated into CI:

```yaml
- name: Test Infrastructure
  run: |
    make infrastructure-test
```

### Pre-commit Hooks
Add infrastructure validation to pre-commit:

```yaml
- repo: local
  hooks:
    - id: infrastructure-test
      name: Infrastructure Test
      entry: make infrastructure-test
      language: system
      pass_filenames: false
```

## Monitoring and Alerting

### Health Check Endpoints
- Backend: `http://localhost:8001/health`
- Database: `pg_isready -h localhost -p 5433`
- Redis: `redis-cli -h localhost -p 6380 ping`

### Metrics Collection
```bash
# System metrics
docker stats --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}"

# Application metrics
curl http://localhost:8001/stats
```

## Security Considerations

### 1. Network Security
- Test containers use isolated networks
- No external access by default
- Internal communication only

### 2. Data Security
- Test database is separate from production
- No sensitive data in test environment
- Temporary data only

### 3. Container Security
- Non-root users in containers
- Minimal base images
- Regular security updates

## Best Practices

### 1. Testing Strategy
- Run tests before deployment
- Use separate test environment
- Clean up after tests
- Document test results

### 2. Performance Testing
- Set realistic thresholds
- Monitor resource usage
- Test under load
- Optimize bottlenecks

### 3. Data Management
- Use test data sets
- Backup before tests
- Clean up test data
- Validate data integrity

### 4. Monitoring
- Set up health checks
- Monitor logs
- Track performance metrics
- Alert on failures

## Advanced Testing

### Load Testing
```bash
# Install Apache Bench
sudo apt-get install apache2-utils

# Test API endpoints
ab -n 1000 -c 10 http://localhost:8001/health
ab -n 1000 -c 10 http://localhost:8001/bodies
```

### Stress Testing
```bash
# Test database connections
for i in {1..50}; do
  psql -h localhost -p 5433 -U postgres -d sannetic_explorer_test -c "SELECT 1;" &
done
wait
```

### Chaos Testing
```bash
# Simulate container failures
docker-compose -f docker-compose.test.yml kill test-backend
sleep 5
docker-compose -f docker-compose.test.yml start test-backend
```

## Conclusion

The infrastructure testing ensures:
- ✅ All services are accessible
- ✅ Data integrity is maintained
- ✅ Performance meets requirements
- ✅ System is production-ready

Regular testing helps identify issues early and ensures reliable deployment. 