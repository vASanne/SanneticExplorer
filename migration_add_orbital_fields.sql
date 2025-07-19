-- Migration: Add orbital fields to celestial_bodies table
-- Date: 2024-01-17
-- Description: Add mean_distance_au and orbital_speed_kms fields for frontend compatibility

-- Add the missing orbital fields
ALTER TABLE celestial_bodies 
ADD COLUMN IF NOT EXISTS mean_distance_au FLOAT,
ADD COLUMN IF NOT EXISTS orbital_speed_kms FLOAT;

-- Add constraints for the new fields
ALTER TABLE celestial_bodies 
ADD CONSTRAINT IF NOT EXISTS positive_mean_distance 
CHECK (mean_distance_au IS NULL OR mean_distance_au >= 0);

ALTER TABLE celestial_bodies 
ADD CONSTRAINT IF NOT EXISTS positive_orbital_speed 
CHECK (orbital_speed_kms IS NULL OR orbital_speed_kms >= 0);

-- Add indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_celestial_bodies_mean_distance 
ON celestial_bodies(mean_distance_au);

CREATE INDEX IF NOT EXISTS idx_celestial_bodies_orbital_speed 
ON celestial_bodies(orbital_speed_kms);

-- Update existing data with reasonable defaults if needed
-- This is optional and can be customized based on your data

-- Example: Set mean_distance_au for planets based on their type
-- UPDATE celestial_bodies 
-- SET mean_distance_au = 1.0 
-- WHERE type = 'planet' AND mean_distance_au IS NULL;

-- Example: Set orbital_speed_kms for planets based on their distance
-- UPDATE celestial_bodies 
-- SET orbital_speed_kms = 29.78 
-- WHERE type = 'planet' AND orbital_speed_kms IS NULL;

-- Log the migration
INSERT INTO migration_log (migration_name, applied_at, description) 
VALUES (
    'add_orbital_fields_20240117', 
    NOW(), 
    'Added mean_distance_au and orbital_speed_kms fields to celestial_bodies table'
) ON CONFLICT DO NOTHING; 