-- Police Reports Database Schema
CREATE TABLE IF NOT EXISTS reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT NOT NULL,
    report_date TEXT,
    report_type TEXT, -- 'General' or 'Security'
    raw_hash TEXT UNIQUE,
    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS sections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    report_id INTEGER,
    category_id INTEGER,
    title TEXT,
    content_sinhala TEXT,
    FOREIGN KEY (report_id) REFERENCES reports(id)
);

CREATE TABLE IF NOT EXISTS incidents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    section_id INTEGER,
    station TEXT,
    province TEXT,
    translation_english TEXT,
    reference_code TEXT,
    confidence_score REAL,
    consensus_status TEXT, -- 'OllamaOnly', 'Validated', 'Mismatch'
    FOREIGN KEY (section_id) REFERENCES sections(id)
);

CREATE TABLE IF NOT EXISTS ai_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    incident_id INTEGER,
    engine TEXT,
    prompt TEXT,
    response TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (incident_id) REFERENCES incidents(id)
);

CREATE TABLE IF NOT EXISTS security_translations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    incident_date TEXT,
    station TEXT,
    original_sinhala TEXT,
    translation_english TEXT,
    confidence REAL,
    engine_used TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS general_translations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    incident_date TEXT,
    station TEXT,
    original_sinhala TEXT,
    translation_english TEXT,
    confidence REAL,
    engine_used TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS recent_files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT NOT NULL,
    filepath TEXT NOT NULL UNIQUE,
    file_type TEXT, -- 'PDF' or 'Word' or 'HTML'
    report_category TEXT, -- 'General' or 'Security'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
