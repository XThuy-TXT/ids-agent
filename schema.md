# Định dạng dữ liệu

## 1. Sự cố (Incident) – pipeline tạo ra, agent đọc vào

| Trường | Kiểu | Mô tả |
|---|---|---|
| incident_id | int | ID duy nhất |
| src_ip | string | IP nguồn |
| dst_ip | string | IP đích |
| start | ISO8601 | Thời điểm cảnh báo đầu |
| end | ISO8601 | Thời điểm cảnh báo cuối |
| alert_count | int | Số cảnh báo trong cụm |
| signatures | string[] | Danh sách tên luật |
| dest_ports | int[] | Các cổng đích bị nhắm |

Ví dụ:
{
  "incident_id": 12,
  "src_ip": "192.168.56.10",
  "dst_ip": "192.168.56.20",
  "start": "2026-11-20T09:01:00",
  "end": "2026-11-20T09:03:30",
  "alert_count": 340,
  "signatures": ["ET SCAN Nmap Scripting Engine"],
  "dest_ports": [22, 80, 443]
}

## 2. Kết quả agent (Analysis) – agent ghi ra, CSDL/dashboard đọc vào

| Trường | Kiểu | Mô tả |
|---|---|---|
| incident_id | int | Khóa ngoại tới incident |
| attack_type | string | port_scan, brute_force, ... |
| severity | string | low / medium / high / critical |
| attack_technique | string | Mã MITRE ATT&CK (vd T1046) |
| explanation | string | Giải thích |
| mitigation | string | Cách xử lý |

Ví dụ:
{
  "incident_id": 12,
  "attack_type": "port_scan",
  "severity": "medium",
  "attack_technique": "T1046",
  "explanation": "...",
  "mitigation": "..."
}

## Quy ước
- Timestamp ISO 8601, không timezone.
- severity: low / medium / high / critical.
- attack_technique theo MITRE ATT&CK.