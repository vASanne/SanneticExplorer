#!/usr/bin/env python3
"""
Sannetic Explorer Project Reorganization Script
Automatically reorganizes the project structure for better maintainability
"""

import os
import shutil
import sys
from pathlib import Path
from typing import List, Tuple, Dict
import json

class ProjectReorganizer:
    def __init__(self):
        self.root_dir = Path.cwd()
        self.backup_dir = self.root_dir / "backup_before_reorganization"
        self.changes_made = []
        
    def log_change(self, action: str, source: str, destination: str = None):
        """Log changes for rollback capability"""
        change = {
            'action': action,
            'source': str(source),
            'destination': str(destination) if destination else None,
            'timestamp': str(Path().stat().st_mtime)
        }
        self.changes_made.append(change)
        print(f"📝 {action}: {source} -> {destination}" if destination else f"📝 {action}: {source}")

    def create_backup(self) -> bool:
        """Create backup of current project state"""
        print("🔄 Creating backup...")
        try:
            if self.backup_dir.exists():
                shutil.rmtree(self.backup_dir)
            
            # Create backup directory
            self.backup_dir.mkdir()
            
            # Copy all files except backup and logs
            for item in self.root_dir.iterdir():
                if item.name not in ['backup_before_reorganization', 'logs', '.git']:
                    if item.is_file():
                        shutil.copy2(item, self.backup_dir / item.name)
                    elif item.is_dir():
                        shutil.copytree(item, self.backup_dir / item.name)
            
            # Save changes log
            with open(self.backup_dir / 'reorganization_changes.json', 'w') as f:
                json.dump(self.changes_made, f, indent=2)
            
            print(f"✅ Backup created at: {self.backup_dir}")
            return True
        except Exception as e:
            print(f"❌ Backup failed: {e}")
            return False

    def create_directories(self) -> bool:
        """Create new directory structure"""
        print("📁 Creating directory structure...")
        
        directories = [
            'backend/migrations',
            'backend/scripts', 
            'backend/tests',
            'infrastructure/docker',
            'infrastructure/scripts',
            'infrastructure/configs',
            'docs/guides',
            'docs/api',
            'docs/deployment',
            'data/celestial_bodies',
            'data/migrations',
            'data/cache'
        ]
        
        try:
            for dir_path in directories:
                full_path = self.root_dir / dir_path
                full_path.mkdir(parents=True, exist_ok=True)
                self.log_change("CREATE_DIR", dir_path)
            
            print("✅ Directory structure created")
            return True
        except Exception as e:
            print(f"❌ Directory creation failed: {e}")
            return False

    def move_backend_files(self) -> bool:
        """Move backend-related files"""
        print("🐍 Moving backend files...")
        
        backend_moves = [
            ('sannetic_explorer', 'backend/sannetic_explorer'),
            ('models.py', 'backend/models.py'),
            ('database.py', 'backend/database.py'),
            ('data_migration.py', 'backend/scripts/data_migration.py'),
            ('create_remaining_models.py', 'backend/scripts/create_remaining_models.py'),
            ('Dockerfile.backend', 'backend/Dockerfile.backend'),
            ('Dockerfile.worker', 'backend/Dockerfile.worker'),
            ('requirements_backend.txt', 'backend/requirements.txt'),
            ('README_BACKEND.md', 'backend/README.md'),
            ('app.py', 'backend/app.py'),
            ('migration_add_update_log.sql', 'backend/migrations/migration_add_update_log.sql'),
            ('migration_add_orbital_fields.sql', 'backend/migrations/migration_add_orbital_fields.sql'),
            ('init-db.sql', 'backend/migrations/init-db.sql'),
            ('tests', 'backend/tests')
        ]
        
        return self._move_files(backend_moves, "Backend")

    def move_infrastructure_files(self) -> bool:
        """Move infrastructure-related files"""
        print("🏗️ Moving infrastructure files...")
        
        infra_moves = [
            ('Dockerfile', 'infrastructure/docker/Dockerfile'),
            ('startup.sh', 'infrastructure/scripts/startup.sh'),
            ('crontab', 'infrastructure/configs/crontab'),
            ('crontab.worker', 'infrastructure/configs/crontab.worker'),
            ('docker-compose.backend.yml', 'infrastructure/docker-compose.backend.yml'),
            ('docker-compose.automation.yml', 'infrastructure/docker-compose.automation.yml'),
            ('web_dashboard.py', 'infrastructure/scripts/web_dashboard.py'),
            ('Makefile.backend', 'infrastructure/Makefile.backend'),
            ('scripts', 'infrastructure/scripts')
        ]
        
        return self._move_files(infra_moves, "Infrastructure")

    def move_documentation_files(self) -> bool:
        """Move documentation files"""
        print("📚 Moving documentation files...")
        
        doc_moves = [
            ('CONFIGURATION_GUIDE.md', 'docs/guides/CONFIGURATION_GUIDE.md'),
            ('LOGGING_GUIDE.md', 'docs/guides/LOGGING_GUIDE.md'),
            ('WEB_DASHBOARD_GUIDE.md', 'docs/guides/WEB_DASHBOARD_GUIDE.md'),
            ('INFRASTRUCTURE_TESTING_GUIDE.md', 'docs/guides/INFRASTRUCTURE_TESTING_GUIDE.md'),
            ('TESTING_GUIDE.md', 'docs/guides/TESTING_GUIDE.md'),
            ('AI_IMPLEMENTATION_SUMMARY.md', 'docs/guides/AI_IMPLEMENTATION_SUMMARY.md'),
            ('AI_INTEGRATION_GUIDE.md', 'docs/guides/AI_INTEGRATION_GUIDE.md'),
            ('DELTA_UPDATE_IMPLEMENTATION.md', 'docs/guides/DELTA_UPDATE_IMPLEMENTATION.md'),
            ('ORBITAL_PROPAGATION_SYSTEM.md', 'docs/guides/ORBITAL_PROPAGATION_SYSTEM.md'),
            ('UPDATE_CYCLE_IMPLEMENTATION.md', 'docs/guides/UPDATE_CYCLE_IMPLEMENTATION.md'),
            ('UPDATE_CYCLE_PLAN.md', 'docs/guides/UPDATE_CYCLE_PLAN.md'),
            ('API_OPTIMIZATION_GUIDE.md', 'docs/api/API_OPTIMIZATION_GUIDE.md'),
            ('concept.md', 'docs/concept.md'),
            ('RULES.md', 'docs/RULES.md'),
            ('ruleset.md', 'docs/ruleset.md')
        ]
        
        return self._move_files(doc_moves, "Documentation")

    def move_data_files(self) -> bool:
        """Move data files"""
        print("📊 Moving data files...")
        
        data_moves = [
            ('Data', 'data/celestial_bodies'),
            ('cache', 'data/cache'),
            ('templates', 'data/templates')
        ]
        
        return self._move_files(data_moves, "Data")

    def cleanup_files(self) -> bool:
        """Remove unnecessary files"""
        print("🧹 Cleaning up unnecessary files...")
        
        files_to_remove = [
            '.DS_Store',
            'test_pre_commit.py'
        ]
        
        try:
            for file_name in files_to_remove:
                file_path = self.root_dir / file_name
                if file_path.exists():
                    file_path.unlink()
                    self.log_change("REMOVE", file_name)
                    print(f"🗑️ Removed: {file_name}")
            
            # Remove venv if exists
            venv_path = self.root_dir / 'venv'
            if venv_path.exists():
                shutil.rmtree(venv_path)
                self.log_change("REMOVE", 'venv')
                print("🗑️ Removed: venv/")
            
            print("✅ Cleanup completed")
            return True
        except Exception as e:
            print(f"❌ Cleanup failed: {e}")
            return False

    def _move_files(self, moves: List[Tuple[str, str]], category: str) -> bool:
        """Helper function to move files"""
        try:
            for source, destination in moves:
                source_path = self.root_dir / source
                dest_path = self.root_dir / destination
                
                if source_path.exists():
                    # Create destination directory if needed
                    dest_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Move file/directory
                    shutil.move(str(source_path), str(dest_path))
                    self.log_change("MOVE", source, destination)
                    print(f"📦 Moved: {source} -> {destination}")
                else:
                    print(f"⚠️ Source not found: {source}")
            
            print(f"✅ {category} files moved successfully")
            return True
        except Exception as e:
            print(f"❌ {category} file move failed: {e}")
            return False

    def update_configurations(self) -> bool:
        """Update configuration files for new structure"""
        print("⚙️ Updating configurations...")
        
        try:
            # Update docker-compose.yml
            self._update_docker_compose()
            
            # Update main.py
            self._update_main_py()
            
            # Update Makefile
            self._update_makefile()
            
            print("✅ Configurations updated")
            return True
        except Exception as e:
            print(f"❌ Configuration update failed: {e}")
            return False

    def _update_docker_compose(self):
        """Update docker-compose.yml for new structure"""
        compose_file = self.root_dir / 'docker-compose.yml'
        if compose_file.exists():
            content = compose_file.read_text()
            
            # Update backend context
            content = content.replace(
                'context: .',
                'context: ./backend'
            )
            
            # Update frontend context
            content = content.replace(
                'context: ./frontend',
                'context: ./frontend'
            )
            
            # Update volumes
            content = content.replace(
                './Data:/app/Data:ro',
                './data:/app/data:ro'
            )
            
            compose_file.write_text(content)
            self.log_change("UPDATE", "docker-compose.yml")

    def _update_main_py(self):
        """Update main.py for new backend path"""
        main_file = self.root_dir / 'main.py'
        if main_file.exists():
            content = main_file.read_text()
            
            # Add backend path
            if 'sys.path.append' not in content:
                new_content = """#!/usr/bin/env python3
\"\"\"
Main entry point for Sannetic Explorer

Starts the FastAPI application with the restructured package.
\"\"\"

import sys
sys.path.append('./backend')

import uvicorn
from sannetic_explorer.api import app

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
"""
                main_file.write_text(new_content)
                self.log_change("UPDATE", "main.py")

    def _update_makefile(self):
        """Update Makefile for new structure"""
        makefile = self.root_dir / 'Makefile'
        if makefile.exists():
            content = makefile.read_text()
            
            # Update backend test command
            content = content.replace(
                'cd sannetic_explorer && python -m pytest',
                'cd backend && python -m pytest'
            )
            
            # Update frontend test command
            content = content.replace(
                'cd frontend && npm test',
                'cd frontend && npm test'
            )
            
            makefile.write_text(content)
            self.log_change("UPDATE", "Makefile")

    def create_docs_index(self) -> bool:
        """Create documentation index"""
        print("📖 Creating documentation index...")
        
        try:
            docs_index = """# Sannetic Explorer Documentation

## 📚 Guides

- [Configuration Guide](guides/CONFIGURATION_GUIDE.md) - System configuration
- [Logging Guide](guides/LOGGING_GUIDE.md) - Logging setup and management
- [Web Dashboard Guide](guides/WEB_DASHBOARD_GUIDE.md) - Dashboard features
- [Infrastructure Testing Guide](guides/INFRASTRUCTURE_TESTING_GUIDE.md) - Docker testing
- [Testing Guide](guides/TESTING_GUIDE.md) - Test suite documentation
- [AI Implementation Summary](guides/AI_IMPLEMENTATION_SUMMARY.md) - AI features
- [AI Integration Guide](guides/AI_INTEGRATION_GUIDE.md) - AI integration
- [Delta Update Implementation](guides/DELTA_UPDATE_IMPLEMENTATION.md) - Update system
- [Orbital Propagation System](guides/ORBITAL_PROPAGATION_SYSTEM.md) - Orbital calculations
- [Update Cycle Implementation](guides/UPDATE_CYCLE_IMPLEMENTATION.md) - Update cycles
- [Update Cycle Plan](guides/UPDATE_CYCLE_PLAN.md) - Update planning

## 🔌 API Documentation

- [API Optimization Guide](api/API_OPTIMIZATION_GUIDE.md) - API performance

## 🚀 Deployment

- [Project Concept](concept.md) - Project overview and concept
- [Rules](RULES.md) - Project rules and guidelines
- [Ruleset](ruleset.md) - Detailed ruleset

## 📁 Project Structure

```
SanneticExplorer/
├── backend/           # Python FastAPI backend
├── frontend/          # SvelteKit frontend
├── infrastructure/    # Docker and deployment
├── docs/             # Documentation
├── data/             # Data files
├── e2e/              # End-to-end tests
└── logs/             # Log files
```

## 🔗 Quick Links

- [Main README](../README.md) - Project overview
- [Backend README](../backend/README.md) - Backend documentation
- [Frontend README](../frontend/README.md) - Frontend documentation
"""
            
            docs_index_file = self.root_dir / 'docs' / 'README.md'
            docs_index_file.write_text(docs_index)
            self.log_change("CREATE", "docs/README.md")
            
            print("✅ Documentation index created")
            return True
        except Exception as e:
            print(f"❌ Documentation index creation failed: {e}")
            return False

    def run_reorganization(self) -> bool:
        """Run complete reorganization"""
        print("🚀 Starting Sannetic Explorer Project Reorganization")
        print("=" * 60)
        
        steps = [
            ("Create backup", self.create_backup),
            ("Create directories", self.create_directories),
            ("Move backend files", self.move_backend_files),
            ("Move infrastructure files", self.move_infrastructure_files),
            ("Move documentation files", self.move_documentation_files),
            ("Move data files", self.move_data_files),
            ("Cleanup files", self.cleanup_files),
            ("Update configurations", self.update_configurations),
            ("Create docs index", self.create_docs_index)
        ]
        
        for step_name, step_func in steps:
            print(f"\n🔄 {step_name}...")
            if not step_func():
                print(f"❌ Reorganization failed at: {step_name}")
                return False
        
        # Save final changes log
        with open(self.root_dir / 'reorganization_changes.json', 'w') as f:
            json.dump(self.changes_made, f, indent=2)
        
        print("\n" + "=" * 60)
        print("✅ REORGANIZATION COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print(f"📁 Backup created at: {self.backup_dir}")
        print(f"📝 Changes logged in: reorganization_changes.json")
        print("\n🎯 Next steps:")
        print("1. Review the new structure")
        print("2. Test the application")
        print("3. Update any remaining references")
        print("4. Commit the changes")
        
        return True

    def rollback(self) -> bool:
        """Rollback reorganization using backup"""
        print("🔄 Rolling back reorganization...")
        
        try:
            if not self.backup_dir.exists():
                print("❌ Backup not found")
                return False
            
            # Remove current files (except backup and git)
            for item in self.root_dir.iterdir():
                if item.name not in ['backup_before_reorganization', '.git', 'logs']:
                    if item.is_file():
                        item.unlink()
                    elif item.is_dir():
                        shutil.rmtree(item)
            
            # Restore from backup
            for item in self.backup_dir.iterdir():
                if item.name != 'reorganization_changes.json':
                    dest = self.root_dir / item.name
                    if item.is_file():
                        shutil.copy2(item, dest)
                    elif item.is_dir():
                        shutil.copytree(item, dest)
            
            print("✅ Rollback completed")
            return True
        except Exception as e:
            print(f"❌ Rollback failed: {e}")
            return False

def main():
    """Main function"""
    reorganizer = ProjectReorganizer()
    
    if len(sys.argv) > 1 and sys.argv[1] == '--rollback':
        success = reorganizer.rollback()
    else:
        success = reorganizer.run_reorganization()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 