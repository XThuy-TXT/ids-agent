CREATE TABLE IF NOT EXISTS incidents (
    incident_id   INTEGER PRIMARY KEY,
    src_ip        TEXT NOT NULL,
    dst_ip        TEXT NOT NULL,
    start         TEXT NOT NULL,
    end           TEXT NOT NULL,
    alert_count   INTEGER NOT NULL,
    signatures    TEXT NOT NULL,
    dest_ports    TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS analyses (
    incident_id       INTEGER PRIMARY KEY,
    attack_type       TEXT,
    severity          TEXT,
    attack_technique  TEXT,
    explanation       TEXT,
    mitigation        TEXT,
    created_at        TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (incident_id) REFERENCES incidents(incident_id)
);