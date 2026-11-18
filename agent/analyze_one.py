"""Phân tích một sự cố bằng LLM và kiểm tra kết quả trả về.

Cách chạy (từ thư mục gốc ids-agent/):
    python agent/analyze_one.py data/sample/incidents_fake.json 4
"""
import json
import re
import sys
import os

from dotenv import load_dotenv
from groq import Groq

MODEL = "openai/gpt-oss-20b"

# Chỉnh danh sách nhãn ở đây khi nhóm chốt.
ATTACK_TYPES = ["port_scan", "brute_force", "web_attack", "dos", "other"]
SEVERITIES = ["low", "medium", "high", "critical"]
REQUIRED_FIELDS = [
    "incident_id", "attack_type", "severity",
    "attack_technique", "explanation", "mitigation",
]

SYSTEM_PROMPT = f"""Bạn là chuyên viên an ninh mạng. Bạn nhận một sự cố ở dạng JSON, \
gồm các cảnh báo của Suricata đã được gom lại.
Hãy phân tích và chỉ trả lời bằng MỘT đối tượng JSON, không viết gì ngoài JSON, \
gồm đúng các trường sau:
- incident_id: số nguyên, giữ nguyên như đầu vào
- attack_type: một trong {json.dumps(ATTACK_TYPES)}
- severity: một trong {json.dumps(SEVERITIES)}
- attack_technique: mã kỹ thuật MITRE ATT&CK, ví dụ "T1046"
- explanation: giải thích ngắn bằng tiếng Việt vì sao bạn kết luận như vậy
- mitigation: cách xử lý bằng tiếng Việt
"""


def load_incident(path, incident_id):
    """Đọc file danh sách sự cố, trả về sự cố có incident_id cần tìm."""
    with open(path, encoding="utf-8") as f:
        incidents = json.load(f)
    for incident in incidents:
        if incident["incident_id"] == incident_id:
            return incident
    raise SystemExit(f"Không tìm thấy sự cố {incident_id} trong {path}")


def call_llm(incident):
    """Gửi sự cố cho Groq, trả về chuỗi chữ model trả lời."""
    load_dotenv()
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    resp = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": json.dumps(incident, ensure_ascii=False)},
        ],
        response_format={"type": "json_object"},
        temperature=0,
	reasoning_effort="low",
        max_completion_tokens=2000,
    )
    return resp.choices[0].message.content or ""


def validate(result, incident_id):
    """Kiểm tra tầng nội dung. Trả về danh sách lỗi (rỗng nghĩa là hợp lệ)."""
    errors = []

    # 1. Có đủ trường không
    for field in REQUIRED_FIELDS:
        if field not in result:
            errors.append(f"Thiếu trường: {field}")
    if errors:
        return errors

    # 2. Từng trường có đúng kiểu và đúng giá trị không
    got_id = result["incident_id"]
    if not isinstance(got_id, int) or isinstance(got_id, bool) or got_id != incident_id:
        errors.append(f"incident_id sai: nhận {got_id!r}, cần {incident_id}")
    if result["attack_type"] not in ATTACK_TYPES:
        errors.append(f"attack_type không hợp lệ: {result['attack_type']!r}")
    if result["severity"] not in SEVERITIES:
        errors.append(f"severity không hợp lệ: {result['severity']!r}")
    technique = result["attack_technique"]
    if not isinstance(technique, str) or not re.fullmatch(r"T\d{4}(\.\d{3})?", technique):
        errors.append(f"attack_technique không đúng dạng Txxxx: {technique!r}")
    for field in ("explanation", "mitigation"):
        value = result[field]
        if not isinstance(value, str) or not value.strip():
            errors.append(f"{field} rỗng hoặc không phải chữ")
    return errors


def main():
    if len(sys.argv) != 3:
        raise SystemExit("Cách dùng: python agent/analyze_one.py <file_su_co.json> <incident_id>")
    path, incident_id = sys.argv[1], int(sys.argv[2])

    incident = load_incident(path, incident_id)
    raw = call_llm(incident)

    # Tầng cú pháp: có đọc được thành JSON không
    try:
        result = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"LỖI cú pháp JSON: {e}")
        print("Model trả về:", raw)
        sys.exit(1)

    # Tầng nội dung
    errors = validate(result, incident_id)
    if errors:
        print(f"LỖI nội dung (sự cố {incident_id}):")
        for err in errors:
            print(" -", err)
        print("Model trả về:", raw)
        sys.exit(1)

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
