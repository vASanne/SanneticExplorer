# Sannetic Explorer E2E Tests

This directory contains end-to-end tests for the Sannetic Explorer application using Playwright.

## Overview

The e2e tests provide comprehensive coverage of the application's user interface and functionality, including:

- **Dashboard functionality** - Status cards, script execution, update logs
- **3D Scene interactions** - Canvas rendering, camera controls, performance monitoring
- **Visual regression testing** - Screenshot comparisons for UI consistency
- **Cross-browser testing** - Chrome, Firefox, Safari, and mobile browsers

## Prerequisites

- Node.js 18+ 
- Docker and Docker Compose
- The Sannetic Explorer application running via `docker compose -p sannetic-explorer up -d`

## Installation

```bash
# Install dependencies
npm install

# Install Playwright browsers
npm run test:install
```

## Test Structure

```
e2e/
├── playwright.config.ts      # Playwright configuration
├── global-setup.ts          # Global setup (starts Docker services)
├── global-teardown.ts       # Global teardown (stops Docker services)
├── tests/
│   ├── dashboard.spec.ts    # Dashboard functionality tests
│   └── 3d-scene.spec.ts     # 3D scene functionality tests
└── package.json
```

## Running Tests

### All Tests
```bash
npm test
```

### Specific Test Categories
```bash
# Functional tests only
npm run test:functional

# Visual regression tests only
npm run test:visual

# Dashboard tests only
npm test -- --grep "Dashboard"
```

### Test Modes
```bash
# Run with browser UI visible
npm run test:headed

# Run with Playwright UI
npm run test:ui

# Debug mode (step through tests)
npm run test:debug

# Update screenshot baselines
npm run test:update-screenshots
```

### View Test Reports
```bash
npm run test:report
```

## Test Features

### Docker Integration
- Automatically starts `docker compose -p sannetic-explorer up -d` before tests
- Waits for services to be ready (frontend:13300, backend:13800)
- Cleans up Docker services after tests complete

### Visual Regression Testing
- Screenshots are captured for key UI states
- Baseline images are stored for comparison
- Configurable threshold for pixel differences
- Supports full-page and component-level screenshots

### Cross-Browser Testing
- Chrome, Firefox, Safari (desktop)
- Mobile Chrome, Mobile Safari
- Parallel execution across browsers

### Performance Monitoring
- FPS monitoring for 3D scenes
- Load time measurements
- Memory usage tracking

## Test Scenarios

### Dashboard Tests
- ✅ Display status cards with script information
- ✅ Show update logs table with data
- ✅ Trigger script execution ("Run Now" button)
- ✅ Monitor status changes (running → success)
- ✅ Auto-refresh functionality
- ✅ Error state handling
- ✅ Empty data state handling
- ✅ Performance metrics display

### 3D Scene Tests
- ✅ Canvas rendering and WebGL support
- ✅ Orbit side panel functionality
- ✅ Celestial body selection and information display
- ✅ Camera controls (rotation, zoom)
- ✅ Performance monitoring (FPS, draw calls)
- ✅ Loading states and error handling
- ✅ Window resize handling
- ✅ Orbital path visualization

### Visual Regression Tests
- ✅ Dashboard baseline screenshots
- ✅ Status cards and table components
- ✅ Running state and error state screenshots
- ✅ 3D scene baseline and component screenshots
- ✅ Loading and error state screenshots

## Configuration

### Playwright Config (`playwright.config.ts`)
- **Base URL**: `http://localhost:13300`
- **Timeout**: 5 seconds for actions, 2 minutes for web server
- **Screenshot threshold**: 0.2 (20% pixel difference allowed)
- **Max diff pixels**: 100 pixels
- **Retries**: 2 on CI, 0 locally
- **Parallel execution**: Enabled

### Global Setup (`global-setup.ts`)
- Starts Docker Compose services
- Waits for frontend and backend to be ready
- Verifies application accessibility
- Health checks for both services

### Global Teardown (`global-teardown.ts`)
- Stops Docker Compose services
- Cleans up test artifacts
- Ensures clean environment for next run

## CI/CD Integration

The e2e tests are integrated into the GitHub Actions workflow:

```yaml
- name: Run E2E Tests
  run: |
    cd e2e
    npm install
    npm run test:install
    npm test
```

## Debugging

### View Test Traces
```bash
# Open trace viewer
npx playwright show-trace test-results/trace.zip
```

### Generate Test Code
```bash
# Record new test
npm run test:codegen
```

### Debug Specific Test
```bash
# Debug a specific test
npm run test:debug -- --grep "should trigger script execution"
```

## Best Practices

1. **Use data-testid attributes** for reliable element selection
2. **Wait for network idle** before making assertions
3. **Use proper timeouts** for async operations
4. **Mock external dependencies** when testing error states
5. **Take screenshots** for visual regression testing
6. **Test across multiple browsers** for compatibility
7. **Use descriptive test names** that explain the scenario
8. **Group related tests** using `test.describe()`

## Troubleshooting

### Common Issues

**Docker services not starting**
```bash
# Check Docker status
docker compose -p sannetic-explorer ps

# Restart services
docker compose -p sannetic-explorer down && docker compose -p sannetic-explorer up -d
```

**Tests timing out**
- Increase timeout in `playwright.config.ts`
- Check if services are responding on correct ports
- Verify Docker containers are healthy

**Screenshot failures**
- Update baselines: `npm run test:update-screenshots`
- Check for UI changes that affect layout
- Verify consistent test environment

**Browser installation issues**
```bash
# Reinstall browsers
npx playwright install
```

## Contributing

When adding new tests:

1. Follow the existing test structure and naming conventions
2. Add appropriate `data-testid` attributes to components
3. Include both functional and visual regression tests
4. Test error states and edge cases
5. Update this README with new test scenarios
6. Ensure tests pass across all browsers

## Performance Considerations

- Tests run in parallel by default
- Screenshots are disabled for animations to ensure consistency
- Docker services are reused between test runs when possible
- Browser instances are shared across tests in the same project 