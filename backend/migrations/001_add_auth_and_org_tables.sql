-- ================================
-- Migration: Add authentication and organization tables
-- ================================

-- Organizations table
CREATE TABLE IF NOT EXISTS organization (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  name VARCHAR(255) NOT NULL,
  email_domain VARCHAR(255) NOT NULL UNIQUE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  INDEX idx_email_domain (email_domain)
);

-- Users table
CREATE TABLE IF NOT EXISTS user (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  organization_id BIGINT NOT NULL,
  email VARCHAR(255) NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  full_name VARCHAR(255),
  is_verified BOOLEAN DEFAULT FALSE,
  verification_token VARCHAR(255),
  verification_token_expires TIMESTAMP,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (organization_id) REFERENCES organization(id) ON DELETE CASCADE,
  INDEX idx_email (email),
  INDEX idx_verification_token (verification_token)
);

-- Sessions table
CREATE TABLE IF NOT EXISTS session (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  user_id BIGINT NOT NULL,
  token VARCHAR(512) NOT NULL UNIQUE,
  expires_at TIMESTAMP NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  ip_address VARCHAR(45),
  user_agent TEXT,
  FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE,
  INDEX idx_token (token),
  INDEX idx_user_id (user_id),
  INDEX idx_expires_at (expires_at)
);

-- Ethics agreements table
CREATE TABLE IF NOT EXISTS ethics_agreement (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  version VARCHAR(50) NOT NULL UNIQUE,
  content LONGTEXT NOT NULL,
  effective_date TIMESTAMP NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_version (version)
);

-- Ethics acceptances table
CREATE TABLE IF NOT EXISTS ethics_acceptance (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  user_id BIGINT NOT NULL,
  agreement_version VARCHAR(50) NOT NULL,
  accepted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  ip_address VARCHAR(45),
  FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE,
  INDEX idx_user_id (user_id),
  INDEX idx_agreement_version (agreement_version)
);

-- Domains table
CREATE TABLE IF NOT EXISTS domain (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  organization_id BIGINT NOT NULL,
  domain_name VARCHAR(255) NOT NULL,
  verification_token VARCHAR(255) NOT NULL,
  is_verified BOOLEAN DEFAULT FALSE,
  verification_method VARCHAR(50),
  verified_at TIMESTAMP NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (organization_id) REFERENCES organization(id) ON DELETE CASCADE,
  UNIQUE KEY unique_org_domain (organization_id, domain_name),
  INDEX idx_domain_name (domain_name),
  INDEX idx_verification_token (verification_token)
);

-- Websites table
CREATE TABLE IF NOT EXISTS website (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  user_id BIGINT NOT NULL,
  domain_id BIGINT NOT NULL,
  entry_url TEXT NOT NULL,
  name VARCHAR(255),
  status VARCHAR(50) DEFAULT 'registered',
  last_remediation_at TIMESTAMP NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE,
  FOREIGN KEY (domain_id) REFERENCES domain(id) ON DELETE CASCADE,
  INDEX idx_user_id (user_id),
  INDEX idx_domain_id (domain_id),
  INDEX idx_status (status)
);

-- Audit trail table
CREATE TABLE IF NOT EXISTS audit_log (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  event_type VARCHAR(100) NOT NULL,
  user_id BIGINT,
  organization_id BIGINT,
  details JSON,
  ip_address VARCHAR(45),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE SET NULL,
  FOREIGN KEY (organization_id) REFERENCES organization(id) ON DELETE SET NULL,
  INDEX idx_event_type (event_type),
  INDEX idx_user_id (user_id),
  INDEX idx_organization_id (organization_id),
  INDEX idx_created_at (created_at)
);

-- Update existing page table to add website_id foreign key
-- Check if column exists first to make migration idempotent
SET @column_exists = (
  SELECT COUNT(*) 
  FROM INFORMATION_SCHEMA.COLUMNS 
  WHERE TABLE_SCHEMA = DATABASE() 
    AND TABLE_NAME = 'page' 
    AND COLUMN_NAME = 'website_id'
);

SET @sql = IF(
  @column_exists = 0,
  'ALTER TABLE page ADD COLUMN website_id BIGINT NULL',
  'SELECT "Column website_id already exists" AS message'
);

PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Add foreign key constraint if it doesn't exist
SET @fk_exists = (
  SELECT COUNT(*)
  FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
  WHERE TABLE_SCHEMA = DATABASE()
    AND TABLE_NAME = 'page'
    AND CONSTRAINT_NAME = 'page_ibfk_1'
);

SET @sql = IF(
  @fk_exists = 0 AND @column_exists = 0,
  'ALTER TABLE page ADD FOREIGN KEY (website_id) REFERENCES website(id) ON DELETE CASCADE',
  'SELECT "Foreign key already exists or column was not added" AS message'
);

PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Add index on website_id if it doesn't exist
SET @idx_exists = (
  SELECT COUNT(*)
  FROM INFORMATION_SCHEMA.STATISTICS
  WHERE TABLE_SCHEMA = DATABASE()
    AND TABLE_NAME = 'page'
    AND INDEX_NAME = 'idx_website_id'
);

SET @sql = IF(
  @idx_exists = 0 AND @column_exists = 0,
  'ALTER TABLE page ADD INDEX idx_website_id (website_id)',
  'SELECT "Index idx_website_id already exists or column was not added" AS message'
);

PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;
