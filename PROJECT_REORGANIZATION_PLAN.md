# Sannetic Explorer - Projekt Reorganisation

## 🚨 Aktuelle Probleme

Das Root-Verzeichnis ist überladen mit:
- 50+ Dateien im Root
- Vermischte Backend/Frontend/Infrastructure Dateien
- Verstreute Dokumentation
- Doppelte Konfigurationsdateien
- Legacy-Dateien

## 🎯 Zielstruktur

```
SanneticExplorer/
├── README.md                    # Hauptdokumentation
├── .env.example                 # Umgebungsvariablen Template
├── .gitignore                   # Git Ignore
├── .pre-commit-config.yaml      # Pre-commit Konfiguration
├── pyproject.toml               # Python Projekt-Konfiguration
├── setup.py                     # Python Setup
├── .versionrc                   # Versionierung
├── docker-compose.yml           # Haupt Docker Compose
├── docker-compose.test.yml      # Test Docker Compose
├── Makefile                     # Haupt Makefile
├── main.py                      # Backend Entry Point
├── requirements.txt             # Python Dependencies
├── pytest.ini                  # Pytest Konfiguration
├──
├── backend/                     # Backend Code
│   ├── sannetic_explorer/       # Python Package
│   ├── migrations/              # Database Migrations
│   ├── scripts/                 # Backend Scripts
│   ├── tests/                   # Backend Tests
│   ├── Dockerfile.backend       # Backend Docker
│   ├── Dockerfile.worker        # Worker Docker
│   ├── requirements.txt         # Backend Dependencies
│   └── README.md               # Backend Dokumentation
├──
├── frontend/                    # Frontend Code
│   ├── src/                     # SvelteKit Source
│   ├── static/                  # Static Assets
│   ├── tests/                   # Frontend Tests
│   ├── Dockerfile              # Frontend Docker
│   ├── package.json            # Node Dependencies
│   └── README.md               # Frontend Dokumentation
├──
├── infrastructure/              # Infrastructure & DevOps
│   ├── docker/                  # Docker Files
│   │   ├── Dockerfile.backend
│   │   ├── Dockerfile.worker
│   │   └── Dockerfile.frontend
│   ├── scripts/                 # Infrastructure Scripts
│   ├── configs/                 # Konfigurationsdateien
│   └── README.md               # Infrastructure Docs
├──
├── docs/                        # Dokumentation
│   ├── guides/                  # Anleitungen
│   ├── api/                     # API Dokumentation
│   ├── deployment/              # Deployment Guides
│   └── README.md               # Docs Index
├──
├── data/                        # Daten
│   ├── celestial_bodies/        # Himmelskörper Daten
│   ├── migrations/              # Data Migrations
│   └── cache/                   # Cache Daten
├──
├── e2e/                         # End-to-End Tests
├──
├── .github/                     # GitHub Actions
└──
└── logs/                        # Log Dateien
```

## 📋 Reorganisations-Schritte

### Phase 1: Backend Reorganisation
```bash
# Backend-Dateien verschieben
mkdir -p backend/migrations
mkdir -p backend/scripts
mkdir -p backend/tests

# Verschieben
mv sannetic_explorer/ backend/
mv models.py backend/
mv database.py backend/
mv data_migration.py backend/scripts/
mv migration_*.sql backend/migrations/
mv init-db.sql backend/migrations/
mv Dockerfile.backend backend/
mv Dockerfile.worker backend/
mv requirements_backend.txt backend/requirements.txt
mv README_BACKEND.md backend/README.md
mv app.py backend/  # Falls noch benötigt
```

### Phase 2: Infrastructure Reorganisation
```bash
# Infrastructure-Dateien verschieben
mkdir -p infrastructure/docker
mkdir -p infrastructure/scripts
mkdir -p infrastructure/configs

# Verschieben
mv Dockerfile infrastructure/docker/
mv startup.sh infrastructure/scripts/
mv crontab* infrastructure/configs/
mv docker-compose.*.yml infrastructure/
mv web_dashboard.py infrastructure/scripts/
mv Makefile.backend infrastructure/
```

### Phase 3: Dokumentation Reorganisation
```bash
# Dokumentation verschieben
mkdir -p docs/guides
mkdir -p docs/api
mkdir -p docs/deployment

# Verschieben
mv *_GUIDE.md docs/guides/
mv *_IMPLEMENTATION.md docs/guides/
mv *_PLAN.md docs/guides/
mv AI_*.md docs/guides/
mv CONFIGURATION_GUIDE.md docs/guides/
mv LOGGING_GUIDE.md docs/guides/
mv API_OPTIMIZATION_GUIDE.md docs/api/
mv WEB_DASHBOARD_GUIDE.md docs/guides/
mv INFRASTRUCTURE_TESTING_GUIDE.md docs/guides/
mv TESTING_GUIDE.md docs/guides/
mv concept.md docs/
mv RULES.md docs/
mv ruleset.md docs/
```

### Phase 4: Daten Reorganisation
```bash
# Daten verschieben
mkdir -p data/celestial_bodies
mkdir -p data/migrations
mkdir -p data/cache

# Verschieben
mv Data/* data/celestial_bodies/
mv cache/* data/cache/
mv templates/ data/
```

### Phase 5: Cleanup
```bash
# Unnötige Dateien entfernen
rm -f .DS_Store
rm -f test_pre_commit.py  # Falls nicht mehr benötigt
rm -f venv/  # Falls vorhanden
```

## 🔧 Konfigurations-Updates

### Docker Compose Updates
```yaml
# docker-compose.yml anpassen
services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile.backend
    volumes:
      - ./data:/app/data:ro
      - ./logs:/app/logs

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
```

### Python Path Updates
```python
# main.py anpassen
import sys
sys.path.append('./backend')
from sannetic_explorer.api import app
```

### Makefile Updates
```makefile
# Makefile anpassen
backend-test:
	cd backend && pytest

frontend-test:
	cd frontend && npm test

docker-build:
	docker-compose -f infrastructure/docker-compose.yml build
```

## 📁 Neue Verzeichnisstruktur

### Backend (`/backend`)
```
backend/
├── sannetic_explorer/          # Python Package
│   ├── api/
│   ├── models/
│   ├── services/
│   └── tests/
├── migrations/                 # Database Migrations
├── scripts/                    # Backend Scripts
├── tests/                      # Backend Tests
├── Dockerfile.backend          # Backend Container
├── Dockerfile.worker           # Worker Container
├── requirements.txt            # Dependencies
└── README.md                   # Backend Docs
```

### Frontend (`/frontend`)
```
frontend/
├── src/                        # SvelteKit Source
├── static/                     # Static Assets
├── tests/                      # Frontend Tests
├── Dockerfile                  # Frontend Container
├── package.json                # Dependencies
└── README.md                   # Frontend Docs
```

### Infrastructure (`/infrastructure`)
```
infrastructure/
├── docker/                     # Docker Files
├── scripts/                    # Infrastructure Scripts
├── configs/                    # Konfigurationen
├── docker-compose.yml          # Main Compose
├── docker-compose.test.yml     # Test Compose
└── README.md                   # Infrastructure Docs
```

### Documentation (`/docs`)
```
docs/
├── guides/                     # Anleitungen
├── api/                        # API Docs
├── deployment/                 # Deployment
├── README.md                   # Docs Index
└── concept.md                  # Projekt-Konzept
```

### Data (`/data`)
```
data/
├── celestial_bodies/           # Himmelskörper
├── migrations/                 # Data Migrations
├── cache/                      # Cache
└── templates/                  # Templates
```

## 🚀 Vorteile der Reorganisation

### ✅ Übersichtlichkeit
- Klare Trennung von Backend/Frontend/Infrastructure
- Logische Gruppierung verwandter Dateien
- Reduzierte Komplexität im Root

### ✅ Wartbarkeit
- Einfachere Navigation
- Bessere Code-Organisation
- Klare Verantwortlichkeiten

### ✅ Skalierbarkeit
- Einfache Erweiterung einzelner Bereiche
- Modulare Struktur
- Wiederverwendbare Komponenten

### ✅ Teamarbeit
- Klare Arbeitsbereiche
- Reduzierte Merge-Konflikte
- Bessere Code-Reviews

## 📝 Migration Checklist

- [ ] Backup des aktuellen Zustands
- [ ] Phase 1: Backend Reorganisation
- [ ] Phase 2: Infrastructure Reorganisation
- [ ] Phase 3: Dokumentation Reorganisation
- [ ] Phase 4: Daten Reorganisation
- [ ] Phase 5: Cleanup
- [ ] Konfigurationsdateien anpassen
- [ ] Tests ausführen
- [ ] Dokumentation aktualisieren
- [ ] Team informieren

## ⚠️ Wichtige Hinweise

1. **Backup erstellen** vor der Reorganisation
2. **Schrittweise vorgehen** und nach jedem Schritt testen
3. **Konfigurationsdateien anpassen** (Docker, Python Paths, etc.)
4. **Tests ausführen** nach jeder Phase
5. **Dokumentation aktualisieren** mit neuen Pfaden

Diese Reorganisation wird das Projekt deutlich übersichtlicher und wartbarer machen! 🎯 