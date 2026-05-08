-- ZipIt Database Initialization
-- This script sets up the initial database structure and data

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);
CREATE INDEX IF NOT EXISTS idx_ml_models_owner ON ml_models(owner_id);
CREATE INDEX IF NOT EXISTS idx_ml_models_status ON ml_models(status);
CREATE INDEX IF NOT EXISTS idx_projects_owner ON projects(owner_id);
CREATE INDEX IF NOT EXISTS idx_user_sessions_token ON user_sessions(session_token);
CREATE INDEX IF NOT EXISTS idx_user_sessions_user ON user_sessions(user_id);

-- Insert default role configurations
INSERT INTO role_configs (role_name, max_models, max_storage_gb, max_compute_hours) VALUES
('Student', 3, 5.0, 10),
('Developer', 10, 25.0, 50),
('Researcher', 25, 100.0, 200),
('Enterprise', 100, 500.0, 1000),
('Admin', 999, 1000.0, 9999)
ON CONFLICT (role_name) DO NOTHING;

-- Create role configurations table if not exists
CREATE TABLE IF NOT EXISTS role_configs (
    id SERIAL PRIMARY KEY,
    role_name VARCHAR(20) UNIQUE NOT NULL,
    max_models INTEGER DEFAULT 3,
    max_storage_gb FLOAT DEFAULT 5.0,
    max_compute_hours INTEGER DEFAULT 10,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);