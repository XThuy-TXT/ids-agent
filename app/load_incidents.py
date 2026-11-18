import json
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "app" / "ids.db"
INCIDENTS_PATH = BASE_DIR / "data" / "sample" / "incidents_fake.json"
SCHEMA_PATH = BASE_DIR / "app" / "schema.sql"


def init_db(conn: sqlite3.Connection) -> None:
    conn.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))


def load_incidents(conn: sqlite3.Connection, path: Path) -> int:
    incidents = json.loads(path.read_text(encoding="utf-8"))
    rows = [
        (
            inc["incident_id"],
            inc["src_ip"],
            inc["dst_ip"],
            inc["start"],
            inc["end"],
            inc["alert_count"],
            json.dumps(inc["signatures"], ensure_ascii=False),
            json.dumps(inc["dest_ports"]),
        )
        for inc in incidents
    ]
    conn.executemany(
        """INSERT OR REPLACE INTO incidents
           (incident_id, src_ip, dst_ip, start, end, alert_count, signatures, dest_ports)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        rows,
    )
    conn.commit()
    return len(rows)


def main() -> None:
    if not INCIDENTS_PATH.exists():
        raise FileNotFoundError(f"Khong tim thay: {INCIDENTS_PATH}")
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    try:
        init_db(conn)
        n = load_incidents(conn, INCIDENTS_PATH)
        print(f"Da nap {n} su co vao {DB_PATH}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()