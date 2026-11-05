#!/usr/bin/env python3
"""
Script to create .env file from env.example with basic Docker-compatible defaults
"""

import os
import shutil
from pathlib import Path

def create_env_file():
    """Create .env file from env.example with Docker defaults"""
    
    project_root = Path(__file__).parent.parent
    env_example_path = project_root / "env.example"
    env_path = project_root / ".env"
    
    print("🔧 Creating .env file for Docker Compose...")
    
    # Check if .env already exists
    if env_path.exists():
        print("⚠️  .env file already exists!")
        response = input("Do you want to overwrite it? (y/N): ").lower().strip()
        if response != 'y':
            print("❌ Aborted. Keeping existing .env file.")
            return False
    
    # Check if env.example exists
    if not env_example_path.exists():
        print("❌ env.example file not found!")
        return False
    
    try:
        # Copy env.example to .env
        shutil.copy2(env_example_path, env_path)
        
        # Read the content and make Docker-compatible modifications
        with open(env_path, 'r') as f:
            content = f.read()
        
        # Replace placeholder values with Docker-compatible defaults
        replacements = {
            'your_openai_api_key_here': 'sk-placeholder-key-replace-with-real-key',
            'your_n2yo_api_key_here': 'placeholder-replace-with-real-key',
            'your_space_track_username': 'placeholder-username',
            'your_space_track_password': 'placeholder-password',
            'your_secret_key_here': 'dev-secret-key-change-in-production',
            'DEBUG_MODE=false': 'DEBUG_MODE=false',
            'DEVELOPMENT_MODE=false': 'DEVELOPMENT_MODE=true'
        }
        
        for old, new in replacements.items():
            content = content.replace(old, new)
        
        # Add Docker-specific environment variables
        docker_vars = """

# =============================================================================
# DOCKER CONFIGURATION (Added automatically)
# =============================================================================

# Database Configuration for Docker
POSTGRES_DB=sannetic_explorer
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DATABASE_URL=postgresql://postgres:postgres@db:5432/sannetic_explorer

# Redis Configuration for Docker (container port; host publish is HOST_REDIS_PORT)
REDIS_HOST=redis
REDIS_PORT=6379
"""
        
        content += docker_vars
        
        # Write the modified content back
        with open(env_path, 'w') as f:
            f.write(content)
        
        print("✅ .env file created successfully!")
        print("📝 Default values have been set for Docker Compose.")
        print("🔑 Please edit .env and add your real API keys:")
        print("   - OPENAI_API_KEY")
        print("   - N2YO_API_KEY") 
        print("   - SPACE_TRACK_USERNAME")
        print("   - SPACE_TRACK_PASSWORD")
        print("")
        print("🚀 You can now run: make build && make up")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating .env file: {e}")
        return False

if __name__ == "__main__":
    success = create_env_file()
    exit(0 if success else 1) 