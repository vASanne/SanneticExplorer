# Sannetic Explorer Documentation

Sannetic Explorer is a solar system simulation platform with a FastAPI backend and a SvelteKit/Threlte frontend.

## Quick Start

```sh
docker compose -p sannetic-explorer up --build
```

The UI is at http://localhost:13300 and the API at http://localhost:13800. Host ports 3000, 8000, 5432, and 6379 are not published. See `DOCKER_SETUP_GUIDE.md`.

## Development Workflow

- **Backend (FastAPI):**
  ```sh
  # In project root
  make dev:back
  # or
  uvicorn app:app --reload
  ```
- **Frontend (SvelteKit):**
  ```sh
  cd frontend
  npm run dev:front
  ```
- **Data Sync/Update:**
  ```sh
  python backend/scripts/sync.py update
  ```

## Contribution Guidelines

- **Lint:**
  - Backend: `make lint` or `flake8 .`
  - Frontend: `npm run lint`
- **Tests:**
  - Backend: `pytest`
  - Frontend: `npx playwright test`
- Open a pull request for all changes. Ensure all tests and linters pass before requesting review.

---

> **Rule:** Keep `docs/README.md` up to date with any changes to project purpose, quick-start, dev workflow, or contribution process. 