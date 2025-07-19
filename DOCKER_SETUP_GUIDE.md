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

# Services starten
make up

# Status prüfen
make ps
```

### Schritt 3: Logs überprüfen

```bash
# Alle Service-Logs anzeigen
make logs-all

# Spezifische Service-Logs
docker compose logs backend
docker compose logs frontend
docker compose logs db
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

**Lösung:**
```bash
# Verwendete Ports prüfen
lsof -i :8000  # Backend
lsof -i :3000  # Frontend
lsof -i :5432  # PostgreSQL

# Prozess beenden (PID aus lsof verwenden)
kill -9 <PID>
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

- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs
- **PostgreSQL:** localhost:5432
- **Redis:** localhost:6379

## 📝 Nützliche Docker Befehle

```bash
# Service-spezifische Logs
docker compose logs -f backend
docker compose logs -f frontend

# Container Status
docker compose ps

# In laufenden Container einsteigen
docker compose exec backend bash
docker compose exec db psql -U postgres -d sannetic_explorer

# Container neu starten
docker compose restart backend

# Einzelnen Service neu bauen
docker compose build backend

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