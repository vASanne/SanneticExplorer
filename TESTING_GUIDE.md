# Testing Guide for Sannetic Explorer

This document provides comprehensive information about the testing setup for both backend and frontend components of the Sannetic Explorer project.

## Overview

The project uses a comprehensive testing strategy with:
- **Backend**: pytest with 90% coverage threshold
- **Frontend**: Vitest with 80% coverage threshold
- **Integration**: End-to-end testing with Docker containers
- **Quality**: Pre-commit hooks for code quality

## Backend Testing

### Test Structure

```
sannetic_explorer/tests/
├── conftest.py              # Pytest configuration and fixtures
├── test_update_logs.py      # UpdateLog model and API tests
└── test_bodies.py           # CelestialBody CRUD tests
```

### Key Test Areas

#### 1. UpdateLog Insertion Logic
- Tests for creating UpdateLog instances
- Validation of constraints (status, duration)
- String representation testing
- Database insertion and retrieval

#### 2. /updates/status Endpoint
- Returns correct latest states for each script
- Status mapping (success → OK, error → FAIL, warning → UNKNOWN)
- Handles empty data gracefully
- Rate limiting functionality

#### 3. /bodies CRUD Operations
- GET /celestial-bodies with filtering
- PUT /bodies/{id} for updates
- Error handling for non-existent bodies
- Data validation and constraints

### Running Backend Tests

```bash
# Run all tests with coverage
make test-backend

# Run tests in watch mode
make test-backend-watch

# Run specific test file
cd sannetic_explorer && python -m pytest tests/test_update_logs.py -v

# Run with specific markers
python -m pytest tests/ -m "unit" -v
python -m pytest tests/ -m "integration" -v
```

### Coverage Requirements

- **Minimum Coverage**: 90%
- **Coverage Reports**: HTML, XML, and terminal output
- **Branch Coverage**: Enabled
- **Coverage Tools**: pytest-cov

## Frontend Testing

### Test Structure

```
frontend/src/
├── routes/
│   ├── dashboard/
│   │   └── +page.test.ts    # Dashboard component tests
│   └── 3d/
│       └── +page.test.ts    # 3D scene component tests
└── test/
    └── setup.ts             # Test setup and mocks
```

### Key Test Areas

#### 1. Dashboard Component
- Renders with loading state initially
- Displays script status cards with correct data
- Shows update logs table with proper formatting
- Manual trigger button functionality
- Auto-refresh every 5 seconds
- Error handling and empty states

#### 2. 3D Scene Component
- Renders celestial bodies after data loads
- Performance monitor display
- Orbit side panel functionality
- Speed control and camera controls
- API error handling

### Running Frontend Tests

```bash
# Run all tests with coverage
make test-frontend

# Run tests in watch mode
make test-frontend-watch

# Run specific test file
cd frontend && npm run test src/routes/dashboard/+page.test.ts

# Run with UI
npm run test:ui
```

### Coverage Requirements

- **Minimum Coverage**: 80%
- **Coverage Reports**: HTML and terminal output
- **Coverage Tools**: @vitest/coverage-v8

## Test Configuration

### Backend (pytest.ini)

```ini
[tool:pytest]
testpaths = sannetic_explorer/tests tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    -v 
    --tb=short
    --strict-markers
    --disable-warnings
    --cov=sannetic_explorer
    --cov-report=term-missing
    --cov-report=html:htmlcov
    --cov-report=xml:coverage.xml
    --cov-fail-under=90
    --cov-branch
```

### Frontend (vitest.config.ts)

```typescript
export default defineConfig({
  plugins: [sveltekit()],
  test: {
    include: ['src/**/*.{test,spec}.{js,ts}'],
    environment: 'jsdom',
    setupFiles: ['src/test/setup.ts'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      thresholds: {
        global: {
          branches: 80,
          functions: 80,
          lines: 80,
          statements: 80
        }
      }
    }
  }
})
```

## CI/CD Integration

### GitHub Actions Workflow

The CI pipeline includes:

1. **Pre-commit Checks**: Code formatting, linting, type checking
2. **Backend Tests**: Unit and integration tests with coverage
3. **Frontend Tests**: Component tests with coverage
4. **Docker Builds**: Integration testing with containers
5. **Coverage Reporting**: Upload to Codecov

### Coverage Upload

```yaml
- name: Upload coverage to Codecov
  uses: codecov/codecov-action@v3
  with:
    file: ./sannetic_explorer/coverage.xml
    flags: backend
    name: backend-coverage
```

## Test Data and Fixtures

### Backend Fixtures

```python
@pytest.fixture
def sample_celestial_bodies():
    """Sample celestial bodies for testing"""
    return [
        {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "name": "Sun",
            "type": "star",
            # ... more fields
        }
    ]

@pytest.fixture
def sample_update_logs():
    """Sample update logs for testing"""
    return [
        {
            "id": "550e8400-e29b-41d4-a716-446655440002",
            "script_name": "update_critical.py",
            "status": "success",
            # ... more fields
        }
    ]
```

### Frontend Mock Data

```typescript
const mockScriptStatus = [
  {
    script_name: 'update_critical.py',
    last_run: '2024-01-15T10:30:00Z',
    status: 'OK',
    duration_sec: 45.2,
    message: 'Successfully updated 5 critical satellites'
  }
]
```

## Mocking Strategy

### Backend Mocking

- **Database**: SQLite test database with transaction rollback
- **Redis**: Mocked for rate limiting and job queue
- **External APIs**: Mocked responses for testing

### Frontend Mocking

- **API Calls**: Mocked fetch responses
- **Three.js**: Mocked for 3D scene testing
- **Browser APIs**: Mocked for testing environment

## Test Commands

### Makefile Targets

```bash
# Run all tests
make test-all

# Backend tests
make test-backend
make test-backend-watch

# Frontend tests
make test-frontend
make test-frontend-watch

# Code quality
make pre-commit
make format
make lint
make type-check
```

### Direct Commands

```bash
# Backend
cd sannetic_explorer && python -m pytest tests/ --cov=. --cov-fail-under=90

# Frontend
cd frontend && npm run test:coverage
```

## Best Practices

### Writing Tests

1. **Descriptive Names**: Use clear, descriptive test names
2. **Arrange-Act-Assert**: Structure tests with clear sections
3. **Isolation**: Each test should be independent
4. **Coverage**: Aim for high coverage but focus on critical paths
5. **Mocking**: Mock external dependencies appropriately

### Test Organization

1. **Unit Tests**: Test individual functions and components
2. **Integration Tests**: Test API endpoints and database operations
3. **End-to-End Tests**: Test complete user workflows
4. **Performance Tests**: Test critical performance requirements

### Debugging Tests

```bash
# Backend debugging
python -m pytest tests/ -v -s --pdb

# Frontend debugging
npm run test -- --reporter=verbose
```

## Coverage Reports

### Backend Coverage

- **Location**: `sannetic_explorer/htmlcov/index.html`
- **Threshold**: 90% minimum
- **Reports**: HTML, XML, terminal

### Frontend Coverage

- **Location**: `frontend/coverage/index.html`
- **Threshold**: 80% minimum
- **Reports**: HTML, terminal

## Continuous Monitoring

- **Pre-commit Hooks**: Automatic quality checks
- **CI Pipeline**: Automated testing on every commit
- **Coverage Tracking**: Historical coverage trends
- **Performance Monitoring**: Test execution time tracking

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all dependencies are installed
2. **Database Issues**: Check test database configuration
3. **Mock Failures**: Verify mock setup and expectations
4. **Coverage Issues**: Check coverage configuration and thresholds

### Debug Commands

```bash
# Check test environment
python -c "import pytest; print(pytest.__version__)"
npm list vitest

# Run tests with verbose output
python -m pytest tests/ -v -s
npm run test -- --reporter=verbose
```

This testing setup ensures high code quality, reliability, and maintainability for the Sannetic Explorer project. 