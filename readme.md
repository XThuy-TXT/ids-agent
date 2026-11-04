# IDS/IPS Log Analysis Agent

AI agent phân tích log Suricata, phát hiện và giải thích sự cố tấn công.

## Cấu trúc
- `lab/` – cấu hình Suricata, ghi chú lab
- `pipeline/` – đọc eve.json, gom sự cố
- `agent/` – gọi LLM, prompt
- `app/` – CSDL SQLite, dashboard Streamlit
- `data/sample/` – dữ liệu mẫu
- `docs/` – schema, ghi chép

## Thành viên
- TV1: lab, Suricata, pipeline
- TV2: LLM, agent
- TV3: CSDL, dashboard, tài liệu