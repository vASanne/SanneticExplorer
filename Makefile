# Sannetic Explorer Makefile

# Variables
DOCKER_COMPOSE = docker compose
BACKEND_SERVICE = backend
WORKER_SERVICE = worker

# Check if Docker is available
.PHONY: check-docker
check-docker:
	@command -v docker >/dev/null 2>&1 || { echo "❌ Docker is not installed or not in PATH"; exit 1; }
	@docker info >/dev/null 2>&1 || { echo "❌ Docker is not running. Please start Docker Desktop"; exit 1; }
	@echo "✅ Docker is available and running"

# Default target
.PHONY: help
help:
	@echo "Sannetic Explorer - Available commands:"
	@echo ""
	@echo "🚀 Core Commands:"
	@echo "  make check-docker   - Check if Docker is available and running"
	@echo "  make build          - Build all Docker containers"
	@echo "  make rebuild        - Rebuild all containers without cache and restart"
	@echo "  make up             - Start all services"
	@echo "  make down           - Stop all services"
	@echo "  make restart        - Restart all services"
	@echo "  make ps             - Show service status"
	@echo "  make logs           - View logs from all services"
	@echo ""
	@echo "🛠️ Development Commands:"
	@echo "  make sh-backend     - Connect to the backend container shell"
	@echo "  make sh-worker      - Connect to the worker container shell"
	@echo "  make test-backend   - Run backend tests with coverage"
	@echo "  make test-frontend  - Run frontend tests with coverage"
	@echo "  make test-all       - Run all tests"
	@echo ""
	@echo "🗄️ Database Commands:"
	@echo "  make db-migrate     - Import planet data to database"
	@echo "  make db-shell       - Connect to PostgreSQL shell"
	@echo ""
	@echo "🧹 Maintenance Commands:"
	@echo "  make clean          - Remove containers and volumes"
	@echo "  make prune          - Remove unused Docker resources"

# Docker management
.PHONY: build
build: check-docker
	@echo "Building all Docker containers..."
	@$(DOCKER_COMPOSE) build
	@echo "Build complete!"

.PHONY: build-with-time
build-with-time: check-docker
	@echo "Building all Docker containers and writing build time..."
	@$(DOCKER_COMPOSE) build
	@$(DOCKER_COMPOSE) up -d
	@echo "Waiting for database to be ready..."
	@sleep 10
	@echo "Writing build time to database..."
	@$(DOCKER_COMPOSE) exec $(BACKEND_SERVICE) python scripts/write_build_time.py frontend || echo "Failed to write build time"
	@echo "Build with time logging complete!"

.PHONY: rebuild
rebuild: check-docker
	@echo "Rebuilding all containers without cache and restarting..."
	@$(DOCKER_COMPOSE) down
	@$(DOCKER_COMPOSE) build --no-cache
	@$(DOCKER_COMPOSE) up -d
	@echo "Waiting for database to be ready..."
	@sleep 10
	@echo "Writing build time to database..."
	@$(DOCKER_COMPOSE) exec $(BACKEND_SERVICE) python scripts/write_build_time.py frontend || echo "Failed to write build time"
	@echo "Rebuild complete! Services are running."

.PHONY: up
up: check-docker
	@echo "Starting all services..."
	@$(DOCKER_COMPOSE) up -d
	@echo "Services started! Frontend: http://localhost:3000, Backend: http://localhost:8000"

.PHONY: down
down: check-docker
	@echo "Stopping all services..."
	@$(DOCKER_COMPOSE) down
	@echo "Services stopped!"

.PHONY: restart
restart: check-docker
	@echo "Restarting all services..."
	@$(DOCKER_COMPOSE) restart
	@echo "Services restarted!"

.PHONY: ps
ps: check-docker
	@echo "Service status:"
	@$(DOCKER_COMPOSE) ps

.PHONY: logs
logs: check-docker
	@echo "Showing logs from all services..."
	@$(DOCKER_COMPOSE) logs -f

# Connect to container shells
.PHONY: sh-backend
sh-backend: check-docker
	@echo "Connecting to backend container..."
	@$(DOCKER_COMPOSE) exec $(BACKEND_SERVICE) bash

.PHONY: sh-worker
sh-worker: check-docker
	@echo "Connecting to worker container..."
	@$(DOCKER_COMPOSE) exec $(WORKER_SERVICE) bash

# Database Commands
.PHONY: db-migrate
db-migrate: check-docker
	@echo "Importing planet data to database..."
	@$(DOCKER_COMPOSE) exec $(BACKEND_SERVICE) python import_planets_simple.py
	@echo "Planet data import complete!"

.PHONY: db-shell
db-shell: check-docker
	@echo "Connecting to PostgreSQL shell..."
	@$(DOCKER_COMPOSE) exec postgres psql -U postgres sannetic_explorer

# Testing
.PHONY: test-backend
test-backend: check-docker
	@echo "Running backend tests with coverage..."
	@$(DOCKER_COMPOSE) exec $(BACKEND_SERVICE) python -m pytest tests/ --cov=. --cov-report=term-missing

.PHONY: test-frontend
test-frontend:
	@echo "Running frontend tests with coverage..."
	@cd frontend && npm run test:coverage

.PHONY: test-all
test-all: test-backend test-frontend
	@echo "All tests completed!"

# Clean up container and volumes
.PHONY: clean
clean: check-docker
	@echo "Cleaning up containers and volumes..."
	@$(DOCKER_COMPOSE) down -v
	@echo "Cleanup complete!"

.PHONY: prune
prune: check-docker
	@echo "Removing unused Docker resources..."
	@docker system prune -f
	@echo "Docker cleanup complete!"