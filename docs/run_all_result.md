| Sự cố | Đáp án | Agent | Loại | Mã đáp án | Mã agent | Mã MITRE | Ghi chú |
|---|---|---|---|---|---|---|---|
| 1 | port_scan | port_scan | đúng | T1046 | T1046 | đúng |  |
| 2 | port_scan | port_scan | đúng | T1046 | T1046 | đúng | mơ hồ |
| 3 | dos | dos | đúng | T1498 | T1496 | sai |  |
| 4 | web_attack | web_attack | đúng | T1190 | T1059 | sai |  |
| 5 | brute_force | brute_force | đúng | T1110 | T1110 | đúng |  |
| 6 | other | web_attack | sai | - | T1071.001 | không chấm | mơ hồ |
| 7 | port_scan | port_scan | đúng | T1046 | T1046 | đúng | mơ hồ |
| 8 | brute_force | brute_force | đúng | T1110 | T1110.001 | đúng |  |
| 9 | web_attack | web_attack | đúng | T1190 | T1059 | sai |  |

- Loại tấn công đúng: 8/9 (sự cố lỗi tính là sai)
- Mã MITRE đúng: 5/8 (bỏ qua sự cố không có mã đáp án)
- Số sự cố lỗi: 0
