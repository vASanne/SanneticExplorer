-- PostgreSQL Database Initialization Script
-- This script runs when the PostgreSQL container starts for the first time

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Create database user for application (optional)
-- CREATE USER sannetic_user WITH PASSWORD 'sannetic_user_password';
-- GRANT ALL PRIVILEGES ON DATABASE sannetic_explorer TO sannetic_user;

-- Set timezone
SET timezone = 'UTC';

-- Create custom functions for better performance
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create indexes for better performance
-- These will be created by SQLAlchemy, but we can add custom ones here if needed

-- Create a function to get celestial body hierarchy
CREATE OR REPLACE FUNCTION get_celestial_hierarchy(body_id UUID)
RETURNS TABLE (
    id UUID,
    name TEXT,
    type TEXT,
    level INTEGER,
    path TEXT
) AS $$
BEGIN
    RETURN QUERY
    WITH RECURSIVE hierarchy AS (
        -- Base case: the starting celestial body
        SELECT 
            cb.id,
            cb.name,
            cb.type,
            0 as level,
            ARRAY[cb.name] as path
        FROM celestial_bodies cb
        WHERE cb.id = body_id
        
        UNION ALL
        
        -- Recursive case: children of the current level
        SELECT 
            child.id,
            child.name,
            child.type,
            h.level + 1,
            h.path || child.name
        FROM celestial_bodies child
        JOIN hierarchy h ON child.parent_id = h.id
    )
    SELECT * FROM hierarchy
    ORDER BY level, name;
END;
$$ LANGUAGE plpgsql;

-- Create a function to search celestial bodies with full-text search
CREATE OR REPLACE FUNCTION search_celestial_bodies(search_term TEXT)
RETURNS TABLE (
    id UUID,
    name TEXT,
    type TEXT,
    similarity REAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        cb.id,
        cb.name,
        cb.type,
        GREATEST(
            similarity(cb.name, search_term),
            similarity(cb.type, search_term)
        ) as similarity
    FROM celestial_bodies cb
    WHERE 
        cb.name ILIKE '%' || search_term || '%'
        OR cb.type ILIKE '%' || search_term || '%'
        OR cb.alternative_names && ARRAY[search_term]
    ORDER BY similarity DESC;
END;
$$ LANGUAGE plpgsql;

-- Create a function to get orbital statistics
CREATE OR REPLACE FUNCTION get_orbital_statistics()
RETURNS TABLE (
    body_type TEXT,
    avg_orbital_period_days REAL,
    avg_eccentricity REAL,
    avg_inclination_degrees REAL,
    count_bodies BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        cb.type,
        AVG(op.orbital_period_days) as avg_orbital_period_days,
        AVG(op.eccentricity) as avg_eccentricity,
        AVG(op.inclination_degrees) as avg_inclination_degrees,
        COUNT(*) as count_bodies
    FROM celestial_bodies cb
    LEFT JOIN orbital_parameters op ON cb.id = op.celestial_body_id
    WHERE op.orbital_period_days IS NOT NULL
    GROUP BY cb.type
    ORDER BY count_bodies DESC;
END;
$$ LANGUAGE plpgsql;

-- Create a function to get physical statistics
CREATE OR REPLACE FUNCTION get_physical_statistics()
RETURNS TABLE (
    body_type TEXT,
    avg_mass_kg REAL,
    avg_radius_km REAL,
    avg_surface_gravity_ms2 REAL,
    count_bodies BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        cb.type,
        AVG(cb.mass_kg) as avg_mass_kg,
        AVG(cb.radius_km) as avg_radius_km,
        AVG(cb.surface_gravity_ms2) as avg_surface_gravity_ms2,
        COUNT(*) as count_bodies
    FROM celestial_bodies cb
    WHERE cb.mass_kg IS NOT NULL OR cb.radius_km IS NOT NULL
    GROUP BY cb.type
    ORDER BY count_bodies DESC;
END;
$$ LANGUAGE plpgsql;

-- Create a function to get exploration statistics
CREATE OR REPLACE FUNCTION get_exploration_statistics()
RETURNS TABLE (
    body_name TEXT,
    event_count BIGINT,
    last_event_date TIMESTAMP,
    total_images INTEGER,
    total_data_gb REAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        cb.name,
        COUNT(eh.id) as event_count,
        MAX(eh.event_date) as last_event_date,
        COALESCE(SUM(eh.images_taken), 0) as total_images,
        COALESCE(SUM(eh.data_volume_gb), 0) as total_data_gb
    FROM celestial_bodies cb
    LEFT JOIN exploration_history eh ON cb.id = eh.celestial_body_id
    GROUP BY cb.id, cb.name
    HAVING COUNT(eh.id) > 0
    ORDER BY event_count DESC;
END;
$$ LANGUAGE plpgsql;

-- Create a function to get simulation state at specific time
CREATE OR REPLACE FUNCTION get_simulation_state_at_time(target_time TIMESTAMP)
RETURNS TABLE (
    body_id UUID,
    body_name TEXT,
    position_x_km REAL,
    position_y_km REAL,
    position_z_km REAL,
    velocity_x_kms REAL,
    velocity_y_kms REAL,
    velocity_z_kms REAL,
    confidence_score REAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        ss.celestial_body_id,
        cb.name,
        ss.position_x_km,
        ss.position_y_km,
        ss.position_z_km,
        ss.velocity_x_kms,
        ss.velocity_y_kms,
        ss.velocity_z_kms,
        ss.confidence_score
    FROM simulation_state ss
    JOIN celestial_bodies cb ON ss.celestial_body_id = cb.id
    WHERE ss.simulation_time <= target_time
    AND ss.simulation_time = (
        SELECT MAX(simulation_time) 
        FROM simulation_state ss2 
        WHERE ss2.celestial_body_id = ss.celestial_body_id 
        AND ss2.simulation_time <= target_time
    )
    ORDER BY cb.name;
END;
$$ LANGUAGE plpgsql;

-- Grant permissions (if using separate user)
-- GRANT USAGE ON SCHEMA public TO sannetic_user;
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO sannetic_user;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO sannetic_user;
-- GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO sannetic_user;

-- Set default privileges for future objects
-- ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO sannetic_user;
-- ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO sannetic_user;
-- ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT EXECUTE ON FUNCTIONS TO sannetic_user; 