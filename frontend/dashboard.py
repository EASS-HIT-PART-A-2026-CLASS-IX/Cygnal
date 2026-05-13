import pandas as pd
import streamlit as st

from frontend.client import (
    list_indicators,
    create_indicator,
    delete_indicator,
    analyze_indicator_ai,
    generate_report,
)

st.set_page_config(page_title="Cygnal", page_icon="🛡️", layout="wide")
st.title("🛡️ Cygnal — Cyber Threat Intelligence")
st.caption("Track, tag, and manage cyber threat indicators in real time.")

SEVERITY_COLORS = {
    "critical": "🔴",
    "high": "🟠",
    "medium": "🟡",
    "low": "🟢",
}

INDICATOR_TYPES = ["All", "IP", "Domain", "URL", "Hash", "Email"]
SEVERITY_LEVELS = ["All", "critical", "high", "medium", "low"]


@st.cache_data(ttl=30)
def cached_indicators() -> list[dict]:
    return list_indicators()


# ── Sidebar filters ──────────────────────────────────────────────
with st.sidebar:
    st.header("🔍 Filters")
    selected_type = st.selectbox("Indicator Type", INDICATOR_TYPES)
    selected_severity = st.selectbox("Severity", SEVERITY_LEVELS)
    if st.button("🔄 Refresh"):
        cached_indicators.clear()
        st.rerun()

# ── Load data ────────────────────────────────────────────────────
try:
    all_indicators = cached_indicators()
except Exception as e:
    st.error(f"❌ Cannot connect to API: {e}")
    st.stop()

# ── Apply filters ────────────────────────────────────────────────
filtered = all_indicators
if selected_type != "All":
    filtered = [i for i in filtered if i["indicator_type"] == selected_type]
if selected_severity != "All":
    filtered = [i for i in filtered if i["severity"] == selected_severity]

# ── Metrics ──────────────────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total IOCs", len(all_indicators))
col2.metric("🔴 Critical", sum(1 for i in all_indicators if i["severity"] == "critical"))
col3.metric("🟠 High", sum(1 for i in all_indicators if i["severity"] == "high"))
col4.metric("✅ Active", sum(1 for i in all_indicators if i["is_active"]))

st.divider()

# ── Table ────────────────────────────────────────────────────────
st.subheader("📋 Indicators")
if not filtered:
    st.info("No indicators found.")
else:
    df = pd.DataFrame(filtered)
    df["severity"] = df["severity"].map(lambda s: f"{SEVERITY_COLORS.get(s, '')} {s}")
    df["tags"] = df["tags"].map(lambda t: ", ".join(t) if t else "—")
    st.dataframe(
        df[["id", "indicator_type", "value", "severity", "source", "confidence", "tags", "threat_actor", "is_active"]],
        use_container_width=True,
        hide_index=True,
    )

st.divider()

# ── Export CSV ───────────────────────────────────────────────────
if all_indicators:
    csv = pd.DataFrame(all_indicators).to_csv(index=False)
    st.download_button(
        label="📥 Export to CSV",
        data=csv,
        file_name="cygnal_indicators.csv",
        mime="text/csv",
    )

st.divider()

# ── AI Analyst ───────────────────────────────────────────────────
st.subheader("🤖 AI Analyst")

tab1, tab2 = st.tabs(["🔍 Analyze Single IOC", "📊 Generate Report"])

with tab1:
    if not all_indicators:
        st.info("No indicators to analyze.")
    else:
        options = {f"[{i['indicator_type']}] {i['value']} (id={i['id']})": i["id"] for i in all_indicators}
        selected_ioc = st.selectbox("Select indicator to analyze", list(options.keys()))
        if st.button("🔍 Analyze with AI"):
            with st.spinner("Analyzing..."):
                try:
                    result = analyze_indicator_ai(options[selected_ioc])
                    st.success(f"**Analysis for `{result['value']}`:**")
                    st.write(result["analysis"])
                except Exception as e:
                    st.error(f"❌ Failed: {e}")

with tab2:
    if st.button("📊 Generate Threat Report"):
        with st.spinner("Generating report..."):
            try:
                result = generate_report()
                st.success(f"**Report based on {result['total_indicators']} active indicators:**")
                st.write(result["report"])
            except Exception as e:
                st.error(f"❌ Failed: {e}")

st.divider()

# ── Add new indicator ────────────────────────────────────────────
with st.expander("➕ Add New Indicator"):
    with st.form("create_indicator"):
        col1, col2 = st.columns(2)
        with col1:
            itype = st.selectbox("Type", ["IP", "Domain", "URL", "Hash", "Email"])
            value = st.text_input("Value", placeholder="e.g. 192.168.1.1")
            severity = st.selectbox("Severity", ["low", "medium", "high", "critical"])
            source = st.text_input("Source", placeholder="e.g. AbuseIPDB")
        with col2:
            confidence = st.slider("Confidence", 0, 100, 50)
            tags_input = st.text_input("Tags (comma separated)", placeholder="e.g. ransomware, APT29")
            threat_actor = st.text_input("Threat Actor (optional)", placeholder="e.g. Lazarus Group")
            is_active = st.checkbox("Active", value=True)

        submitted = st.form_submit_button("➕ Create Indicator")

    if submitted:
        if not value or not source:
            st.warning("⚠️ Value and Source are required.")
        else:
            try:
                tags = [t.strip() for t in tags_input.split(",") if t.strip()]
                indicator = create_indicator(
                    indicator_type=itype,
                    value=value,
                    severity=severity,
                    source=source,
                    confidence=confidence,
                    tags=tags,
                    threat_actor=threat_actor or None,
                    is_active=is_active,
                )
                cached_indicators.clear()
                st.success(f"✅ Created [{indicator['indicator_type']}] {indicator['value']}")
                st.rerun()
            except Exception as e:
                st.error(f"❌ Failed: {e}")

st.divider()

# ── Delete indicator ─────────────────────────────────────────────
with st.expander("🗑️ Delete Indicator"):
    if not all_indicators:
        st.info("No indicators to delete.")
    else:
        options = {f"[{i['indicator_type']}] {i['value']} (id={i['id']})": i["id"] for i in all_indicators}
        selected = st.selectbox("Select indicator to delete", list(options.keys()))
        if st.button("🗑️ Delete"):
            try:
                delete_indicator(options[selected])
                cached_indicators.clear()
                st.success("✅ Deleted successfully")
                st.rerun()
            except Exception as e:
                st.error(f"❌ Failed: {e}")