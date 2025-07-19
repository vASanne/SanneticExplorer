# ruleset.md

## Project Data Ruleset for Cursor

This ruleset defines all conventions and requirements for working with project data files using Cursor (or similar automated tools and assistants).\
It ensures consistent structure, data quality, and maintainability across the project.

---

### 1. Directory Structure & Data Organization

- All primary data objects are stored under the main project folder:\
  `Data/`
  - `NaturalSatellites/`   (natural moons)
  - `Planets/`             (planets)
  - `Satellites/`          (artificial satellites)
  - `Spacecraft/`          (spacecraft and probes)
  - `Stars/`               (stars, e.g. the Sun)
- Each of these subfolders contains:
  - One mandatory `.template.json` file that defines the object schema.
  - Multiple JSON data files, each representing a single object conforming to the schema.
  - An `index.json` file listing all objects in the folder (except the `.template.json`), plus providing a statistics section.

---

### 2. Template and Data File Requirements

- **Schema Definition**:

  - The `.template.json` in each subfolder provides the canonical property structure for all object files in that folder.
  - All object JSON files **must** strictly adhere to this schema.
  - If a required field is not available or data is missing, it must be set to `"noValue"`.

- **index.json**:

  - Each data folder **must** contain an `index.json` file.
  - `index.json` lists all object data files in the directory (excluding the `.template.json`).
  - It contains a statistics section (e.g. total objects, filled fields, percentage of missing values, etc.).
  - The format of `index.json` must itself be defined in the corresponding `.template.json`.

---

### 3. Data Consistency & Validation

- All new or modified object files **must** be validated against the `.template.json` schema of their directory.
- Any deviation from the schema (extra, missing, or misspelled properties) is **not permitted**.
- `"noValue"` must be used **explicitly** wherever a property is empty or information is missing.
- `index.json` and `.template.json` files are **mandatory** and must be updated whenever object data files are added, removed, or modified.

---

### 4. Scripts Folder

- The `scripts/` directory contains scripts exclusively for data collection and updating from external sources.
- **Scripts must not be used for data retrieval at runtime.**
- Scripts should only be run intentionally to refresh or extend data and must not alter files outside the `Data/` directory.

---

### 5. File Naming Conventions

- Data object files in each folder should use clear, descriptive filenames (e.g. `mars.json`, `io.json`).
- Avoid spaces and special characters in filenames.
- The only files allowed in a data folder: `.template.json`, `index.json`, and valid object data files.

---

### 6. General Best Practices

- All modifications to data files must be tracked via version control (e.g. Git).
- Any change to `.template.json` or schema **must** be reflected in all affected data files and in `index.json`.
- All automated tools (including Cursor) must strictly adhere to these rules when creating, editing, or validating files.

---

### 7. Example Directory Layout

```
Data/
  Planets/
    .template.json
    earth.json
    mars.json
    index.json
  NaturalSatellites/
    .template.json
    europa.json
    io.json
    index.json
  Spacecraft/
    .template.json
    voyager1.json
    index.json
  ...
scripts/
  fetch_nasa_data.py
  update_stats.py
```

---

### 8. Enforcement

- Any commit or automated action violating these rules should be rejected and flagged for review.
- Consistency checks should be implemented and run regularly.

---

**End of ruleset.**

