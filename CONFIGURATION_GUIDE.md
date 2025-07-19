# 🔧 Sannetic Explorer - Konfigurationsanleitung

Willkommen zur Konfigurationsanleitung für Sannetic Explorer! Diese Anleitung hilft Ihnen dabei, alle API-Zugangsdaten und Systemeinstellungen über eine zentrale `.env`-Datei zu konfigurieren.

## 📋 Schnellstart

### 1. Konfigurationsdatei erstellen
```bash
# Erstelle .env aus Vorlage
make config-setup

# Oder manuell:
cp env.example .env
```

### 2. API-Schlüssel konfigurieren
Öffnen Sie die `.env`-Datei und tragen Sie Ihre API-Schlüssel ein:

```bash
# Bearbeiten Sie die .env-Datei
nano .env
# oder
code .env
```

### 3. Konfiguration prüfen
```bash
# Überprüfen Sie die Konfiguration
make config-check

# Validieren Sie alle Einstellungen
make config-validate
```

## 🔑 API-Schlüssel einrichten

### OpenAI API (für KI-Features)
1. Besuchen Sie: https://platform.openai.com/api-keys
2. Erstellen Sie einen neuen API-Schlüssel
3. Tragen Sie ihn in die `.env` ein:
```env
OPENAI_API_KEY=sk-proj-your_openai_api_key_here
```

**Empfohlene Einstellungen:**
```env
OPENAI_MODEL=gpt-4o-mini          # Kostengünstig und effizient
OPENAI_MAX_TOKENS=2000            # Ausreichend für technische Antworten
OPENAI_TEMPERATURE=0.3            # Präzise technische Antworten
AI_DAILY_COST_LIMIT=5.00          # Kostenkontrolle
AI_MONTHLY_COST_LIMIT=50.00       # Monatliche Begrenzung
```

### N2YO API (für Satellitentracking)
1. Registrieren Sie sich: https://www.n2yo.com/api/
2. Erhalten Sie Ihren kostenlosen API-Schlüssel
3. Konfigurieren Sie:
```env
N2YO_API_KEY=your_n2yo_api_key_here
```

### Space-Track.org (für TLE-Daten)
1. Registrieren Sie sich: https://www.space-track.org/auth/createAccount
2. Bestätigen Sie Ihre E-Mail-Adresse
3. Konfigurieren Sie:
```env
SPACE_TRACK_USERNAME=your_username
SPACE_TRACK_PASSWORD=your_password
```

## ⚙️ Systemkonfiguration

### Dashboard-Einstellungen
```env
DASHBOARD_PORT=8080               # Port für Web-Dashboard
DASHBOARD_HOST=0.0.0.0           # Host-Adresse
DASHBOARD_AUTO_REFRESH=30        # Auto-Refresh in Sekunden
```

### Logging-Konfiguration
```env
LOG_LEVEL=INFO                   # DEBUG, INFO, WARNING, ERROR
LOG_MAX_FILES=10                 # Anzahl der Log-Dateien
```

### Update-System
```env
UPDATE_BATCH_SIZE=5              # Objekte pro Batch
UPDATE_DELAY_SECONDS=2           # Verzögerung zwischen Updates
API_RATE_LIMIT_DELAY=1           # API-Rate-Limiting
```

### Datenqualität-Schwellenwerte
```env
DATA_QUALITY_EXCELLENT_THRESHOLD=100
DATA_QUALITY_GOOD_THRESHOLD=50
DATA_QUALITY_FAIR_THRESHOLD=10
```

## 🧠 KI-System konfigurieren

### KI-Features aktivieren/deaktivieren
```env
AI_ENABLE_ERROR_ANALYSIS=true        # Automatische Fehleranalyse
AI_ENABLE_ORBITAL_CALCULATIONS=true  # Erweiterte Orbitalberechnungen
AI_ENABLE_OPTIMIZATION=true          # Systemoptimierung
AI_CONFIDENCE_THRESHOLD=0.7          # Mindest-Vertrauenswert
AI_MAX_RETRIES=3                     # Wiederholungsversuche
```

### Kostenkontrolle
```env
AI_COST_TRACKING=true               # Kostenüberwachung aktivieren
AI_DAILY_COST_LIMIT=5.00           # Tägliches Limit in USD
AI_MONTHLY_COST_LIMIT=50.00        # Monatliches Limit in USD
```

## 🔒 Sicherheitseinstellungen

### API-Sicherheit
```env
API_TIMEOUT_SECONDS=30              # Request-Timeout
API_MAX_RETRIES=3                   # Wiederholungsversuche
API_VERIFY_SSL=true                 # SSL-Zertifikat prüfen
```

### Dashboard-Sicherheit
```env
DASHBOARD_SECRET_KEY=your_secret_key_here    # Für Sessions
DASHBOARD_SESSION_TIMEOUT=3600               # Session-Timeout
```

## 🛠️ Entwicklungseinstellungen

### Debug-Modus
```env
DEBUG_MODE=false                    # Debug-Ausgaben
VERBOSE_LOGGING=false               # Ausführliche Logs
DEVELOPMENT_MODE=false              # Entwicklungsmodus
```

### Testing
```env
TEST_MODE=false                     # Test-Modus
MOCK_API_RESPONSES=false            # Mock-APIs für Tests
```

### Cache-Konfiguration
```env
CACHE_ENABLED=true                  # Cache aktivieren
CACHE_TTL_SECONDS=1800             # Cache-Lebensdauer (30 Min)
CACHE_MAX_SIZE=100                 # Maximale Cache-Größe
```

## 📊 Konfiguration validieren

### Alle Befehle im Überblick
```bash
# Konfiguration einrichten
make config-setup

# Status anzeigen
make config-check

# Validierung durchführen
make config-validate

# Dashboard starten
make dashboard

# KI-System testen
make test-ai

# KI-Demo ausführen
make ai-demo
```

### Konfigurationsstatus verstehen

**✅ Grüne Symbole:** API konfiguriert und einsatzbereit  
**❌ Rote Symbole:** API nicht konfiguriert  
**⚠️ Gelbe Symbole:** Warnung oder suboptimale Konfiguration

### Typische Warnungen
- **"OpenAI API key not configured"** → Tragen Sie Ihren OpenAI-Schlüssel ein
- **"N2YO API key not configured"** → Registrieren Sie sich bei N2YO
- **"Space-Track credentials not configured"** → Erstellen Sie ein Space-Track-Konto

## 🚀 Nach der Konfiguration

### 1. System testen
```bash
# Grundfunktionen testen
make config-validate

# KI-System testen
make test-ai

# Dashboard starten
make dashboard
```

### 2. Dashboard öffnen
```bash
# Dashboard im Browser öffnen
make open-dashboard
```

### 3. KI-Features nutzen
```bash
# KI-Demo ausführen
make ai-demo

# Intelligente Updates
make update-delta-smart-ai

# KI-Gesundheitscheck
make ai-health-check
```

## ❓ Häufige Probleme

### "Configuration manager not available"
- Installieren Sie: `pip install python-dotenv`
- Prüfen Sie: `python -c "import dotenv; print('OK')"`

### "OpenAI API key not found"
- Prüfen Sie die `.env`-Datei: `cat .env | grep OPENAI`
- Stellen Sie sicher, dass keine Leerzeichen um das `=` stehen

### "Invalid API key"
- Überprüfen Sie den API-Schlüssel auf der jeweiligen Plattform
- Stellen Sie sicher, dass der Schlüssel aktiv ist

### Dashboard läuft nicht
- Prüfen Sie den Port: `lsof -i :8080`
- Verwenden Sie einen anderen Port: `DASHBOARD_PORT=8081`

## 🔐 Sicherheitshinweise

1. **Niemals API-Schlüssel in Git committen**
2. **`.env`-Datei zu `.gitignore` hinzufügen**
3. **Regelmäßig API-Schlüssel rotieren**
4. **Kostenlimits überwachen**
5. **Nur benötigte APIs aktivieren**

## 📞 Support

Bei Problemen:
1. Führen Sie `make config-validate` aus
2. Prüfen Sie die Logs: `make tail-logs`
3. Testen Sie einzelne Komponenten: `make test-ai`

Die Konfiguration ist erfolgreich, wenn alle APIs als "✅ Configured" angezeigt werden! 