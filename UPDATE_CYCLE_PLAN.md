# Sannetic Explorer Update Cycle Plan

## Overview

This document outlines the optimal update cycle strategy for the Sannetic Explorer container to maintain fresh data while respecting API limits, minimizing costs, and ensuring system reliability.

## Current State Analysis

### Data Freshness Requirements
- **Orbital Elements**: Change daily due to atmospheric drag and perturbations
- **Satellite Positions**: Change every few minutes for real-time tracking
- **Wikipedia Data**: Changes infrequently (weeks/months)
- **Launch/Mission Data**: Changes rarely (months/years)

### API Constraints
- **Celestrak**: ~300 calls/hour (very generous, batch-friendly)
- **N2YO**: 200 calls/hour (expensive for individual satellites)
- **Space-Track**: 100 calls/hour (rate-limited, requires authentication)
- **Wikipedia**: 600 calls/hour (generous, batch-friendly)

### Current Data Status
- **358 total celestial objects** across 5 categories
- **29 satellites** in active tracking
- **Last update**: Manual execution only
- **Cache TTL**: 24 hours (good for optimization)

## Recommended Update Cycle Strategy

### 🕐 **Tier 1: Critical Real-Time Data (Every 6 Hours)**
**Target**: Top 5 priority satellites (ISS, Hubble, major navigation satellites)
**Sources**: Celestrak (batch) + N2YO (individual)
**API Impact**: ~6 calls total
**Command**: `make update-critical`

```bash
# Updates only the most important satellites with real-time data
- ISS position and orbit
- Hubble Space Telescope
- GPS/Galileo/GLONASS constellation status
- Emergency/rescue satellites
```

### 🕕 **Tier 2: Standard Updates (Every 12 Hours)**
**Target**: All 29 active satellites
**Sources**: Celestrak (batch) + Wikipedia (batch) + Space-Track (limited)
**API Impact**: ~15 calls total
**Command**: `make update-optimized`

```bash
# Full optimized update using batch processing
- All satellite orbital elements
- Wikipedia descriptions (cached)
- Space-Track verification data
- System health checks
```

### 🕛 **Tier 3: Full System Update (Daily at 02:00 UTC)**
**Target**: All 358 celestial objects + system maintenance
**Sources**: All APIs + data validation + cleanup
**API Impact**: ~50 calls total
**Command**: `make update-full`

```bash
# Comprehensive system update and maintenance
- All satellites, planets, natural satellites
- Index file updates
- Data validation and cleanup
- Log rotation and system health
- Cache optimization
```

### 📅 **Tier 4: Deep Maintenance (Weekly - Sunday 01:00 UTC)**
**Target**: System optimization + data enrichment
**Sources**: All APIs + external validation
**API Impact**: ~100 calls total
**Command**: `make update-weekly`

```bash
# Deep system maintenance and optimization
- Data structure validation
- API credential testing
- Performance optimization
- Database cleanup and indexing
- Backup and archival
```

## Implementation Plan

### Phase 1: Create Update Tiers (Immediate)

#### 1. Critical Update Script
```python
# scripts/update_critical.py
- Update top 5 satellites only
- Real-time position data
- Emergency status monitoring
- Fast execution (< 2 minutes)
```

#### 2. Enhanced Makefile Commands
```makefile
update-critical:   # Every 6 hours
update-standard:   # Every 12 hours  
update-full:       # Daily
update-weekly:     # Weekly maintenance
```

#### 3. Update Scheduler Script
```python
# scripts/update_scheduler.py
- Intelligent scheduling logic
- API rate limit monitoring
- Failure recovery and retry
- Health status reporting
```

### Phase 2: Container Automation (Next)

#### 1. Cron Integration
```dockerfile
# Add cron to container
RUN apt-get update && apt-get install -y cron
COPY crontab /etc/cron.d/sannetic-cron
```

#### 2. Cron Schedule
```cron
# /etc/cron.d/sannetic-cron
0 */6 * * * root cd /app && make update-critical >> /var/log/cron.log 2>&1
0 */12 * * * root cd /app && make update-standard >> /var/log/cron.log 2>&1
0 2 * * * root cd /app && make update-full >> /var/log/cron.log 2>&1
0 1 * * 0 root cd /app && make update-weekly >> /var/log/cron.log 2>&1
```

#### 3. Health Monitoring
```python
# scripts/health_monitor.py
- API quota monitoring
- Update success/failure tracking
- Alert system for failures
- Performance metrics
```

### Phase 3: Advanced Features (Future)

#### 1. Dynamic Scheduling
```python
# Adjust update frequency based on:
- Satellite orbital decay rates
- Mission criticality
- API quota availability
- System load
```

#### 2. Intelligent Caching
```python
# Cache optimization:
- Extend cache for stable data
- Reduce cache for dynamic data
- Predictive cache warming
- Cache compression
```

#### 3. Distributed Updates
```python
# Spread updates across time:
- Randomize update times
- Load balancing across APIs
- Geographic API selection
- Fallback API sources
```

## API Usage Optimization

### Daily API Budget (Conservative)
```
Celestrak:    50/300 calls  (17% utilization)
Wikipedia:   100/600 calls  (17% utilization)
Space-Track:  20/100 calls  (20% utilization)
N2YO:         30/200 calls  (15% utilization)
Total: ~200 calls/day (well within limits)
```

### Peak Usage Distribution
```
06:00 UTC: Critical Update    (20 calls)
12:00 UTC: Standard Update    (40 calls)
18:00 UTC: Critical Update    (20 calls)
02:00 UTC: Full Update       (80 calls)
01:00 UTC: Weekly Update     (40 calls - Sundays only)
```

### Failure Recovery Strategy
```python
# If API fails:
1. Use cached data (up to 48 hours old)
2. Try alternative API sources
3. Reduce update frequency temporarily
4. Alert administrators
5. Graceful degradation
```

## Container Update Commands

### Immediate Implementation
```bash
# Create the update tier scripts
make setup-update-tiers

# Test the new update system
make test-update-cycle

# Deploy automated updates
make deploy-automation
```

### Manual Control
```bash
# Force immediate updates
make update-critical-now
make update-standard-now
make update-full-now

# Check update status
make update-status
make api-health-check

# Emergency commands
make update-emergency    # Fastest possible update
make update-offline      # Use only cached data
```

## Monitoring and Alerting

### Health Checks
```python
# Automated monitoring:
- API response times
- Data freshness indicators
- Update success rates
- System resource usage
- Cache hit/miss ratios
```

### Alert Conditions
```python
# Alert when:
- API quota > 80% used
- Update failures > 3 consecutive
- Data age > 48 hours
- Disk space < 500MB
- System load > 80%
```

### Reporting Dashboard
```python
# Daily reports:
- Update statistics
- API usage summary
- Data quality metrics
- System performance
- Error logs summary
```

## Benefits of This Strategy

### ✅ **Reliability**
- Multiple update tiers ensure data availability
- Graceful degradation during API issues
- Comprehensive error handling and recovery

### ✅ **Efficiency**
- Optimized API usage (15-20% of limits)
- Intelligent caching reduces redundant calls
- Batch processing minimizes API overhead

### ✅ **Freshness**
- Critical data updated every 6 hours
- Standard data updated every 12 hours
- Complete system refresh daily

### ✅ **Scalability**
- Easy to add new satellites or data sources
- Flexible scheduling for different priorities
- Resource usage scales with system capacity

### ✅ **Maintainability**
- Clear separation of update responsibilities
- Comprehensive logging and monitoring
- Automated health checks and alerts

## Risk Mitigation

### API Rate Limiting
- **Conservative limits**: Use only 15-20% of available quotas
- **Distributed timing**: Spread calls across different hours
- **Fallback sources**: Multiple APIs for critical data
- **Circuit breakers**: Automatic throttling on errors

### Data Consistency
- **Atomic updates**: All-or-nothing data updates
- **Validation checks**: Verify data integrity before saving
- **Rollback capability**: Restore previous data on corruption
- **Checksums**: Detect data corruption early

### System Reliability
- **Resource monitoring**: CPU, memory, disk usage
- **Graceful degradation**: Reduce functionality vs. complete failure
- **Health endpoints**: Easy monitoring integration
- **Automated recovery**: Restart services on failure

## Future Enhancements

### Short Term (1-2 weeks)
- Implement Tier 1 and Tier 2 updates
- Add cron scheduling to container
- Create health monitoring dashboard

### Medium Term (1-2 months)
- Add intelligent scheduling based on orbital mechanics
- Implement predictive caching
- Add external monitoring integration

### Long Term (3-6 months)
- Machine learning for optimal update timing
- Multi-region API distribution
- Real-time streaming for critical satellites
- Integration with space situational awareness networks

---

This update cycle plan ensures that Sannetic Explorer maintains fresh, accurate data while operating well within API limits and providing reliable service to users. 