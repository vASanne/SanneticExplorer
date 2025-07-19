# Infrastrukturkonzept: Interaktive Simulation des Sonnensystems im Browser

---

## 1. Systemarchitektur – Überblick

Die Anwendung besteht aus drei Hauptkomponenten:

- **Frontend** (Client, Browser): Visualisierung und Benutzerinteraktion  
- **Backend** (Server): Datenverwaltung, API, Konfigurationsmanagement  
- **Datenbank**: Speicherung astronomischer Daten, Benutzerszenarien, Konfigurationen

Das Ziel ist eine modulare, leicht erweiterbare und gut wartbare Infrastruktur.

---

## 2. Datenbank

**Empfehlung:** [PostgreSQL](https://www.postgresql.org/)

**Begründung:**
- Open Source, leistungsfähig, zuverlässig, kostenlos
- Starke Unterstützung für strukturierte und semistrukturierte Daten (z. B. JSON)
- Gute Anbindung an gängige Backend-Frameworks
- Erweiterbar für spätere Features (z. B. User-Accounts, Szenarienverwaltung)

**Alternative:** SQLite (für einfachen Start ohne Serverprozess, aber weniger zukunftssicher)

**Modellvorschlag:**
- Tabellen: `celestial_bodies`, `orbits`, `scenarios`, `users` (später)
- JSON-Felder für flexible Speicherung komplexer Eigenschaften
- Import der bestehenden astronomischen JSON-Daten in die DB

---

## 3. Backend Framework

**Empfehlung:** [FastAPI](https://fastapi.tiangolo.com/)

**Begründung:**
- Modernes, sehr schnelles Python-Framework (async-fähig)
- Einfache API-Definition via OpenAPI/Swagger (automatische Dokumentation)
- Sehr gute Performance und Skalierbarkeit
- Kostenlos & Open Source
- Gute Community und viele Tutorials

**Backend-Aufgaben:**
- Aufbereitung und Bereitstellung astronomischer Daten als REST-API
- Endpunkte für Szenarien, Nutzerkonfiguration etc.
- Optional: Berechnung/Simulation von Bewegungen
- Authentifizierung (für spätere Erweiterungen)

---

## 4. Frontend Framework

**Empfehlung:** [React](https://react.dev/) + [Three.js](https://threejs.org/)

**Begründung:**
- React: Moderne UI-Entwicklung, Komponentenmodell, Open Source, große Community
- Three.js: Marktführer für 3D-WebGL-Visualisierung, kostenlos, flexibel
- Gute Integration über [react-three-fiber](https://docs.pmnd.rs/react-three-fiber)
- Viele Open-Source-Beispiele für 3D-Simulationen verfügbar

**Alternativen:** Vue.js + Three.js oder reines Three.js für Minimalismus

---

## 5. Weitere Dienste & Tools

- **Versionsverwaltung:** Git + GitHub/GitLab (kostenlos)
- **Deployment:** Lokale Server oder Docker-Container für Entwicklung
- **Dokumentation:** Markdown (README, Wikis), [MkDocs](https://www.mkdocs.org/) o. Ä.
- **Testing:** Jest (Frontend), Pytest (Backend)
- **Task-Management:** GitHub Issues/Projects (kostenlos)

---

## 6. Roadmap / Fahrplan

### Phase 1 – Prototyp (0–2 Monate)
1. **Initiale Planung & Setup (Woche 1–2)**
   - Projektstruktur (Repo, Grundordner)
   - Auswahl und Einrichtung der Tools/Frameworks

2. **Backend- und Datenbank-Grundgerüst (Woche 3–4)**
   - Setup von FastAPI und PostgreSQL
   - Import der astronomischen JSON-Daten in die DB
   - Erste API-Endpunkte: Abruf von Planeten, Monden etc.

3. **Frontend-Prototyp (Woche 5–6)**
   - Grundstruktur in React (Vite o. Ä.)
   - Anbindung der API
   - Einfache 3D-Visualisierung mit Three.js (Sonne, Planeten auf Umlaufbahnen)

### Phase 2 – Funktionaler Ausbau (2–4 Monate)
1. **Erweiterung der Visualisierung (Monat 2–3)**
   - Hinzufügen von Monden, Satelliten
   - Realistische Bewegungen (Orbit-Simulation)
   - Animierte Darstellung (z. B. Zeitskala, Steuerung)

2. **Interaktive Features (Monat 3–4)**
   - Szenarienwechsel, Anpassung von Parametern (z. B. Masse, Umlaufbahnen)
   - Grundlegende Benutzeroberfläche (Parameter-Slider, Dropdowns)
   - Save/Load von Szenarien (Backend)

### Phase 3 – Erweiterung & Optimierung (4–8 Monate)
1. **Konfigurierbare Sonnensysteme**
   - Nutzerdefinierte Himmelskörper anlegen/bearbeiten/löschen
   - Speichern und Verwalten mehrerer Szenarien

2. **Performance & Usability**
   - Optimierung der 3D-Engine (Framerate, Level-of-Detail)
   - Verbesserte Benutzerführung

3. **Dokumentation & Testing**
   - Ausführliche technische Dokumentation
   - Unit- und Integrationstests

---

## 7. Zusammenfassung der wichtigsten Komponenten

| Schicht        | Empfehlung        | Open Source? | Kosten     |
|----------------|------------------|--------------|------------|
| Datenbank      | PostgreSQL       | Ja           | Kostenlos  |
| Backend        | FastAPI (Python) | Ja           | Kostenlos  |
| Frontend       | React + Three.js | Ja           | Kostenlos  |
| 3D-Engine      | Three.js         | Ja           | Kostenlos  |

---

## 8. Hinweise zur Erweiterbarkeit

- **Modularität:** Alle Frameworks sind modular, neue Features lassen sich leicht ergänzen.
- **Skalierung:** Das System kann problemlos für größere Datenmengen/Userzahlen erweitert werden.
- **Community & Support:** Für alle gewählten Tools gibt es viele Ressourcen und Open-Source-Beispiele.

---

**Bei Bedarf an konkreten Codebeispielen, Setup-Templates oder einem Schnellstart – einfach melden!**
