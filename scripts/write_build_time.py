#!/usr/bin/env python3
"""
Script to write build time to database during container build process.
Build time format: yyyyMMDDhhmm
"""

import os
import sys
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor

def get_db_connection():
    """Get database connection using environment variables"""
    try:
        conn = psycopg2.connect(
            host=os.getenv('POSTGRES_HOST', 'db'),
            port=os.getenv('POSTGRES_PORT', '5432'),
            database=os.getenv('POSTGRES_DB', 'sannetic_explorer'),
            user=os.getenv('POSTGRES_USER', 'postgres'),
            password=os.getenv('POSTGRES_PASSWORD', 'postgres')
        )
        return conn
    except Exception as e:
        print(f"Database connection failed: {e}")
        return None

def create_build_info_table(conn):
    """Create build_info table if it doesn't exist"""
    try:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS build_info (
                    id SERIAL PRIMARY KEY,
                    build_time VARCHAR(12) NOT NULL,
                    build_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    component VARCHAR(50) DEFAULT 'frontend'
                );
            """)
        conn.commit()
        print("✅ Build info table created/verified")
        return True
    except Exception as e:
        print(f"❌ Failed to create build_info table: {e}")
        return False

def write_build_time(conn, component='frontend', event_type='start'):
    """Write current build/start time to database"""
    try:
        # Generate time in yyyyMMDDhhmm format
        current_time = datetime.now().strftime('%Y%m%d%H%M')
        
        with conn.cursor() as cur:
            # Delete old entries for this component (keep only latest)
            cur.execute("DELETE FROM build_info WHERE component = %s", (component,))
            
            # Insert new time
            cur.execute("""
                INSERT INTO build_info (build_time, component) 
                VALUES (%s, %s)
            """, (current_time, component))
        
        conn.commit()
        print(f"✅ {event_type.capitalize()} time written to database: {current_time} (component: {component})")
        return current_time
    except Exception as e:
        print(f"❌ Failed to write {event_type} time: {e}")
        return None

def main():
    """Main function"""
    component = sys.argv[1] if len(sys.argv) > 1 else 'frontend'
    event_type = sys.argv[2] if len(sys.argv) > 2 else 'start'
    
    print(f"🔧 Writing {event_type} time for component: {component}")
    
    # Get database connection
    conn = get_db_connection()
    if not conn:
        print("❌ Could not connect to database")
        sys.exit(1)
    
    try:
        # Create table if needed
        if not create_build_info_table(conn):
            sys.exit(1)
        
        # Write start/build time
        result_time = write_build_time(conn, component, event_type)
        if not result_time:
            sys.exit(1)
        
        print(f"🎯 {event_type.capitalize()} time {result_time} successfully written to database")
        
    finally:
        conn.close()

if __name__ == "__main__":
    main() 