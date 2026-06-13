CREATE TABLE IF NOT EXISTS sdlc_runs (
    id TEXT PRIMARY KEY,
    task_name TEXT NOT NULL,
    stage TEXT,
    agent TEXT,
    task_tags TEXT,
    started_at TEXT NOT NULL,
    ended_at TEXT,
    completion_status TEXT,
    duration_ms INTEGER,
    tokens_input INTEGER DEFAULT 0,
    tokens_output INTEGER DEFAULT 0,
    cost_usd REAL DEFAULT 0,
    tool_calls_total INTEGER DEFAULT 0,
    tool_calls_success INTEGER DEFAULT 0,
    tool_calls_failed INTEGER DEFAULT 0,
    tests_passed INTEGER DEFAULT 0,
    tests_failed INTEGER DEFAULT 0,
    doctor_exit_code INTEGER,
    hallucination_flag INTEGER DEFAULT 0,
    card TEXT,
    branch TEXT,
    session_id TEXT
);

CREATE TABLE IF NOT EXISTS sdlc_events (
    event_id TEXT PRIMARY KEY,
    schema_version TEXT NOT NULL DEFAULT '1.0',
    event_type TEXT NOT NULL,
    category TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    source TEXT NOT NULL,
    correlation_id TEXT,
    correlation_json TEXT,
    payload_json TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_sdlc_events_ts ON sdlc_events(timestamp);
CREATE INDEX IF NOT EXISTS idx_sdlc_events_category ON sdlc_events(category);
CREATE INDEX IF NOT EXISTS idx_sdlc_runs_stage ON sdlc_runs(stage);

CREATE VIEW IF NOT EXISTS sdlc_metrics AS
SELECT
    stage,
    agent,
    COUNT(*) AS run_count,
    SUM(CASE WHEN completion_status = 'completed' THEN 1 ELSE 0 END) AS completed_count,
    AVG(duration_ms) AS avg_duration_ms,
    SUM(cost_usd) AS total_cost_usd
FROM sdlc_runs
GROUP BY stage, agent;
