-- ================================
-- Migration: Rename website to webpage and allow multiple webpages per domain
-- ================================

-- Drop the foreign key constraint from page table
ALTER TABLE page DROP FOREIGN KEY page_ibfk_1;

-- Rename website table to webpage
RENAME TABLE website TO webpage;

-- Re-add the foreign key constraint with the new table name
ALTER TABLE page 
  ADD CONSTRAINT page_ibfk_1 
  FOREIGN KEY (website_id) REFERENCES webpage(id) ON DELETE CASCADE;

-- Note: We keep the column name as website_id in the page table for now
-- to minimize breaking changes. It will reference the webpage table.
-- In a future migration, we could rename website_id to webpage_id if desired.

-- The unique constraint limiting one website per organization has been removed
-- Organizations can now have multiple webpages per domain
