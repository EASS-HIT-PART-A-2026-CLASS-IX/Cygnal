import pandas as pd
import streamlit as st

from frontend.client import list_indicators, create_indicator, delete_indicator

st.set_page_config(page_title="Cygnal", page_icon="🛡️", layout="wide")
st.info("💡 Tip: Use the filters on the left to narrow down specific threats or export the current view to CSV.")
st.title("🛡️ Cygnal — Cyber Threat Intelligence")
st.markdown("Track, tag, and manage cyber threat indicators in real time.")

# ── Sidebar: Filters ─────────────────────────────────────────────
st.sidebar.title("🔍 Filters")
indicator_type = st.sidebar.selectbox(
    "Indicator Type",
    ["All", "IP", "Domain", "URL", "Hash", "Email"]
)
severity = st.sidebar.selectbox(
    "Severity",
    ["All", "low", "medium", "high", "critical"]
)

if st.sidebar.button("🔄 Refresh"):
    st.cache_data.clear()

@st.cache_data(ttl=60)
def cached_indicators(it: str, sv: str):
    return list_indicators(
        indicator_type=None if it == "All" else it,
        severity=None if sv == "All" else sv
    )

try:
    indicators = cached_indicators(indicator_type, severity)
except Exception as e:
    st.error(f"Failed to fetch indicators: {e}")
    indicators = []

# ── Metrics ──────────────────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total IOCs", len(indicators))

SEVERITY_COLORS = {
    "critical": "🔴",
    "high": "🟠",
    "medium": "🟡",
    "low": "🔵",
}

crit_count = sum(1 for i in indicators if i.get("severity") == "critical")
high_count = sum(1 for i in indicators if i.get("severity") == "high")
active_count = sum(1 for i in indicators if i.get("is_active"))

col2.metric(f"{SEVERITY_COLORS['critical']} Critical", crit_count)
col3.metric(f"{SEVERITY_COLORS['high']} High", high_count)
col4.metric("✅ Active", active_count)

st.divider()

# ── Table ────────────────────────────────────────────────────────
st.subheader("📋 Indicators")
if not indicators:
    st.info("No indicators found.")
else:
    try:
        df = pd.DataFrame(indicators)
        if "severity" in df.columns:
            df["severity"] = df["severity"].map(lambda s: f"{SEVERITY_COLORS.get(s, '')} {s}")
        if "tags" in df.columns:
            df["tags"] = df["tags"].map(lambda t: ", ".join(t) if isinstance(t, list) else str(t))
            
        desired_columns = ["id", "indicator_type", "value", "severity", "source", "confidence", "tags", "threat_actor", "is_active"]
        available_columns = [col for col in desired_columns if col in df.columns]
        
        st.dataframe(df[available_columns], use_container_width=True, hide_index=True)
        
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Export to CSV",
            data=csv,
            file_name='threat_indicators.csv',
            mime='text/csv',
        )
    except Exception as e:
        st.error(f"⚠️ Error rendering table: {e}")
        st.write("Raw data:", indicators)

st.divider()

# ── Add/Delete Forms ─────────────────────────────────────────────
with st.expander("➕ Add New Indicator"):
    with st.form("new_indicator_form", clear_on_submit=True):
        new_type = st.selectbox("Type", ["IP", "Domain", "URL", "Hash", "Email"])
        new_value = st.text_input("Value")
        new_severity = st.selectbox("Severity", ["low", "medium", "high", "critical"])
        new_source = st.text_input("Source")
        new_confidence = st.slider("Confidence", 0, 100, 50)
        new_tags = st.text_input("Tags (comma separated)")
        new_actor = st.text_input("Threat Actor (optional)")
        new_active = st.checkbox("Is Active", value=True)
        
        if st.form_submit_button("Add Indicator"):
            if new_value and new_source:
                tags_list = [t.strip() for t in new_tags.split(",") if t.strip()]
                create_indicator(
                    indicator_type=new_type,
                    value=new_value,
                    severity=new_severity,
                    source=new_source,
                    confidence=new_confidence,
                    tags=tags_list,
                    threat_actor=new_actor if new_actor else None,
                    is_active=new_active
                )
                st.success("Indicator added! Click Refresh.")
            else:
                st.error("Value and Source are required.")

with st.expander("🗑️ Delete Indicator"):
    with st.form("delete_indicator_form"):
        del_id = st.number_input("Indicator ID", min_value=1, step=1)
        if st.form_submit_button("Delete"):
            try:
                delete_indicator(del_id)
                st.success(f"Indicator {del_id} deleted! Click Refresh.")
            except Exception as e:
                st.error(f"Failed to delete: {e}")