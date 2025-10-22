-- Migration: create base portfolio tables
CREATE TABLE IF NOT EXISTS portfolio_entry (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    summary TEXT NOT NULL,
    status TEXT NOT NULL,
    tags TEXT[] DEFAULT ARRAY[]::TEXT[],
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS artifact (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entry_id TEXT REFERENCES portfolio_entry(id) ON DELETE CASCADE,
    type TEXT NOT NULL,
    title TEXT NOT NULL,
    uri TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
