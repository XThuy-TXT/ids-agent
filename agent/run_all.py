"""Chạy agent trên tất cả sự cố, chấm với đáp án và ghi kết quả vào SQLite.

Cách chạy (từ thư mục gốc ids-agent/, venv đang bật):
    python app/load_incidents.py     # nạp sự cố vào CSDL, chỉ cần chạy một lần
    python agent/run_all.py
"""
import json
import sqlite3
import time
from pathlib import Path

import groq

from analyze_one import call_llm, validate

BASE_DIR = Path(__file__).resolve().parent.parent
INCIDENTS_PATH = BASE_DIR / "data" / "sample" / "incidents_fake.json"
ANSWERS_PATH = BASE_DIR / "data" / "sample" / "answers.json"
DB_PATH = BASE_DIR / "app" / "ids.db"
REPORT_PATH = BASE_DIR / "docs" / "run_all_result.md"


def analyze(incident):
    """Phân tích một sự cố. Trả về (kết quả, lỗi): đúng một trong hai là None."""
    try:
        raw = call_llm(incident)
    except groq.APIError as e:
        return None, f"Groq từ chối: {e}"
    try:
        result = json.loads(raw)
    except json.JSONDecodeError as e:
        return None, f"JSON sai cú pháp: {e}"
    if not isinstance(result, dict):
        return None, "JSON không phải một đối tượng"
    errors = validate(result, incident["incident_id"])
    if errors:
        return None, "; ".join(errors)
    return result, None


def save_analysis(conn, incident_id, result):
    """Ghi kết quả hợp lệ vào bảng analyses. Sự cố lỗi thì xóa kết quả cũ."""
    if result is None:
        conn.execute("DELETE FROM analyses WHERE incident_id = ?", (incident_id,))
    else:
        conn.execute(
            """INSERT OR REPLACE INTO analyses
               (incident_id, attack_type, severity, attack_technique, explanation, mitigation)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (incident_id, result["attack_type"], result["severity"],
             result["attack_technique"], result["explanation"], result["mitigation"]),
        )
    conn.commit()


def same_technique(got, expected):
    """So mã MITRE theo kỹ thuật gốc: T1110.001 và T1110 coi là khớp."""
    return got.split(".")[0] == expected.split(".")[0]


def main():
    if not DB_PATH.exists():
        raise SystemExit(f"Chưa có {DB_PATH}. Chạy `python app/load_incidents.py` trước.")
    incidents = json.loads(INCIDENTS_PATH.read_text(encoding="utf-8"))
    answers = {a["incident_id"]: a for a in json.loads(ANSWERS_PATH.read_text(encoding="utf-8"))}
    conn = sqlite3.connect(DB_PATH)

    rows = []
    type_ok = tech_ok = tech_total = failed = 0
    for incident in incidents:
        iid = incident["incident_id"]
        ans = answers[iid]
        print(f"Đang phân tích sự cố {iid}...")
        result, error = analyze(incident)
        save_analysis(conn, iid, result)

        if error:
            failed += 1
            got_type, got_tech, type_mark, tech_mark = "-", "-", "lỗi", "lỗi"
        else:
            got_type, got_tech = result["attack_type"], result["attack_technique"]
            type_mark = "đúng" if got_type == ans["attack_type"] else "sai"
            if ans["attack_technique"] is None:
                tech_mark = "không chấm"
            else:
                tech_mark = "đúng" if same_technique(got_tech, ans["attack_technique"]) else "sai"
        type_ok += type_mark == "đúng"
        if ans["attack_technique"] is not None:
            tech_total += 1
            tech_ok += tech_mark == "đúng"

        note = "mơ hồ" if ans["ambiguous"] else ""
        if error:
            note = (note + "; " if note else "") + error
        rows.append(f"| {iid} | {ans['attack_type']} | {got_type} | {type_mark} "
                    f"| {ans['attack_technique'] or '-'} | {got_tech} | {tech_mark} | {note} |")
        time.sleep(1)  # nghỉ 1 giây giữa các lần gọi để không chạm giới hạn của Groq

    conn.close()
    lines = [
        "| Sự cố | Đáp án | Agent | Loại | Mã đáp án | Mã agent | Mã MITRE | Ghi chú |",
        "|---|---|---|---|---|---|---|---|",
        *rows,
        "",
        f"- Loại tấn công đúng: {type_ok}/{len(incidents)} (sự cố lỗi tính là sai)",
        f"- Mã MITRE đúng: {tech_ok}/{tech_total} (bỏ qua sự cố không có mã đáp án)",
        f"- Số sự cố lỗi: {failed}",
    ]
    report = "\n".join(lines)
    print()
    print(report)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(report + "\n", encoding="utf-8")
    print(f"\nĐã lưu bảng kết quả vào {REPORT_PATH}")


if __name__ == "__main__":
    main()
