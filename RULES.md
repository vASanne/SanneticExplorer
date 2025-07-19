# Sannetic Explorer - Project Rules and Guidelines

## Data Management Rules

1. **Directory Structure**
   - All data must be stored in the `Data` directory
   - Each celestial body type has its own subdirectory:
     - `Data/Planets/`
     - `Data/NaturalSatellites/`
     - `Data/Spacecraft/`
     - `Data/Stars/`
   - Each directory must contain an `index.json` file

2. **Index Files**
   - Every data directory must contain an `index.json` file
   - Index files must list all available content JSON files
   - Index files must include metadata and statistics
   - Index files must be updated whenever content changes

3. **JSON Files**
   - All JSON files must follow their respective templates
   - Files must be properly formatted and validated
   - Cross-references must be valid and consistent
   - All required fields must be filled

4. **Data Enrichment**
   - All data enrichment must be done through containerized scripts
   - External data sources must be properly credited
   - API keys must be stored in `.env` file
   - Rate limiting must be respected for API calls

## Development Rules

1. **Docker Usage**
   - All Python scripts must be run within the Sannetic Explorer container
   - No direct Python execution outside the container
   - Container name must be `sannetic-explorer`
   - Data directory must be properly mounted

2. **Code Quality**
   - All code must be properly documented
   - Error handling must be implemented
   - Logging must be consistent
   - Type hints must be used

3. **Testing**
   - All changes must be validated
   - Data integrity must be maintained
   - Cross-references must be verified
   - Templates must be followed

4. **Version Control**
   - Meaningful commit messages
   - Feature branches for changes
   - Pull requests for reviews
   - No sensitive data in commits

## Security Rules

1. **API Keys**
   - All API keys must be in `.env` file
   - `.env` file must not be committed
   - Keys must be rotated regularly
   - Access must be logged

2. **Data Access**
   - Read-only access to data directory
   - Write access only through container
   - Regular backups required
   - Access logging enabled

## Maintenance Rules

1. **Updates**
   - Regular dependency updates
   - Security patches applied
   - Data validation runs
   - Index file updates

2. **Backups**
   - Regular data backups
   - Backup verification
   - Recovery testing
   - Archive maintenance

## Documentation Rules

1. **Code Documentation**
   - Function documentation
   - Type hints
   - Usage examples
   - Error handling

2. **Data Documentation**
   - Data sources
   - Update procedures
   - Validation rules
   - Cross-references

## Compliance

1. **Data Sources**
   - Proper attribution
   - License compliance
   - Usage terms
   - Rate limiting

2. **Security**
   - Data protection
   - Access control
   - Audit logging
   - Incident response 