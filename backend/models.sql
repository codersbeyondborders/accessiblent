-- ================================
-- Drop old tables if they exist
-- (make sure to drop in FK order)
-- ================================
DROP TABLE IF EXISTS issue;
DROP TABLE IF EXISTS chunk;
DROP TABLE IF EXISTS page;

-- ================================
-- PAGE table
-- ================================
CREATE TABLE page (
  id          BIGINT PRIMARY KEY AUTO_INCREMENT,
  url         TEXT,
  domain      VARCHAR(255),
  raw_html    LONGTEXT,
  fixed_html  LONGTEXT,
  status      VARCHAR(32),
  created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ================================
-- CHUNK table
-- Stores extracted segments with embeddings
-- ================================
CREATE TABLE chunk (
  id          BIGINT PRIMARY KEY AUTO_INCREMENT,
  page_id     BIGINT NOT NULL,
  path        VARCHAR(1024),
  role        VARCHAR(64),
  text        LONGTEXT,
  attrs       JSON,
  embedding   VECTOR(1536) NULL,
  created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_chunk_page (page_id),
  FOREIGN KEY (page_id) REFERENCES page(id) ON DELETE CASCADE
);

-- Add vector index (HNSW) on the embedding column
ALTER TABLE chunk
  ADD VECTOR INDEX idx_chunk_embedding (embedding) USING HNSW;

-- ================================
-- ISSUE table
-- Stores accessibility issues linked to chunks
-- ================================
CREATE TABLE issue (
  id          BIGINT PRIMARY KEY AUTO_INCREMENT,
  page_id     BIGINT NOT NULL,
  chunk_id    BIGINT,
  type        VARCHAR(64),
  severity    VARCHAR(16),
  details     JSON,
  created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (page_id) REFERENCES page(id) ON DELETE CASCADE,
  FOREIGN KEY (chunk_id) REFERENCES chunk(id) ON DELETE CASCADE,
  INDEX idx_issue_page (page_id),
  INDEX idx_issue_chunk (chunk_id)
);
