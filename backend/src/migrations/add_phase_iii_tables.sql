-- Phase III Database Migration: Conversations & Messages Tables
-- Created: 2026-01-25
-- Purpose: Add conversational todo management support (spec-7-persistence-memory.md)
-- Constitutional Compliance: Principle VI (Phase-II Protection) - Additive schema only

-- ============================================================================
-- TABLE: conversations
-- ============================================================================
-- Purpose: Store metadata for user conversations
-- Constraints:
--   - One conversation per user (UNIQUE constraint on user_id)
--   - Cascade delete when user is removed
--
-- PostgreSQL Version (for Neon DB production):
-- CREATE TABLE conversations (
--     id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
--     user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
--     created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
--     updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
--     CONSTRAINT unique_user_conversation UNIQUE(user_id)
-- );
--
-- CREATE INDEX idx_conversations_user_id ON conversations(user_id);

-- SQLite Version (for development):
CREATE TABLE IF NOT EXISTS conversations (
    id CHAR(32) PRIMARY KEY,  -- UUID stored as 32-char hex string (SQLModel default)
    user_id CHAR(32) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_user_conversation UNIQUE(user_id)
);

CREATE INDEX IF NOT EXISTS idx_conversations_user_id ON conversations(user_id);


-- ============================================================================
-- TABLE: messages
-- ============================================================================
-- Purpose: Store individual messages in conversations (user inputs & agent responses)
-- Constraints:
--   - role must be 'user' or 'agent'
--   - content limited to 10,000 characters
--   - Cascade delete when conversation is removed
--   - Indexed for fast chronological retrieval
--
-- PostgreSQL Version (for Neon DB production):
-- CREATE TABLE messages (
--     id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
--     conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
--     role VARCHAR(10) NOT NULL CHECK (role IN ('user', 'agent')),
--     content TEXT NOT NULL CHECK (LENGTH(content) <= 10000),
--     created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
-- );
--
-- CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
-- CREATE INDEX idx_messages_created_at ON messages(conversation_id, created_at DESC);

-- SQLite Version (for development):
CREATE TABLE IF NOT EXISTS messages (
    id CHAR(32) PRIMARY KEY,  -- UUID stored as 32-char hex string (SQLModel default)
    conversation_id CHAR(32) NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    role VARCHAR(5) NOT NULL CHECK (role IN ('user', 'agent')),
    content VARCHAR NOT NULL,  -- SQLite VARCHAR is unlimited, enforce max length in application
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX IF NOT EXISTS idx_messages_created_at ON messages(conversation_id, created_at DESC);


-- ============================================================================
-- Migration Verification Queries
-- ============================================================================

-- Verify tables exist:
-- SELECT name FROM sqlite_master WHERE type='table' AND name IN ('conversations', 'messages');

-- Verify indexes exist:
-- SELECT name FROM sqlite_master WHERE type='index' AND tbl_name IN ('conversations', 'messages');

-- Verify relationships:
-- PRAGMA foreign_key_list(conversations);
-- PRAGMA foreign_key_list(messages);


-- ============================================================================
-- Rollback Plan (if needed)
-- ============================================================================

-- DROP INDEX IF EXISTS idx_messages_created_at;
-- DROP INDEX IF EXISTS idx_messages_conversation_id;
-- DROP TABLE IF EXISTS messages;
-- DROP INDEX IF EXISTS idx_conversations_user_id;
-- DROP TABLE IF EXISTS conversations;


-- ============================================================================
-- Phase-II Protection Validation
-- ============================================================================

-- Verify existing Phase-II tables remain unchanged:
-- PRAGMA table_info(users);
-- PRAGMA table_info(tasks);
-- PRAGMA table_info(priorities);
-- PRAGMA table_info(tags);
-- PRAGMA table_info(task_tags);

-- Expected: No schema changes to Phase-II tables
