# Solar System Data Synchronization Script

The `sync.py` script provides comprehensive data synchronization capabilities for importing solar system data from JSON files into the PostgreSQL database.

## Features

- **Multi-format Support**: Handles JSON and CSV files
- **Intelligent Mapping**: Automatically maps data fields to database schema
- **Upsert Logic**: Updates existing records or creates new ones
- **Comprehensive Logging**: Detailed logging of all operations
- **CLI Interface**: Easy command-line usage
- **Data Validation**: Validates data structure and types
- **Unit Conversion**: Automatic unit conversions (AU to km, °C to K, etc.)

## Usage

### Basic Usage

```bash
# Synchronize all data (insert new, update existing)
python sync.py update

# Synchronize without updating existing records
python sync.py update --no-update

# Use custom data directory
python sync.py update --data-dir /path/to/data

# Enable verbose logging
python sync.py update --verbose
```

### Command Line Options

- `command`: Either "update" or "sync" (both do the same thing)
- `--data-dir`: Path to data directory (default: "Data")
- `--no-update`: Skip updating existing records
- `--verbose, -v`: Enable verbose logging

## Data Structure Requirements

### Directory Structure

```
Data/
├── Planets/
│   ├── template.json
│   ├── earth.json
│   ├── mars.json
│   └── ...
├── Stars/
│   ├── template.json
│   ├── sun.json
│   └── ...
├── NaturalSatellites/
│   ├── template.json
│   ├── moon.json
│   └── ...
├── Satellites/
│   ├── template.json
│   ├── gps.json
│   └── ...
└── Spacecraft/
    ├── template.json
    ├── voyager1.json
    └── ...
```

### Supported Categories

- **Planets** → `planet` type
- **Stars** → `star` type
- **NaturalSatellites** → `moon` type
- **Satellites** → `satellite` type
- **Spacecraft** → `spacecraft` type
- **Asteroids** → `asteroid` type
- **Comets** → `comet` type

### Data Format Examples

#### Planet Data (JSON)

```json
{
  "name": "Earth",
  "type": "terrestrial planet",
  "mass": {
    "value": 5.972e24,
    "unit": "kg"
  },
  "diameter": {
    "value": 12742,
    "unit": "km"
  },
  "gravity": {
    "value": 9.81,
    "unit": "m/s²"
  },
  "orbit": {
    "semiMajorAxis": {
      "value": 1.0,
      "unit": "AU"
    },
    "eccentricity": 0.0167,
    "orbitalPeriod": {
      "value": 365.25,
      "unit": "days"
    },
    "orbitalSpeed": {
      "value": 29.78,
      "unit": "km/s"
    }
  },
  "atmosphere": {
    "present": true,
    "pressure": {
      "value": 101325,
      "unit": "Pa"
    },
    "composition": {
      "nitrogen": "78%",
      "oxygen": "21%"
    }
  },
  "surface": {
    "type": "rocky",
    "features": ["mountains", "oceans", "continents"]
  },
  "rings": {
    "hasRings": false
  },
  "discovery": {
    "date": "prehistoric",
    "discoverer": "unknown"
  },
  "metadata": {
    "dataQuality": "excellent"
  },
  "dataSources": {
    "nasa": "verified",
    "esa": "verified"
  }
}
```

#### Star Data (JSON)

```json
{
  "name": "Sun",
  "type": "G-type main-sequence star",
  "mass": {
    "value": 1.989e30,
    "unit": "kg"
  },
  "radius": {
    "value": 696340,
    "unit": "km"
  },
  "stellarParameters": {
    "spectralType": "G2V",
    "luminosity": {
      "value": 1,
      "unit": "L☉"
    },
    "effectiveTemperature": {
      "value": 5778,
      "unit": "K"
    },
    "absoluteMagnitude": {
      "value": 4.83,
      "unit": "mag"
    },
    "apparentMagnitude": {
      "value": -26.74,
      "unit": "mag"
    }
  },
  "discovery": {
    "date": "prehistoric",
    "discoverer": "unknown"
  },
  "metadata": {
    "dataQuality": "excellent"
  }
}
```

#### Natural Satellite Data (JSON)

```json
{
  "name": "Moon",
  "type": "natural satellite",
  "parentBody": "Earth",
  "mass": {
    "value": 7.34767309e22,
    "unit": "kg"
  },
  "radius": {
    "value": 1737.4,
    "unit": "km"
  },
  "orbit": {
    "semiMajorAxis": {
      "value": 384400,
      "unit": "km"
    },
    "eccentricity": 0.0549,
    "orbitalPeriod": {
      "value": 27.322,
      "unit": "days"
    },
    "orbitalSpeed": {
      "value": 1.022,
      "unit": "km/s"
    }
  },
  "atmosphere": {
    "present": false
  },
  "surface": {
    "type": "rocky",
    "features": ["craters", "maria", "highlands"]
  },
  "discovery": {
    "date": "prehistoric",
    "discoverer": "unknown"
  },
  "metadata": {
    "dataQuality": "excellent"
  }
}
```

## Field Mapping

The script automatically maps JSON fields to database columns:

### Basic Properties

| JSON Field | Database Column | Notes |
|------------|----------------|-------|
| `name` | `name` | Required |
| `type` | `subtype` | Celestial body subtype |
| `mass.value` | `mass_kg` | Auto-converts units |
| `diameter.value` | `radius_km` | Auto-converts to radius |
| `radius.value` | `radius_km` | Direct mapping |
| `gravity.value` | `surface_gravity_ms2` | Auto-converts units |

### Orbital Properties

| JSON Field | Database Column | Notes |
|------------|----------------|-------|
| `orbit.semiMajorAxis.value` | `semi_major_axis_km` | Auto-converts AU to km |
| `orbit.eccentricity` | `eccentricity` | Direct mapping |
| `orbit.orbitalPeriod.value` | `orbital_period_days` | Auto-converts units |
| `orbit.orbitalSpeed.value` | `orbital_speed_kms` | Direct mapping |

### Physical Properties

| JSON Field | Database Column | Notes |
|------------|----------------|-------|
| `atmosphere.present` | `has_atmosphere` | Boolean conversion |
| `atmosphere.pressure.value` | `atmospheric_pressure_pa` | Auto-converts units |
| `atmosphere.composition` | `atmospheric_composition` | JSON storage |
| `surface.type` | `surface_type` | Direct mapping |
| `surface.features` | `surface_features` | Array storage |
| `rings.hasRings` | `has_rings` | Boolean conversion |

### Stellar Properties

| JSON Field | Database Column | Notes |
|------------|----------------|-------|
| `stellarParameters.spectralType` | `spectral_type` | Direct mapping |
| `stellarParameters.luminosity.value` | `luminosity_lsun` | Direct mapping |
| `stellarParameters.effectiveTemperature.value` | `effective_temperature_k` | Direct mapping |

## Unit Conversions

The script automatically handles unit conversions:

### Distance Units
- **AU** → **km** (1 AU = 149,597,870.7 km)
- **m** → **km** (1 m = 0.001 km)
- **R⊕** → **km** (1 R⊕ = 6,371 km)

### Mass Units
- **kg** → **kg** (no conversion)
- **g** → **kg** (1 g = 0.001 kg)
- **M⊕** → **kg** (1 M⊕ = 5.972e24 kg)

### Temperature Units
- **K** → **K** (no conversion)
- **°C** → **K** (T(K) = T(°C) + 273.15)
- **°F** → **K** (T(K) = (T(°F) - 32) × 5/9 + 273.15)

### Pressure Units
- **Pa** → **Pa** (no conversion)
- **bar** → **Pa** (1 bar = 100,000 Pa)
- **atm** → **Pa** (1 atm = 101,325 Pa)

### Time Units
- **days** → **days** (no conversion)
- **hours** → **days** (1 hour = 1/24 days)

## Logging

The script provides comprehensive logging:

- **File logging**: All operations logged to `sync.log`
- **Console logging**: Progress and statistics displayed
- **Verbose mode**: Detailed debug information with `--verbose`

### Log Levels

- **INFO**: General progress and statistics
- **DEBUG**: Detailed field mapping and conversions
- **WARNING**: Non-critical issues (missing fields, etc.)
- **ERROR**: Critical errors that prevent processing

## Error Handling

The script handles various error conditions gracefully:

- **Missing files**: Logs warning and continues
- **Invalid JSON**: Logs error and skips file
- **Database errors**: Logs error and continues with next record
- **Missing required fields**: Logs warning and uses defaults

## Performance

### Optimization Features

- **Batch processing**: Processes files efficiently
- **Database transactions**: Uses transactions for data integrity
- **Memory efficient**: Processes one record at a time
- **Connection pooling**: Reuses database connections

### Expected Performance

- **Small datasets** (< 100 records): < 1 minute
- **Medium datasets** (100-1000 records): 1-5 minutes
- **Large datasets** (> 1000 records): 5-15 minutes

## Testing

Run the test script to verify functionality:

```bash
python test_sync.py
```

The test script:
1. Creates sample data files
2. Runs synchronization
3. Verifies database records
4. Cleans up test data

## Integration with Backend

The sync script integrates seamlessly with the FastAPI backend:

1. **Database compatibility**: Uses same models and schema
2. **Data consistency**: Maintains referential integrity
3. **API ready**: Imported data immediately available via API
4. **Incremental updates**: Can run repeatedly without duplicates

## Troubleshooting

### Common Issues

1. **Database connection failed**:
   - Check database is running
   - Verify connection parameters
   - Ensure database is initialized

2. **Missing data files**:
   - Check data directory path
   - Verify file permissions
   - Ensure JSON files are valid

3. **Field mapping errors**:
   - Check JSON structure matches expected format
   - Verify required fields are present
   - Review field mapping documentation

4. **Unit conversion errors**:
   - Check unit values are valid
   - Verify supported units are used
   - Review unit conversion table

### Debug Mode

Enable verbose logging for detailed debugging:

```bash
python sync.py update --verbose
```

This will show:
- Field mapping details
- Unit conversion steps
- Database operations
- Error details 