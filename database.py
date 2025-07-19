#!/usr/bin/env python3
"""
Database Configuration and Session Management
Handles PostgreSQL connection, session creation, and database operations
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.pool import QueuePool
from contextlib import contextmanager
from typing import Generator
import logging

# Import models
from models import Base

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseManager:
    """Manages database connections and sessions"""
    
    def __init__(self, database_url: str = None):
        """Initialize database manager"""
        self.database_url = database_url or self._get_database_url()
        self.engine = None
        self.SessionLocal = None
        self._setup_engine()
    
    def _get_database_url(self) -> str:
        """Get database URL from environment or use default"""
        # Check for environment variables
        db_host = os.getenv('DB_HOST', 'localhost')
        db_port = os.getenv('DB_PORT', '5432')
        db_name = os.getenv('DB_NAME', 'sannetic_explorer')
        db_user = os.getenv('DB_USER', 'postgres')
        db_password = os.getenv('DB_PASSWORD', '')
        
        # Construct PostgreSQL URL
        if db_password:
            return f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
        else:
            return f"postgresql://{db_user}@{db_host}:{db_port}/{db_name}"
    
    def _setup_engine(self):
        """Setup SQLAlchemy engine with optimized settings"""
        try:
            self.engine = create_engine(
                self.database_url,
                poolclass=QueuePool,
                pool_size=10,
                max_overflow=20,
                pool_pre_ping=True,
                pool_recycle=3600,
                echo=os.getenv('DB_ECHO', 'false').lower() == 'true'
            )
            
            # Create session factory
            self.SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )
            
            logger.info(f"Database engine configured for: {self.database_url}")
            
        except Exception as e:
            logger.error(f"Failed to setup database engine: {e}")
            raise
    
    def create_tables(self):
        """Create all tables in the database"""
        try:
            Base.metadata.create_all(bind=self.engine)
            logger.info("All database tables created successfully")
        except Exception as e:
            logger.error(f"Failed to create tables: {e}")
            raise
    
    def drop_tables(self):
        """Drop all tables from the database"""
        try:
            Base.metadata.drop_all(bind=self.engine)
            logger.info("All database tables dropped successfully")
        except Exception as e:
            logger.error(f"Failed to drop tables: {e}")
            raise
    
    @contextmanager
    def get_session(self) -> Generator:
        """Get a database session with automatic cleanup"""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            session.close()
    
    def get_session_direct(self):
        """Get a database session directly (manual management required)"""
        return self.SessionLocal()
    
    def test_connection(self) -> bool:
        """Test database connection"""
        try:
            with self.get_session() as session:
                session.execute("SELECT 1")
            logger.info("Database connection test successful")
            return True
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            return False
    
    def get_database_info(self) -> dict:
        """Get database information and statistics"""
        try:
            with self.get_session() as session:
                # Get table counts
                table_counts = {}
                for table_name in Base.metadata.tables.keys():
                    result = session.execute(f"SELECT COUNT(*) FROM {table_name}")
                    count = result.scalar()
                    table_counts[table_name] = count
                
                # Get database size
                result = session.execute("""
                    SELECT pg_size_pretty(pg_database_size(current_database())) as size
                """)
                db_size = result.scalar()
                
                return {
                    "database_url": self.database_url,
                    "table_counts": table_counts,
                    "database_size": db_size,
                    "total_tables": len(table_counts)
                }
        except Exception as e:
            logger.error(f"Failed to get database info: {e}")
            return {"error": str(e)}

# Global database manager instance
db_manager = DatabaseManager()

# Convenience functions
def get_db_session():
    """Get a database session"""
    return db_manager.get_session_direct()

@contextmanager
def get_db():
    """Get a database session with automatic cleanup"""
    with db_manager.get_session() as session:
        yield session

def init_database():
    """Initialize the database (create tables)"""
    db_manager.create_tables()

def test_database():
    """Test database connection"""
    return db_manager.test_connection()

def get_database_stats():
    """Get database statistics"""
    return db_manager.get_database_info() 