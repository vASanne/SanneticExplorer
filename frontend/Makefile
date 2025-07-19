.PHONY: install dev build preview check lint format clean help

# Default target
help:
	@echo "Sannetic Explorer Frontend - Available commands:"
	@echo "  install  - Install dependencies"
	@echo "  dev      - Start development server on port 3000"
	@echo "  build    - Build for production"
	@echo "  preview  - Preview production build"
	@echo "  check    - Type-check the project"
	@echo "  lint     - Lint the code"
	@echo "  format   - Format the code"
	@echo "  clean    - Clean build artifacts"

# Install dependencies
install:
	npm install

# Start development server
dev:
	npm run dev:front

# Build for production
build:
	npm run build

# Preview production build
preview:
	npm run preview

# Type-check the project
check:
	npm run check

# Lint the code
lint:
	npm run lint

# Format the code
format:
	npm run format

# Clean build artifacts
clean:
	rm -rf dist .svelte-kit node_modules 