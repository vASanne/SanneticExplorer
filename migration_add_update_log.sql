-- Migration: Add UpdateLog table
-- Date: 2024-01-XX
-- Description: Add table for tracking update script executions and their results

-- Create UpdateLog table
CREATE TABLE IF NOT EXISTS update_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    script_name VARCHAR(255) NOT NULL,
    status VARCHAR(50) NOT NULL,
    message TEXT,
    duration_sec FLOAT,
    log_level VARCHAR(20),
    source_file VARCHAR(255),
    
    -- Constraints
    CONSTRAINT valid_update_status CHECK (status IN ('success', 'error', 'warning', 'info')),
    CONSTRAINT non_negative_duration CHECK (duration_sec IS NULL OR duration_sec >= 0)
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_update_log_timestamp ON update_logs(timestamp);
CREATE INDEX IF NOT EXISTS idx_update_log_script_status ON update_logs(script_name, status);
CREATE INDEX IF NOT EXISTS idx_update_log_script_name ON update_logs(script_name);

-- Add comments
COMMENT ON TABLE update_logs IS 'Log of update script executions and their results';
COMMENT ON COLUMN update_logs.id IS 'Primary key UUID';
COMMENT ON COLUMN update_logs.timestamp IS 'When the log entry was created';
COMMENT ON COLUMN update_logs.script_name IS 'Name of the script that generated this log entry';
COMMENT ON COLUMN update_logs.status IS 'Status of the operation: success, error, warning, info';
COMMENT ON COLUMN update_logs.message IS 'Detailed message or error description';
COMMENT ON COLUMN update_logs.duration_sec IS 'Duration of the operation in seconds';
COMMENT ON COLUMN update_logs.log_level IS 'Log level: DEBUG, INFO, WARNING, ERROR';
COMMENT ON COLUMN update_logs.source_file IS 'Source log file this entry came from'; 