-- ZipIt Platform Database Initialization
-- Creates all necessary tables and indexes

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    role VARCHAR(20) DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    is_active BOOLEAN DEFAULT true
);

-- Models table
CREATE TABLE IF NOT EXISTS models (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    version VARCHAR(20) NOT NULL,
    user_id INTEGER REFERENCES users(id),
    algorithm VARCHAR(50),
    accuracy DECIMAL(5,4),
    status VARCHAR(20) DEFAULT 'training',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deployed_at TIMESTAMP,
    model_path TEXT,
    metadata JSONB
);

-- Experiments table
CREATE TABLE IF NOT EXISTS experiments (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    user_id INTEGER REFERENCES users(id),
    model_id INTEGER REFERENCES models(id),
    parameters JSONB,
    metrics JSONB,
    status VARCHAR(20) DEFAULT 'running',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);

-- Deployments table
CREATE TABLE IF NOT EXISTS deployments (
    id SERIAL PRIMARY KEY,
    model_id INTEGER REFERENCES models(id),
    endpoint_url VARCHAR(255),
    status VARCHAR(20) DEFAULT 'deploying',
    instances INTEGER DEFAULT 1,
    cpu_usage DECIMAL(5,2),
    memory_usage DECIMAL(5,2),
    requests_per_minute INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Monitoring data table
CREATE TABLE IF NOT EXISTS monitoring_data (
    id SERIAL PRIMARY KEY,
    model_id INTEGER REFERENCES models(id),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    accuracy DECIMAL(5,4),
    latency_ms INTEGER,
    drift_score DECIMAL(5,4),
    prediction_count INTEGER,
    error_rate DECIMAL(5,4)
);

-- Audit logs table
CREATE TABLE IF NOT EXISTS audit_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    action VARCHAR(50) NOT NULL,
    resource_type VARCHAR(50),
    resource_id INTEGER,
    ip_address INET,
    user_agent TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    details JSONB
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_models_user_id ON models(user_id);
CREATE INDEX IF NOT EXISTS idx_experiments_model_id ON experiments(model_id);
CREATE INDEX IF NOT EXISTS idx_deployments_model_id ON deployments(model_id);
CREATE INDEX IF NOT EXISTS idx_monitoring_timestamp ON monitoring_data(timestamp);
CREATE INDEX IF NOT EXISTS idx_audit_logs_timestamp ON audit_logs(timestamp);

-- Insert demo data
INSERT INTO users (username, email, password_hash, full_name, role) VALUES
('demo_user', 'demo@zipit.com', '$2b$12$gSvqqUPvlXRJsxTU/ohtAuYHyqSqHX6aDdP0dU4CcT/h7GrHVG.vS', 'Demo User', 'user'),
('admin', 'admin@zipit.com', '$2b$12$gSvqqUPvlXRJsxTU/ohtAuYHyqSqHX6aDdP0dU4CcT/h7GrHVG.vS', 'Admin User', 'admin')
ON CONFLICT (username) DO NOTHING;

-- Create MLflow database
CREATE DATABASE mlflow;
GRANT ALL PRIVILEGES ON DATABASE mlflow TO postgres;