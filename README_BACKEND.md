# Sannetic Explorer Backend

A comprehensive FastAPI backend for solar system simulation with PostgreSQL database, featuring celestial body data management, orbital calculations, and real-time simulation capabilities.

## 🚀 Features

### Core Functionality
- **Celestial Body Management**: Complete CRUD operations for stars, planets, moons, satellites, and spacecraft
- **Orbital Calculations**: Precise orbital parameters and propagation using astronomical algorithms
- **Physical Characteristics**: Detailed physical properties including mass, radius, atmosphere, and magnetic fields
- **Stellar Data**: Comprehensive star data including spectral types, luminosity, and evolutionary stages
- **Spacecraft Missions**: Mission tracking, launch data, and exploration history
- **TLE Elements**: Two-Line Element sets for satellite tracking and orbital prediction
- **Simulation Engine**: Real-time 3D position and velocity calculations

### Technical Features
- **FastAPI**: Modern, fast web framework with automatic API documentation
- **PostgreSQL**: Robust relational database with advanced indexing and custom functions
- **SQLAlchemy**: Powerful ORM with relationship management and data validation
- **Redis**: Caching layer and message broker for background tasks
- **Celery**: Asynchronous task processing for data updates and calculations
- **Docker**: Containerized deployment with health checks and orchestration

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   FastAPI App   │    │   PostgreSQL    │    │     Redis       │
│   (Port 8000)   │◄──►│   (Port 5432)   │    │   (Port 6379)   │
│ host: 13800     │    │ host: 15432     │    │ host: 16379     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Celery Worker  │    │  Celery Beat    │    │     Flower      │
│ (Background)    │    │ (Scheduler)     │    │ (Monitoring)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Database Schema

The backend uses a comprehensive relational database schema with the following main tables:

- **celestial_bodies**: Core celestial body information
- **orbital_parameters**: Detailed orbital elements and calculations
- **physical_characteristics**: Physical properties and composition
- **stellar_characteristics**: Star-specific data and classification
- **spacecraft_missions**: Mission information and tracking
- **tle_elements**: Two-Line Element sets for satellites
- **exploration_history**: Historical exploration events
- **simulation_state**: Real-time simulation data

## 🛠️ Installation & Setup

### Prerequisites
- Docker and Docker Compose
- Git
- At least 4GB RAM available for containers

### Quick Start

1. **Clone and navigate to the project**:
```bash
cd SanneticExplorer
```

2. **Set up environment variables** (optional):
```bash
cp env.example .env
# Edit .env with your API keys and configuration
```

3. **Run the complete setup**:
```bash
make -f Makefile.backend setup
```

This will:
- Build all Docker containers
- Start PostgreSQL and Redis
- Initialize the database
- Migrate existing JSON data to PostgreSQL
- Start the FastAPI application

### Manual Setup

If you prefer manual setup:

```bash
# Build containers
make -f Makefile.backend build

# Start services
make -f Makefile.backend up

# Initialize database
make -f Makefile.backend db-init

# Migrate data
make -f Makefile.backend db-migrate
```

## 📊 API Endpoints

### Core Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/stats` | GET | System statistics |
| `/docs` | GET | Interactive API documentation |
| `/redoc` | GET | Alternative API documentation |

### Celestial Bodies

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/celestial-bodies` | GET | List all celestial bodies |
| `/celestial-bodies/{id}` | GET | Get detailed celestial body info |
| `/celestial-bodies/search/{name}` | GET | Search celestial bodies by name |
| `/solar-system` | GET | Get complete solar system hierarchy |

### Specialized Data

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/orbital-parameters/{id}` | GET | Get orbital parameters |
| `/physical-characteristics/{id}` | GET | Get physical characteristics |
| `/stellar-characteristics/{id}` | GET | Get stellar characteristics |
| `/spacecraft-missions/{id}` | GET | Get spacecraft missions |
| `/tle-elements/{id}` | GET | Get TLE elements |
| `/simulation-state/{id}` | GET | Get simulation state |

## 🗄️ Database Management

### Basic Operations

```bash
# Initialize database (create tables)
make -f Makefile.backend db-init

# Migrate JSON data to PostgreSQL
make -f Makefile.backend db-migrate

# Reset database (drop and recreate)
make -f Makefile.backend db-reset

# Create backup
make -f Makefile.backend db-backup

# Restore from backup
make -f Makefile.backend db-restore BACKUP_FILE=backups/filename.sql

# Connect to PostgreSQL shell
make -f Makefile.backend db-shell
```

### Database Functions

The PostgreSQL database includes custom functions for advanced queries:

- `get_celestial_hierarchy(body_id)`: Get hierarchical structure
- `search_celestial_bodies(search_term)`: Full-text search
- `get_orbital_statistics()`: Orbital parameter statistics
- `get_physical_statistics()`: Physical property statistics
- `get_exploration_statistics()`: Exploration history statistics
- `get_simulation_state_at_time(target_time)`: Historical simulation data

## 🔧 Development

### Development Environment

```bash
# Start development environment
make -f Makefile.backend dev

# Run tests
make -f Makefile.backend test

# Code formatting
make -f Makefile.backend format

# Linting
make -f Makefile.backend lint

# Connect to container shell
make -f Makefile.backend shell
```

### Project Structure

```
backend/
├── models.py              # SQLAlchemy models
├── database.py            # Database configuration
├── app.py                 # FastAPI application
├── data_migration.py      # JSON to PostgreSQL migration
├── requirements_backend.txt # Python dependencies
├── docker-compose.backend.yml # Docker services
├── Dockerfile.backend     # Backend container
├── Makefile.backend       # Development commands
├── init-db.sql           # Database initialization
└── README_BACKEND.md     # This file
```

## 📈 Monitoring & Maintenance

### Health Monitoring

```bash
# Check API health
make -f Makefile.backend health

# Get system statistics
make -f Makefile.backend stats

# Open Celery monitoring
make -f Makefile.backend flower
```

### Performance Monitoring

```bash
# Database performance
make -f Makefile.backend performance

# Database maintenance
make -f Makefile.backend db-maintenance
```

### Logs

```bash
# View all logs
make -f Makefile.backend logs

# View specific service logs
docker compose -p sannetic-explorer-backend -f docker-compose.backend.yml logs backend
docker compose -p sannetic-explorer-backend -f docker-compose.backend.yml logs postgres
```

## 🚀 Production Deployment

### Production Setup

```bash
# Deploy to production
make -f Makefile.backend deploy
```

### Environment Variables

Create a `.env` file with production settings:

```env
# Database
DB_HOST=postgres
DB_PORT=5432
DB_NAME=sannetic_explorer
DB_USER=postgres
DB_PASSWORD=secure_password
DB_ECHO=false

# Redis
REDIS_HOST=redis
REDIS_PORT=6379

# API
API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=false

# Security
CORS_ORIGINS=https://yourdomain.com
SECRET_KEY=your_secret_key

# External APIs
N2YO_API_KEY=your_n2yo_key
SPACE_TRACK_USERNAME=your_username
SPACE_TRACK_PASSWORD=your_password
OPENAI_API_KEY=your_openai_key
```

## 🔒 Security Considerations

### Production Security

1. **Database Security**:
   - Use strong passwords
   - Enable SSL connections
   - Restrict network access
   - Regular backups

2. **API Security**:
   - Enable CORS restrictions
   - Use HTTPS in production
   - Implement rate limiting
   - Add authentication if needed

3. **Container Security**:
   - Keep images updated
   - Use non-root users
   - Scan for vulnerabilities
   - Monitor resource usage

## 🐛 Troubleshooting

### Common Issues

1. **Database Connection Failed**:
   ```bash
   # Check if PostgreSQL is running
   make -f Makefile.backend status
   
   # Restart services
   make -f Makefile.backend restart
   ```

2. **Migration Errors**:
   ```bash
   # Reset database and retry
   make -f Makefile.backend db-reset
   make -f Makefile.backend db-migrate
   ```

3. **API Not Responding**:
   ```bash
   # Check health
   make -f Makefile.backend health
   
   # Check logs
   make -f Makefile.backend logs
   ```

4. **Memory Issues**:
   ```bash
   # Check resource usage
   docker stats
   
   # Clean up
   make -f Makefile.backend prune
   ```

### Emergency Commands

```bash
# Emergency stop all services
make -f Makefile.backend emergency-stop

# Emergency restart
make -f Makefile.backend emergency-restart
```

## 📚 API Documentation

Once the backend is running (`docker compose -p sannetic-explorer-backend -f docker-compose.backend.yml up -d`), visit:
- **Interactive Docs**: http://localhost:13800/docs
- **ReDoc**: http://localhost:13800/redoc
- **Celery Monitoring**: http://localhost:15555

Those are the published host ports. Inside the Compose network the API still listens on 8000, Postgres on 5432, Redis on 6379, and Flower on 5555. The main web stack (`make up`) uses the same host ports for API, Postgres, and Redis under project name `sannetic-explorer`; do not run both stacks together.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `make -f Makefile.backend test`
5. Format code: `make -f Makefile.backend format`
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Check the troubleshooting section
- Review the API documentation
- Open an issue on GitHub
- Check the logs for error details

---

**Note**: This backend is designed to work with the existing Sannetic Explorer data structure and can be extended for additional celestial body types and simulation features. 