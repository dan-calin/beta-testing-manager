-- ============================================================
--  Beta Testing Manager — Supabase Schema
--  Paste this into: Supabase Dashboard → SQL Editor → New Query
-- ============================================================

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ------------------------------------------------------------
--  users
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.users (
    id          UUID        PRIMARY KEY DEFAULT uuid_generate_v4(),
    username    TEXT        NOT NULL UNIQUE,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ------------------------------------------------------------
--  sessions
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.sessions (
    id           UUID        PRIMARY KEY,
    user_id      UUID        NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    session_name TEXT        NOT NULL,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_sessions_user_id
    ON public.sessions(user_id);

-- Auto-bump updated_at on every UPDATE
CREATE OR REPLACE FUNCTION public.set_updated_at()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_sessions_updated_at ON public.sessions;
CREATE TRIGGER trg_sessions_updated_at
    BEFORE UPDATE ON public.sessions
    FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();

-- ------------------------------------------------------------
--  test_items
--  start_timestamp / stop_timestamp are TEXT so they can hold
--  either an OBS timecode ("00:12:34.500") or a wall-clock
--  ISO-8601 datetime ("2024-01-15T10:30:00").
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.test_items (
    id              UUID        PRIMARY KEY,
    session_id      UUID        NOT NULL REFERENCES public.sessions(id) ON DELETE CASCADE,
    system_name     TEXT        NOT NULL,
    status          TEXT        NOT NULL DEFAULT 'Pending'
                                CHECK (status IN ('Pending','In Progress','Pass','Fail')),
    start_timestamp TEXT,
    stop_timestamp  TEXT,
    notes           TEXT        NOT NULL DEFAULT '',
    sort_order      INTEGER     NOT NULL DEFAULT 0,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

ALTER TABLE public.test_items
    ADD COLUMN IF NOT EXISTS sort_order INTEGER NOT NULL DEFAULT 0;

CREATE INDEX IF NOT EXISTS idx_test_items_session_id
    ON public.test_items(session_id);

CREATE INDEX IF NOT EXISTS idx_test_items_session_sort_order
    ON public.test_items(session_id, sort_order);

-- ------------------------------------------------------------
--  Row Level Security
--  Using permissive anon-key policies for a desktop app.
--  Replace with auth.uid() policies if you need per-user isolation.
-- ------------------------------------------------------------
ALTER TABLE public.users      ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.sessions   ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.test_items ENABLE ROW LEVEL SECURITY;

-- Drop before re-creating to make the script idempotent
DROP POLICY IF EXISTS "anon_all_users"      ON public.users;
DROP POLICY IF EXISTS "anon_all_sessions"   ON public.sessions;
DROP POLICY IF EXISTS "anon_all_test_items" ON public.test_items;

CREATE POLICY "anon_all_users"
    ON public.users FOR ALL USING (true) WITH CHECK (true);

CREATE POLICY "anon_all_sessions"
    ON public.sessions FOR ALL USING (true) WITH CHECK (true);

CREATE POLICY "anon_all_test_items"
    ON public.test_items FOR ALL USING (true) WITH CHECK (true);
