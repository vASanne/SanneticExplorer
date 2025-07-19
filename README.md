# Sannetic Explorer

A comprehensive space exploration data management system that collects, validates, and enriches data about celestial bodies and spacecraft.

## Project Status

🔧 **API Integration Complete** - All API credentials are configured and tested. Current status:

- **Total Files**: 358 celestial objects across 5 categories
- **API Status**: 
  - ✅ N2YO API: Connected and configured
  - ✅ Space-Track: Connected and configured  
  - ⚠️ NASA ADS: Authentication needs refresh
  - ❌ HEASARC: Connection issues
- **Data Quality**: Structure fixes applied, working on data enrichment
- **Next Phase**: Completing missing field population and final validation

Use `make status` to get the latest project status report.

## Prerequisites

- Docker and Docker Compose
- Git
- Python 3.12+ (for local development)
- API keys for:
  - N2YO (satellite tracking)
  - Space-Track (satellite information)

## Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd SanneticExplorer
```

2. Create a `.env` file in the project root:
```bash
# N2YO API Key for satellite tracking data
N2YO_API_KEY=your_n2yo_api_key_here

# Space-Track credentials for detailed satellite information
SPACE_TRACK_USERNAME=your_space_track_username_here
SPACE_TRACK_PASSWORD=your_space_track_password_here
```

3. Create required data directories:
```bash
mkdir -p Data/{Planets,NaturalSatellites,Spacecraft,Stars}
```

4. (Optional) Install pre-commit hooks for development:
```bash
pip install pre-commit
pre-commit install
```

## Running the Project

All Python scripts must be run within the Sannetic Explorer Docker container to ensure consistent dependencies and environment.

### Quick Commands (Makefile)

The easiest way to interact with the system:

```bash
make build        # Build the Docker container
make sh          # Connect to the container shell
make update-data # Run all update/insert scripts
make status      # Show project status and API credentials
make clean       # Remove the container and its volumes
```

### Manual Script Execution

To run individual scripts manually:
```bash
# Update templates
docker compose run --rm sannetic-explorer python scripts/update_templates.py

# Validate data
docker compose run --rm sannetic-explorer python scripts/validate_data.py

# Enrich data sources
docker compose run --rm sannetic-explorer python scripts/enrich_data_sources.py

# Update index files
docker compose run --rm sannetic-explorer python scripts/update_index_files.py

# Create satellite files
docker compose run --rm sannetic-explorer python scripts/create_satellite_files.py
```

### Development

For development work, you can start an interactive shell in the container:
```bash
make sh
# or manually:
docker compose run --rm sannetic-explorer bash
```

#### Code Quality

This project uses pre-commit hooks to ensure code quality. The hooks run automatically on commit and include:

- **Black**: Code formatting
- **Ruff**: Fast Python linting and formatting
- **MyPy**: Static type checking (strict mode)
- **isort**: Import sorting
- **Pre-commit hooks**: Basic file checks

To install the hooks:
```bash
pip install pre-commit
pre-commit install
```

To run the hooks manually:
```bash
pre-commit run --all-files
```

## Project Structure

```
SanneticExplorer/
├── Data/                    # Data directory (mounted in container)
│   ├── Planets/
│   ├── NaturalSatellites/
│   ├── Spacecraft/
│   └── Stars/
├── sannetic_explorer/       # Main Python package
│   ├── api/                # FastAPI application
│   ├── models/             # SQLAlchemy models
│   ├── services/           # Database and external services
│   ├── cron/               # Scheduled tasks
│   └── tests/              # Test suite
├── scripts/
│   ├── update_templates.py
│   ├── validate_data.py
│   ├── enrich_data_sources.py
│   ├── update_index_files.py
│   └── create_satellite_files.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── pyproject.toml          # Modern Python packaging
├── .pre-commit-config.yaml # Pre-commit hooks configuration
├── RULES.md                # Project rules and guidelines
└── .env
```

## Data Rules

See [RULES.md](RULES.md) for detailed project rules and guidelines.

## Data Validation

The system includes comprehensive validation for:
- JSON schema compliance
- Data completeness
- Cross-references
- Orbital parameters
- Physical properties

## Contributing

1. Fork the repository
2. Create a feature branch
3. Install pre-commit hooks:
```bash
pip install pre-commit
pre-commit install
```
4. Make your changes
5. Run validation:
```bash
docker-compose run sannetic-explorer python scripts/validate_data.py
```
6. Ensure all pre-commit hooks pass:
```bash
pre-commit run --all-files
```
7. Submit a pull request

## License

[Your License Here]

## Contact

[Your Contact Information]

## 🚀 Release Process

This project uses semantic versioning and automated releases. To create a new release:

1. **Follow Conventional Commits**: All commits should follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:
   - `feat:` for new features
   - `fix:` for bug fixes
   - `docs:` for documentation changes
   - `style:` for formatting changes
   - `refactor:` for code refactoring
   - `perf:` for performance improvements
   - `test:` for adding tests
   - `build:` for build system changes
   - `ci:` for CI/CD changes
   - `chore:` for maintenance tasks

2. **Create a Release Tag**: When ready to release, create a semantic version tag:
   ```bash
   git tag v1.2.3
   git push origin v1.2.3
   ```

3. **Automated Release Process**: The release workflow will automatically:
   - Generate a changelog from conventional commits
   - Create a GitHub release
   - Build and push Docker images to GitHub Container Registry
   - Send Slack notifications (if configured)

### Docker Images

Each release creates three Docker images:
- `ghcr.io/<owner>/<repo>-backend:v1.2.3`
- `ghcr.io/<owner>/<repo>-frontend:v1.2.3`
- `ghcr.io/<owner>/<repo>-worker:v1.2.3`

### Required Secrets

For the release workflow to function properly, ensure these secrets are configured in your GitHub repository:

- `SLACK_WEBHOOK_URL` (optional): Slack webhook URL for release notifications 