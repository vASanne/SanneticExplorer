# Docker Setup Guide für Sannetic Explorer

## 🐳 Docker Installation auf macOS

### Option 1: Docker Desktop (Empfohlen)

1. **Download Docker Desktop:**
   - Gehe zu [docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop)
   - Lade Docker Desktop für Mac herunter

2. **Installation:**
   ```bash
   # Nach dem Download die .dmg Datei öffnen und Docker.app nach /Applications ziehen
   open /Applications/Docker.app
   ```

3. **Docker Desktop starten:**
   - Docker Desktop aus dem Applications Ordner starten
   - Warten bis Docker vollständig gestartet ist (Wal-Symbol in der Menüleiste)

### Option 2: Homebrew Installation

```bash
# Docker Desktop via Homebrew installieren
brew install --cask docker

# Docker Desktop starten
open /Applications/Docker.app
```

### Option 3: Colima (Leichtgewichtige Alternative)

```bash
# Colima installieren (Docker-kompatible Container Runtime)
brew install colima docker docker-compose

# Colima starten
colima start

# Docker testen
docker --version
```

## 🔧 Docker Konfiguration

### Docker Desktop Einstellungen

1. **Ressourcen anpassen:**
   - Docker Desktop öffnen → Settings → Resources
   - Empfohlene Einstellungen:
     - CPUs: 4+
     - Memory: 8GB+
     - Swap: 2GB
     - Disk image size: 64GB+

2. **File Sharing aktivieren:**
   - Settings → Resources → File Sharing
   - Sicherstellen, dass `/Users` aktiviert ist

## ✅ Docker Installation testen

```bash
# Docker Version prüfen
docker --version
docker compose version

# Docker funktionalität testen
docker run hello-world

# Sannetic Explorer Docker Check
make check-docker
```

## 🚀 Sannetic Explorer mit Docker starten

Der Stack nutzt das Compose-Projekt **sannetic-explorer**. Container, Netzwerke und Volumes heißen dadurch `sannetic-explorer_*` und kollidieren nicht mit anderen Projekten auf derselben Maschine.

Veröffentlichte Host-Ports (Container-Ports bleiben 3000 / 8000 / 5432 / 6379):

| Dienst | Host | Container |
| --- | --- | --- |
| Frontend | 13300 | 3000 |
| Backend / API | 13800 | 8000 |
| PostgreSQL | 15432 | 5432 |
| Redis | 16379 | 6379 |

Dienste im Compose-Netz sprechen sich mit den Service-Namen und den Container-Ports an (`db:5432`, `redis:6379`, `backend:8000`). Nur der Browser nutzt die Host-Ports. `PUBLIC_API_URL` ist deshalb `http://localhost:13800`. SvelteKit-Loads im Frontend-Container nutzen `INTERNAL_API_URL=http://backend:8000` (Test-Stack: `http://test-backend:8000`). Der Backend-Start importiert Sonne und acht Planeten.

Überschreiben in `.env` (Vorlage: `env.example`), zum Beispiel `HOST_FRONTEND_PORT=13310`. Wenn du `HOST_BACKEND_PORT` änderst, setze `PUBLIC_API_URL=http://localhost:<port>` auf denselben Wert und baue das Frontend neu (`make build`). `COMPOSE_PROJECT_NAME` in der `.env` überschreibt den Projektnamen **aller** Compose-Dateien in diesem Ordner; für einen einzelnen Aufruf `docker compose -p <name>` verwenden.

### Schritt 1: Umgebungsvariablen einrichten

```bash
# .env Datei erstellen
make config-setup

# .env Datei bearbeiten und API Keys hinzufügen
nano .env
```

### Schritt 2: Services starten

```bash
# Alle Container bauen
make build

# Services starten (Projektname sannetic-explorer, Host-Ports 13300/13800/15432/16379)
make up

# Gleichwertig ohne Make:
docker compose -p sannetic-explorer up -d

# Status prüfen
make ps
```

### Schritt 3: Logs überprüfen

```bash
# Alle Service-Logs anzeigen
make logs-all

# Spezifische Service-Logs
docker compose -p sannetic-explorer logs backend
docker compose -p sannetic-explorer logs frontend
docker compose -p sannetic-explorer logs db
```

## 🛠️ Häufige Probleme und Lösungen

### Problem: "Docker is not running"

**Lösung:**
```bash
# Docker Desktop starten
open /Applications/Docker.app

# Warten bis Docker gestartet ist, dann testen
make check-docker
```

### Problem: "Permission denied" Fehler

**Lösung:**
```bash
# Docker Gruppe hinzufügen (falls nötig)
sudo dscl . append /Groups/staff GroupMembership $(whoami)

# Terminal neu starten
```

### Problem: Container starten nicht

**Lösung:**
```bash
# Logs überprüfen
make logs-all

# Container neu bauen
make clean
make build
make up
```

### Problem: Port bereits belegt

Die Standardports 3000, 8000, 5432 und 6379 werden nicht mehr gebunden. Falls ein reservierter Host-Port schon belegt ist:

```bash
# Reservierte Ports prüfen
lsof -i :13800  # Backend
lsof -i :13300  # Frontend
lsof -i :15432  # PostgreSQL
lsof -i :16379  # Redis

# In .env auf freie Ports legen (PUBLIC_API_URL an HOST_BACKEND_PORT anpassen)
# HOST_BACKEND_PORT=13810
# PUBLIC_API_URL=http://localhost:13810
```

## 📊 Verfügbare Make-Befehle

### Docker Management
- `make check-docker` - Docker verfügbarkeit prüfen
- `make build` - Alle Container bauen
- `make up` - Services starten
- `make down` - Services stoppen
- `make ps` - Service Status
- `make logs-all` - Alle Logs anzeigen
- `make clean` - Container und Volumes löschen

### Container Shell-Zugriff
- `make sh-backend` - Backend Container Shell
- `make sh-worker` - Worker Container Shell

### Daten-Updates
- `make update-data` - Alle Update-Skripte ausführen
- `make update-optimized` - API-optimiertes Update
- `make update-critical` - Kritische Satelliten updaten

### Tests
- `make docker-test` - Infrastructure Tests
- `make test-backend` - Backend Tests
- `make test-frontend` - Frontend Tests

## 🔍 Service URLs

Nach dem Start sind folgende Services verfügbar:

- **Frontend:** http://localhost:13300
- **Backend API:** http://localhost:13800
- **API Docs:** http://localhost:13800/docs
- **Planeten:** http://localhost:13800/planets
- **PostgreSQL:** localhost:15432
- **Redis:** localhost:16379

Beim Start lädt das Backend Sonne und Planeten aus `Data/Stars/sun.json` und `Data/Planets/*.json`, falls diese Namen noch nicht in Postgres stehen. Derselbe Import erneut:

```bash
make db-seed
```

Der Browser spricht die API über `PUBLIC_API_URL` (http://localhost:13800) an. SvelteKit-Load-Funktionen im Frontend-Container nutzen `INTERNAL_API_URL` (http://backend:8000).

## 📝 Nützliche Docker Befehle

```bash
# Service-spezifische Logs
docker compose -p sannetic-explorer logs -f backend
docker compose -p sannetic-explorer logs -f frontend

# Container Status
docker compose -p sannetic-explorer ps

# In laufenden Container einsteigen
docker compose -p sannetic-explorer exec backend bash
docker compose -p sannetic-explorer exec db psql -U postgres -d sannetic_explorer

# Container neu starten
docker compose -p sannetic-explorer restart backend

# Einzelnen Service neu bauen
docker compose -p sannetic-explorer build backend

# Volumes auflisten
docker volume ls

# Container-Ressourcen überwachen
docker stats
```

## 🆘 Support

Falls Probleme auftreten:

1. **Logs überprüfen:** `make logs-all`
2. **Docker Status:** `make check-docker`
3. **Services neu starten:** `make down && make up`
4. **Clean Build:** `make clean && make build && make up`

Bei persistenten Problemen, erstelle ein Issue mit:
- Docker Version (`docker --version`)
- macOS Version (`sw_vers`)
- Fehlermeldungen aus den Logs 