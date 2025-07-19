"""
Database service for Sannetic Explorer

Database connection management and utility functions.
"""

import os
from typing import Generator, Dict, Any
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError

from ..models import Base


# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/sannetic_explorer")

# Create engine and session factory
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """Get database session dependency for FastAPI"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_database() -> None:
    """Initialize database tables"""
    try:
        Base.metadata.create_all(bind=engine)
        print("Database tables created successfully")
    except SQLAlchemyError as e:
        print(f"Error creating database tables: {e}")
        raise


def get_database_stats() -> Dict[str, Any]:
    """Get database statistics"""
    try:
        with engine.connect() as connection:
            # Get table sizes
            result = connection.execute(text("""
                SELECT 
                    schemaname,
                    tablename,
                    attname,
                    n_distinct,
                    correlation
                FROM pg_stats 
                WHERE schemaname = 'public'
                ORDER BY tablename, attname
            """))
            
            stats = {
                "tables": {},
                "total_rows": 0
            }
            
            for row in result:
                table_name = row.tablename
                if table_name not in stats["tables"]:
                    stats["tables"][table_name] = {
                        "columns": {},
                        "row_count": 0
                    }
                
                stats["tables"][table_name]["columns"][row.attname] = {
                    "n_distinct": row.n_distinct,
                    "correlation": row.correlation
                }
            
            # Get row counts
            for table_name in stats["tables"]:
                count_result = connection.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
                row_count = count_result.scalar()
                stats["tables"][table_name]["row_count"] = row_count
                stats["total_rows"] += row_count
            
            return stats
            
    except SQLAlchemyError as e:
        print(f"Error getting database stats: {e}")
        return {"error": str(e)} 