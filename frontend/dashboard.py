from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from frontend.client import (
    analyze_indicator_ai,
    create_indicator,
    delete_indicator,
    generate_report,
    list_indicators,
    update_indicator,
)

# ── Page config ──────────────────────────────────────────────────
st.set_page_config(
    page_title="Cygnal",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ───────────────────────────────────────────────────
st.markdown(
    """
    <style>
        .metric-card {
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            border: 1px solid #0f3460;
            border-radius: 12px;
            padding: 1rem 1.5rem;
        }
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
        }
        .stTabs [data-baseweb="tab"] {
            border-radius: 8px 8px 0 0;
        }
        div[data-testid="stExpander"] {
            border: 1px solid #0f3460;
            border-radius: 8px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

SEVERITY_COLORS = {
    "critical": "🔴",
    "high": "🟠",
    "medium": "🟡",
    "low": "🟢",
}

SEVERITY_BG = {
    "critical": "#3d0000",
    "high": "#3d1a00",
    "medium": "#2e2a00",
    "low": "#002e0a",
}

INDICATOR_TYPES = ["All", "IP", "Domain", "URL", "Hash", "Email"]
SEVERITY_LEVELS = ["All", "critical", "high", "medium", "low"]

CHART_COLORS = {
    "critical": "#e63946",
    "high": "#f4a261",
    "medium": "#e9c46a",
    "low": "#2a9d8f",
    "IP": "#457b9d",
    "Domain": "#a8dadc",
    "URL": "#e76f51",
    "Hash": "#8ecae6",
    "Email": "#b5838d",
}


@st.cache_data(ttl=30)
def cached_indicators() -> list[dict]:
    return list_indicators()


# ── Sidebar ──────────────────────────────────────────────────────
with st.sidebar:
    st.image(
        "https://img.icons8.com/fluency/96/shield.png",
        width=64,
    )
    st.title("Cygnal")
    st.caption("Cyber Threat Intelligence")
    st.divider()

    st.header("🔍 Filters")
    selected_type = st.selectbox("Indicator Type", INDICATOR_TYPES)
    selected_severity = st.selectbox("Severity", SEVERITY_LEVELS)
    search_query = st.text_input("🔎 Free Search", placeholder="Search value, source, actor…")

    st.divider()
    if st.button("🔄 Refresh Data", width="stretch"):
        cached_indicators.clear()
        st.rerun()

    st.divider()
    st.caption("🕒 Cache refreshes every 30s")

# ── Header ───────────────────────────────────────────────────────
st.markdown("## 🛡️ Cygnal — Cyber Threat Intelligence")
st.caption("Track, tag, and manage cyber threat indicators in real time.")

# ── Load data ─────────────────────────────────────────────────────
try:
    all_indicators = cached_indicators()
except Exception as e:
    st.error(f"❌ Cannot connect to API: {e}")
    st.info("Make sure the backend is running: `uv run uvicorn backend.main:app --reload`")
    st.stop()

# ── Apply filters ─────────────────────────────────────────────────
filtered = all_indicators
if selected_type != "All":
    filtered = [i for i in filtered if i["indicator_type"] == selected_type]
if selected_severity != "All":
    filtered = [i for i in filtered if i["severity"] == selected_severity]
if search_query:
    q = search_query.lower()
    filtered = [
        i for i in filtered
        if q in i.get("value", "").lower()
        or q in i.get("source", "").lower()
        or q in (i.get("threat_actor") or "").lower()
        or any(q in tag.lower() for tag in i.get("tags", []))
    ]

# ── Metrics ───────────────────────────────────────────────────────
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("📊 Total IOCs", len(all_indicators))
col2.metric("🔴 Critical", sum(1 for i in all_indicators if i["severity"] == "critical"))
col3.metric("🟠 High", sum(1 for i in all_indicators if i["severity"] == "high"))
col4.metric("✅ Active", sum(1 for i in all_indicators if i["is_active"]))
col5.metric("🔍 Filtered", len(filtered))

st.divider()

# ── Charts ────────────────────────────────────────────────────────
if all_indicators:
    chart_col1, chart_col2 = st.columns(2)

    df_all = pd.DataFrame(all_indicators)

    with chart_col1:
        st.subheader("📊 By Severity")
        sev_counts = df_all["severity"].value_counts().reset_index()
        sev_counts.columns = ["severity", "count"]
        sev_order = ["critical", "high", "medium", "low"]
        sev_counts["severity"] = pd.Categorical(sev_counts["severity"], categories=sev_order, ordered=True)
        sev_counts = sev_counts.sort_values("severity")
        fig_sev = px.pie(
            sev_counts,
            names="severity",
            values="count",
            color="severity",
            color_discrete_map={k: CHART_COLORS[k] for k in ["critical", "high", "medium", "low"]},
            hole=0.45,
        )
        fig_sev.update_traces(textposition="inside", textinfo="percent+label")
        fig_sev.update_layout(
            showlegend=True,
            margin=dict(t=10, b=10, l=10, r=10),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#ccc",
        )
        st.plotly_chart(fig_sev, width="stretch")

    with chart_col2:
        st.subheader("🗂️ By Type")
        type_counts = df_all["indicator_type"].value_counts().reset_index()
        type_counts.columns = ["type", "count"]
        fig_type = px.bar(
            type_counts,
            x="type",
            y="count",
            color="type",
            color_discrete_map={k: CHART_COLORS.get(k, "#888") for k in type_counts["type"]},
            text="count",
        )
        fig_type.update_traces(textposition="outside")
        fig_type.update_layout(
            showlegend=False,
            margin=dict(t=10, b=10, l=10, r=10),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#ccc",
            xaxis=dict(title="", gridcolor="#333"),
            yaxis=dict(title="Count", gridcolor="#333"),
        )
        st.plotly_chart(fig_type, width="stretch")

    st.divider()

# ── Table ─────────────────────────────────────────────────────────
st.subheader(f"📋 Indicators ({len(filtered)} shown)")

if not filtered:
    st.info("No indicators match the current filters.")
else:
    df = pd.DataFrame(filtered)

    # Severity column with emoji
    df["severity_label"] = df["severity"].map(lambda s: f"{SEVERITY_COLORS.get(s, '')} {s}")
    df["tags"] = df["tags"].map(lambda t: ", ".join(t) if t else "—")
    df["threat_actor"] = df["threat_actor"].fillna("—")

    display_df = df[["id", "indicator_type", "value", "severity_label", "source", "confidence", "tags", "threat_actor", "is_active"]].copy()
    display_df.columns = ["ID", "Type", "Value", "Severity", "Source", "Conf%", "Tags", "Threat Actor", "Active"]

    # Color rows by severity
    def color_severity(row):
        sev = df.loc[row.name, "severity"] if row.name in df.index else ""
        bg = SEVERITY_BG.get(sev, "")
        if bg:
            return [f"background-color: {bg}"] * len(row)
        return [""] * len(row)

    styled = display_df.style.apply(color_severity, axis=1)

    st.dataframe(
        styled,
        width="stretch",
        hide_index=True,
        height=min(400, 40 + len(display_df) * 38),
    )

    # Export
    csv = pd.DataFrame(filtered).to_csv(index=False)
    st.download_button(
        label="📥 Export filtered to CSV",
        data=csv,
        file_name="cygnal_indicators.csv",
        mime="text/csv",
    )

st.divider()

# ── AI Analyst ────────────────────────────────────────────────────
st.subheader("🤖 AI Analyst")
tab1, tab2 = st.tabs(["🔍 Analyze Single IOC", "📊 Generate Threat Report"])

with tab1:
    if not all_indicators:
        st.info("No indicators to analyze.")
    else:
        options = {
            f"[{i['indicator_type']}] {i['value']} (id={i['id']})": i["id"]
            for i in all_indicators
        }
        selected_ioc = st.selectbox("Select indicator to analyze", list(options.keys()))
        if st.button("🔍 Analyze with AI", key="analyze_btn"):
            with st.spinner("Analyzing…"):
                try:
                    result = analyze_indicator_ai(options[selected_ioc])
                    st.success(f"**Analysis for `{result['value']}`:**")
                    st.write(result["analysis"])
                except Exception as e:
                    st.error(f"❌ Failed: {e}")

with tab2:
    if st.button("📊 Generate Threat Report", key="report_btn"):
        with st.spinner("Generating report…"):
            try:
                result = generate_report()
                st.success(f"**Report based on {result['total_indicators']} active indicators:**")
                st.write(result["report"])
            except Exception as e:
                st.error(f"❌ Failed: {e}")

st.divider()

# ── Add / Edit / Delete ───────────────────────────────────────────
action_tab1, action_tab2, action_tab3 = st.tabs(["➕ Add Indicator", "✏️ Edit Indicator", "🗑️ Delete Indicator"])

with action_tab1:
    with st.form("create_indicator_form"):
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

        submitted = st.form_submit_button("➕ Create Indicator", width="stretch")
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

with action_tab2:
    if not all_indicators:
        st.info("No indicators to edit.")
    else:
        edit_options = {
            f"[{i['indicator_type']}] {i['value']} (id={i['id']})": i
            for i in all_indicators
        }
        selected_label = st.selectbox("Select indicator to edit", list(edit_options.keys()), key="edit_select")
        ioc = edit_options[selected_label]

        with st.form("edit_indicator_form"):
            col1, col2 = st.columns(2)
            with col1:
                e_severity = st.selectbox(
                    "Severity",
                    ["low", "medium", "high", "critical"],
                    index=["low", "medium", "high", "critical"].index(ioc["severity"]),
                )
                e_source = st.text_input("Source", value=ioc.get("source", ""))
                e_confidence = st.slider("Confidence", 0, 100, ioc.get("confidence", 50))
            with col2:
                e_tags = st.text_input("Tags", value=", ".join(ioc.get("tags") or []))
                e_threat_actor = st.text_input("Threat Actor", value=ioc.get("threat_actor") or "")
                e_is_active = st.checkbox("Active", value=ioc.get("is_active", True))

            edit_submitted = st.form_submit_button("✏️ Update Indicator", width="stretch")
            if edit_submitted:
                try:
                    update_indicator(
                        indicator_id=ioc["id"],
                        severity=e_severity,
                        source=e_source,
                        confidence=e_confidence,
                        tags=[t.strip() for t in e_tags.split(",") if t.strip()],
                        threat_actor=e_threat_actor or None,
                        is_active=e_is_active,
                    )
                    cached_indicators.clear()
                    st.success("✅ Updated successfully")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Failed: {e}")

with action_tab3:
    if not all_indicators:
        st.info("No indicators to delete.")
    else:
        del_options = {
            f"[{i['indicator_type']}] {i['value']} (id={i['id']})": i["id"]
            for i in all_indicators
        }
        selected_del = st.selectbox("Select indicator to delete", list(del_options.keys()), key="del_select")
        st.warning(f"⚠️ This will permanently delete the selected indicator.")
        if st.button("🗑️ Confirm Delete", type="primary"):
            try:
                delete_indicator(del_options[selected_del])
                cached_indicators.clear()
                st.success("✅ Deleted successfully")
                st.rerun()
            except Exception as e:
                st.error(f"❌ Failed: {e}")