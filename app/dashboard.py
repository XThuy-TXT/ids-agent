import json
import sqlite3
from pathlib import Path

import pandas as pd
import streamlit as st

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "app" / "ids.db"

st.set_page_config(page_title="IDS/IPS Log Agent", layout="wide")
st.title("IDS/IPS Log Analysis Agent")

if not DB_PATH.exists():
    st.error(f"Khong tim thay CSDL {DB_PATH}. Chay `python app/load_incidents.py` truoc.")
    st.stop()

conn = sqlite3.connect(DB_PATH, check_same_thread=False)
df = pd.read_sql_query(
    """
    SELECT i.incident_id, i.src_ip, i.dst_ip, i.start, i.end, i.alert_count,
           i.signatures, i.dest_ports,
           a.attack_type, a.severity, a.attack_technique
    FROM incidents i
    LEFT JOIN analyses a ON a.incident_id = i.incident_id
    ORDER BY i.incident_id
    """,
    conn,
)
conn.close()

col1, col2 = st.columns(2)
with col1:
    sev_filter = st.multiselect(
        "Muc do", sorted([s for s in df["severity"].dropna().unique().tolist()])
    )
with col2:
    atk_filter = st.multiselect(
        "Loai tan cong", sorted([s for s in df["attack_type"].dropna().unique().tolist()])
    )

view = df.copy()
if sev_filter:
    view = view[view["severity"].isin(sev_filter)]
if atk_filter:
    view = view[view["attack_type"].isin(atk_filter)]

st.subheader(f"Danh sach su co ({len(view)})")
st.dataframe(view, use_container_width=True)

st.subheader("Chi tiet mot su co")
if not view.empty:
    chosen = st.selectbox("Chon incident_id", view["incident_id"].tolist())
    row = view[view["incident_id"] == chosen].iloc[0]
    st.json({
        "incident": {
            "incident_id": int(row["incident_id"]),
            "src_ip": row["src_ip"],
            "dst_ip": row["dst_ip"],
            "start": row["start"],
            "end": row["end"],
            "alert_count": int(row["alert_count"]),
            "signatures": json.loads(row["signatures"]),
            "dest_ports": json.loads(row["dest_ports"]),
        },
        "analysis": {
            "attack_type": row["attack_type"],
            "severity": row["severity"],
            "attack_technique": row["attack_technique"],
        },
    })