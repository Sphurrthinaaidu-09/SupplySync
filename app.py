import streamlit as st
import pandas as pd
import plotly.express as px

from database import (
    get_total_orders,
    get_otif_percentage,
    get_products_at_risk,
    get_critical_risk_count,
    get_supply_chain_health,
    get_critical_risks,
    get_risk_center_data,
    get_replenishment_recommendations,
    get_supported_upload_schemas,
    detect_plastic_dataset,
    validate_plastic_upload,
    load_plastic_table_data,
    log_ingestion,
    get_latest_ingestion,
    get_ingestion_history,
)

from ai_engine import ask_supplysync


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="SupplySync — AI Supply Chain Control Tower",
    page_icon="S",
    layout="wide",
    initial_sidebar_state="locked",
)


# ============================================================
# DESIGN SYSTEM
# Code 1 visual language: slate / teal enterprise palette.
# Functional contracts remain those of the tested SupplySync app.
# ============================================================

st.markdown(
    """
<style>
:root {
    --navy: #1E3A4C;
    --navy-2: #2D4A5E;
    --ink: #1E293B;
    --muted: #64748B;
    --muted-2: #94A3B8;
    --canvas: #E2EBF0;
    --surface: #F8FAFC;
    --white: #FFFFFF;
    --line: #CBD5E1;
    --line-soft: #E2E8F0;
    --teal: #0F766E;
    --teal-soft: #ECFDF5;
    --red: #DC2626;
    --red-soft: #FFF5F5;
    --amber: #D97706;
    --amber-soft: #FFFBEB;
    --green: #15803D;
    --green-soft: #F0FDF4;
}
.stApp { background: var(--canvas) !important; color: var(--ink) !important; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; }
.main .block-container { padding: 1.7rem 2.2rem 3rem 2.2rem; max-width: 1500px; }
#MainMenu, footer { visibility: hidden; }
header[data-testid="stHeader"] { background: transparent !important; z-index: 100000; }
section[data-testid="stSidebar"] { background: var(--navy) !important; border-right: none !important; display: block !important; min-width: 258px !important; }
section[data-testid="stSidebar"] > div { padding-top: 1.2rem; }
section[data-testid="stSidebar"] * { color: #E2E8F0 !important; }
section[data-testid="stSidebar"] .stRadio > div { gap: 5px; }
section[data-testid="stSidebar"] .stRadio label { border-radius: 10px; padding: 9px 12px; font-size: .86rem; font-weight: 600; color: #CBD5E1 !important; transition: .15s ease; }
section[data-testid="stSidebar"] .stRadio label:hover { background: var(--navy-2) !important; color: #FFFFFF !important; }
.sidebar-brand { padding: .2rem .35rem .9rem .35rem; }
.sidebar-brand-name { color: #FFFFFF !important; font-size: 1.3rem; font-weight: 800; letter-spacing: -.03em; }
.sidebar-brand-sub { color: #AFC1CC !important; font-size: .72rem; line-height: 1.45; margin-top: 4px; }
.sidebar-rule { height: 1px; background: #365367; margin: .7rem 0 1rem 0; }
.sidebar-label { color: #8FA5B2 !important; font-size: .63rem; font-weight: 800; letter-spacing: .12em; text-transform: uppercase; margin: 0 .35rem .45rem .35rem; }
.sidebar-status { margin: 1.2rem .35rem 0 .35rem; padding: .75rem .8rem; border: 1px solid #365367; border-radius: 10px; background: rgba(255,255,255,.035); }
.sidebar-status-title { color: #FFFFFF !important; font-size: .72rem; font-weight: 700; }
.sidebar-status-text { color: #AFC1CC !important; font-size: .66rem; margin-top: 3px; }
.page-kicker { color: var(--teal); font-size: .66rem; font-weight: 800; letter-spacing: .12em; text-transform: uppercase; margin-bottom: 5px; }
.page-title { color: var(--ink); font-size: 1.82rem; line-height: 1.15; font-weight: 800; letter-spacing: -.035em; margin-bottom: 5px; }
.page-description { color: var(--muted); font-size: .86rem; line-height: 1.55; max-width: 760px; }
.header-status { background: rgba(248,250,252,.82); border: 1px solid var(--line); border-radius: 12px; padding: .65rem .85rem; text-align: right; }
.header-status-label { color: var(--muted-2); font-size: .59rem; font-weight: 800; letter-spacing: .1em; text-transform: uppercase; }
.header-status-value { color: var(--navy); font-size: .78rem; font-weight: 800; margin-top: 2px; }
.section-title { color: var(--ink); font-size: 1.02rem; font-weight: 800; letter-spacing: -.015em; margin: 1.35rem 0 .18rem 0; }
.section-caption { color: var(--muted); font-size: .75rem; line-height: 1.45; margin-bottom: .7rem; }
.kpi-card { background: var(--surface); border: 1px solid var(--line); border-top: 3px solid var(--navy); border-radius: 13px; padding: 1rem 1.05rem .9rem 1.05rem; min-height: 116px; box-shadow: 0 2px 6px rgba(30,58,76,.045); }
.kpi-card.alert { border-top-color: var(--red); background: #FCF9F9; }
.kpi-label { color: var(--muted); font-size: .64rem; font-weight: 800; letter-spacing: .09em; text-transform: uppercase; }
.kpi-value { color: var(--ink); font-size: 1.72rem; font-weight: 850; line-height: 1.05; margin-top: 9px; letter-spacing: -.035em; }
.kpi-note { color: var(--muted-2); font-size: .67rem; margin-top: 7px; }
.panel { background: var(--surface); border: 1px solid var(--line); border-radius: 14px; box-shadow: 0 2px 6px rgba(30,58,76,.04); padding: 1rem 1.1rem; }
.panel-title { color: var(--ink); font-size: .78rem; font-weight: 850; letter-spacing: .07em; text-transform: uppercase; }
.panel-subtitle { color: var(--muted); font-size: .72rem; margin-top: 3px; line-height: 1.4; }
.health-status { font-size: 1.45rem; font-weight: 850; letter-spacing: -.03em; margin-top: 7px; }
.health-critical { color: var(--red); }
.health-high { color: #C2410C; }
.health-attention { color: var(--amber); }
.health-healthy { color: var(--green); }
.health-message { color: var(--muted); font-size: .73rem; margin-top: 4px; }
.health-count { border-left: 1px solid var(--line-soft); padding-left: .8rem; }
.health-count-label { color: var(--muted-2); font-size: .61rem; font-weight: 800; letter-spacing: .07em; text-transform: uppercase; }
.health-count-value { color: var(--ink); font-size: 1.35rem; font-weight: 850; margin-top: 4px; }
.risk-card { background: var(--surface); border: 1px solid var(--line); border-left: 4px solid var(--red); border-radius: 12px; padding: .95rem 1rem; margin-bottom: .7rem; box-shadow: 0 2px 6px rgba(30,58,76,.035); }
.risk-card.high { border-left-color: #EA580C; }
.risk-card.medium { border-left-color: var(--amber); }
.risk-card.low { border-left-color: #64748B; }
.risk-title { color: var(--ink); font-size: 1rem; font-weight: 850; }
.risk-subtitle { color: var(--muted); font-size: .7rem; margin-top: 2px; }
.risk-badge { display: inline-block; padding: 3px 8px; border-radius: 999px; font-size: .62rem; font-weight: 850; }
.badge-critical { color: #991B1B; background: #FEE2E2; border: 1px solid #FECACA; }
.badge-high { color: #9A3412; background: #FFEDD5; border: 1px solid #FED7AA; }
.badge-medium { color: #92400E; background: #FEF3C7; border: 1px solid #FDE68A; }
.badge-low { color: #475569; background: #F1F5F9; border: 1px solid #E2E8F0; }
.risk-metric-label { color: var(--muted-2); font-size: .58rem; font-weight: 800; letter-spacing: .07em; text-transform: uppercase; }
.risk-metric-value { color: var(--ink); font-size: .9rem; font-weight: 800; margin-top: 2px; }
.reason-box { background: #F1F5F9; border: 1px solid var(--line-soft); border-radius: 9px; padding: .55rem .7rem; color: #475569; font-size: .7rem; line-height: 1.45; margin-top: .55rem; }
.action-box { background: #EEF7F6; border: 1px solid #C7E7E3; border-radius: 9px; padding: .55rem .7rem; color: #115E59; font-size: .7rem; line-height: 1.45; margin-top: .45rem; font-weight: 650; }
.procurement-hero { background: var(--navy); color: #FFFFFF; border-radius: 14px; padding: 1.2rem 1.25rem; box-shadow: 0 5px 14px rgba(30,58,76,.13); }
.procurement-eyebrow { color: #AFC1CC; font-size: .61rem; font-weight: 800; letter-spacing: .11em; text-transform: uppercase; }
.procurement-product { color: #FFFFFF; font-size: 1.35rem; font-weight: 850; margin-top: 5px; }
.procurement-supplier { color: #D7E3E8; font-size: .72rem; margin-top: 2px; }
.procurement-number { color: #FFFFFF; font-size: 1.25rem; font-weight: 850; margin-top: 4px; }
.procurement-label { color: #AFC1CC; font-size: .57rem; font-weight: 800; letter-spacing: .07em; text-transform: uppercase; margin-top: 1rem; }
.procurement-note { color: #D7E3E8; font-size: .67rem; line-height: 1.4; margin-top: 3px; }
.ingest-step { display: flex; align-items: center; gap: 8px; padding: .55rem .65rem; border: 1px solid var(--line-soft); background: #FFFFFF; border-radius: 9px; margin-bottom: .45rem; }
.ingest-dot { width: 9px; height: 9px; border-radius: 50%; background: var(--teal); flex: 0 0 auto; }
.ingest-step-text { color: var(--ink); font-size: .68rem; font-weight: 750; }
.ingest-step-sub { color: var(--muted-2); font-size: .6rem; margin-left: auto; }
.ai-hero { background: var(--navy); border-radius: 15px; padding: 1.35rem 1.45rem; color: #FFFFFF; box-shadow: 0 6px 16px rgba(30,58,76,.12); }
.ai-eyebrow { color: #AFC1CC; font-size: .61rem; font-weight: 850; letter-spacing: .12em; text-transform: uppercase; }
.ai-title { color: #FFFFFF; font-size: 1.35rem; font-weight: 850; margin-top: 4px; }
.ai-subtitle { color: #D7E3E8; font-size: .72rem; line-height: 1.45; max-width: 780px; margin-top: 4px; }
.ai-status { display: inline-block; margin-top: 10px; padding: 4px 9px; border-radius: 999px; background: rgba(255,255,255,.1); border: 1px solid rgba(255,255,255,.15); color: #E2E8F0; font-size: .61rem; font-weight: 750; }
.ai-answer { background: var(--surface); border: 1px solid var(--line); border-left: 4px solid var(--teal); border-radius: 13px; padding: 1rem 1.1rem; box-shadow: 0 2px 6px rgba(30,58,76,.035); }
.empty-state { text-align: center; padding: 2rem 1rem; }
.empty-state-title { color: var(--ink); font-size: .95rem; font-weight: 800; }
.empty-state-text { color: var(--muted); font-size: .72rem; margin-top: 5px; }
div[data-testid="stVerticalBlockBorderWrapper"] { border-radius: 13px !important; border-color: var(--line) !important; background: var(--surface) !important; box-shadow: 0 2px 6px rgba(30,58,76,.035) !important; }
.stButton > button { border-radius: 9px !important; font-weight: 700 !important; border-color: var(--line) !important; }
.stButton > button[kind="primary"] { background: var(--navy) !important; border-color: var(--navy) !important; color: #FFFFFF !important; }
.stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] > div { border-radius: 9px !important; }
[data-testid="stDataFrame"] { border: 1px solid var(--line-soft); border-radius: 10px; overflow: hidden; }
.stMetric { background: #FFFFFF; border-radius: 10px; padding: .35rem .45rem; }
</style>
""",
    unsafe_allow_html=True,
)


# ============================================================
# HELPERS
# ============================================================

def as_records(value):
    if isinstance(value, pd.DataFrame):
        return value.to_dict(orient="records")
    if isinstance(value, list):
        return value
    if isinstance(value, dict):
        return [value]
    return []


def money_inr(value):
    try:
        value = float(value)
    except Exception:
        return "₹0"
    if abs(value) >= 1_000_000:
        return f"₹{value / 1_000_000:.2f}M"
    if abs(value) >= 100_000:
        return f"₹{value / 100_000:.2f}L"
    return f"₹{value:,.0f}"


def risk_class(level):
    level = str(level or "").lower()
    if level == "critical":
        return "risk-card", "badge-critical"
    if level == "high":
        return "risk-card high", "badge-high"
    if level == "medium":
        return "risk-card medium", "badge-medium"
    return "risk-card low", "badge-low"


def health_class(status):
    mapping = {
        "Critical": ("health-critical", "Immediate attention required"),
        "High Risk": ("health-high", "High-priority risks require attention"),
        "Attention Required": ("health-attention", "Some operational risks require monitoring"),
        "Healthy": ("health-healthy", "Supply chain operating within healthy levels"),
    }
    return mapping.get(status, ("health-attention", "Current risk conditions require review"))


def render_page_header(kicker, title, description, status_label=None, status_value=None):
    left, right = st.columns([7, 2], gap="large")
    with left:
        st.markdown(f'<div class="page-kicker">{kicker}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="page-title">{title}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="page-description">{description}</div>', unsafe_allow_html=True)
    with right:
        if status_label and status_value:
            st.markdown(f'<div class="header-status"><div class="header-status-label">{status_label}</div><div class="header-status-value">{status_value}</div></div>', unsafe_allow_html=True)


def render_kpi(label, value, note, alert=False):
    cls = "kpi-card alert" if alert else "kpi-card"
    st.markdown(f'<div class="{cls}"><div class="kpi-label">{label}</div><div class="kpi-value">{value}</div><div class="kpi-note">{note}</div></div>', unsafe_allow_html=True)


def _first_present(record, *keys, default="—"):
    """Return the first non-empty value available under the supplied keys."""
    for key in keys:
        value = record.get(key)
        if value is not None and str(value).strip() and str(value).strip().lower() != "nan":
            return value
    return default


def _display_number(value, suffix=""):
    """Format optional numeric values without turning missing data into fake zeroes."""
    if value is None or str(value).strip() in {"", "—", "nan", "None"}:
        return "—"
    try:
        number = float(value)
        if number.is_integer():
            return f"{int(number):,}{suffix}"
        return f"{number:,.2f}{suffix}"
    except Exception:
        return f"{value}{suffix}"


def render_risk_card(risk, compact=False):
    level = str(risk.get("risk_level", "Low"))
    card_cls, badge_cls = risk_class(level)

    # ---------------------------------------------------------
    # Basic identity
    # ---------------------------------------------------------

    product = str(
        _first_present(
            risk,
            "product_name",
            "item_name",
            "reference_id",
            default="Unknown item",
        )
    )

    supplier = str(
        _first_present(
            risk,
            "supplier_name",
            default="Supplier not assigned",
        )
    )

    risk_type = str(
        _first_present(
            risk,
            "risk_type",
            default="Operational",
        )
    )

    reference_id = str(
        _first_present(
            risk,
            "reference_id",
            default="",
        )
    )

    score = _display_number(
        risk.get("risk_score")
    )

    # ---------------------------------------------------------
    # Why this is a risk
    # ---------------------------------------------------------

    reason = _first_present(
        risk,
        "risk_reason",
        "reason",
        "rationale",
        default="Review the current operational evidence.",
    )

    # ---------------------------------------------------------
    # Recommended action
    #
    # decision_action comes from decision_recommendations.
    # recommended_action comes from risk_assessments.
    #
    # Prefer the actual decision recommendation.
    # ---------------------------------------------------------

    action = _first_present(
        risk,
        "decision_action",
        "recommended_action",
        default="Review the current risk evidence.",
    )

    # ---------------------------------------------------------
    # Additional recommendation information
    # ---------------------------------------------------------

    recommendation_status = _first_present(
        risk,
        "recommendation_status",
        default="",
    )

    priority = _first_present(
        risk,
        "priority",
        default="",
    )

    recommended_qty = _display_number(
        risk.get("recommended_qty")
    )

    recommended_supplier = _first_present(
        risk,
        "recommended_supplier_name",
        default="",
    )

    estimated_cost = _display_number(
        risk.get("estimated_cost")
    )

    # ---------------------------------------------------------
    # Build optional recommendation metrics safely
    # ---------------------------------------------------------

    optional_metrics = ""

    if priority:
        optional_metrics += (
            f'<div>'
            f'<div class="risk-metric-label">Priority</div>'
            f'<div class="risk-metric-value">{priority}</div>'
            f'</div>'
        )

    if recommended_qty != "—":
        optional_metrics += (
            f'<div>'
            f'<div class="risk-metric-label">'
            f'Recommended quantity'
            f'</div>'
            f'<div class="risk-metric-value">'
            f'{recommended_qty}'
            f'</div>'
            f'</div>'
        )

    if estimated_cost != "—":
        optional_metrics += (
            f'<div>'
            f'<div class="risk-metric-label">'
            f'Estimated cost'
            f'</div>'
            f'<div class="risk-metric-value">'
            f'{estimated_cost}'
            f'</div>'
            f'</div>'
        )

    if recommendation_status:
        optional_metrics += (
            f'<div>'
            f'<div class="risk-metric-label">'
            f'Recommendation status'
            f'</div>'
            f'<div class="risk-metric-value">'
            f'{recommendation_status}'
            f'</div>'
            f'</div>'
        )

    # ---------------------------------------------------------
    # Recommended supplier
    # ---------------------------------------------------------

    recommended_supplier_html = ""

    if recommended_supplier:
        recommended_supplier_html = (
            f'<div style="margin-top:11px;">'
            f'<div class="risk-metric-label">'
            f'Recommended supplier'
            f'</div>'
            f'<div class="risk-metric-value">'
            f'{recommended_supplier}'
            f'</div>'
            f'</div>'
        )

    # ---------------------------------------------------------
    # Compact card
    # Used on Executive Dashboard
    # ---------------------------------------------------------

    if compact:

        compact_html = (
            f'<div class="{card_cls}">'

            f'<div style="display:flex;'
            f'justify-content:space-between;'
            f'align-items:flex-start;gap:10px;">'

            f'<div>'
            f'<div class="risk-title">{product}</div>'
            f'<div class="risk-subtitle">'
            f'{risk_type}'
            f'</div>'
            f'</div>'

            f'<div style="text-align:right;">'

            f'<span class="risk-badge {badge_cls}">'
            f'{level.upper()}'
            f'</span>'

            f'<div style="color:#1E293B;'
            f'font-size:.8rem;font-weight:850;'
            f'margin-top:4px;">'
            f'Score {score}'
            f'</div>'

            f'</div>'

            f'</div>'

            f'<div style="display:flex;'
            f'gap:24px;flex-wrap:wrap;'
            f'margin-top:11px;">'

            f'<div>'
            f'<div class="risk-metric-label">'
            f'Risk type'
            f'</div>'
            f'<div class="risk-metric-value">'
            f'{risk_type}'
            f'</div>'
            f'</div>'

            f'<div>'
            f'<div class="risk-metric-label">'
            f'Supplier'
            f'</div>'
            f'<div class="risk-metric-value">'
            f'{supplier}'
            f'</div>'
            f'</div>'

            f'</div>'

            f'<div class="reason-box">'
            f'<b>Why this is a risk</b><br>'
            f'{reason}'
            f'</div>'

            f'<div class="action-box">'
            f'<b>Next step:</b> {action}'
            f'</div>'

            f'</div>'
        )

        st.markdown(
            compact_html,
            unsafe_allow_html=True,
        )

        return

    # ---------------------------------------------------------
    # Main Risk Center card
    # ---------------------------------------------------------

    risk_metadata_html = (
        f'<div style="display:flex;'
        f'gap:28px;flex-wrap:wrap;'
        f'margin-top:11px;">'

        f'<div>'
        f'<div class="risk-metric-label">'
        f'Risk type'
        f'</div>'
        f'<div class="risk-metric-value">'
        f'{risk_type}'
        f'</div>'
        f'</div>'

        f'<div>'
        f'<div class="risk-metric-label">'
        f'Supplier'
        f'</div>'
        f'<div class="risk-metric-value">'
        f'{supplier}'
        f'</div>'
        f'</div>'

        f'<div>'
        f'<div class="risk-metric-label">'
        f'Reference'
        f'</div>'
        f'<div class="risk-metric-value">'
        f'{reference_id}'
        f'</div>'
        f'</div>'

        f'</div>'
    )

    recommendation_html = ""

    if optional_metrics:
        recommendation_html = (
            f'<div style="display:flex;'
            f'gap:28px;flex-wrap:wrap;'
            f'margin-top:11px;">'
            f'{optional_metrics}'
            f'</div>'
        )

    main_html = (
        f'<div class="{card_cls}">'

        # -----------------------------------------------------
        # Header
        # -----------------------------------------------------

        f'<div style="display:flex;'
        f'justify-content:space-between;'
        f'align-items:flex-start;gap:10px;">'

        f'<div>'

        f'<div class="risk-title">'
        f'{product}'
        f'</div>'

        f'<div class="risk-subtitle">'
        f'{supplier}'
        f'</div>'

        f'</div>'

        f'<div style="text-align:right;">'

        f'<span class="risk-badge {badge_cls}">'
        f'{level.upper()}'
        f'</span>'

        f'<div style="color:#1E293B;'
        f'font-size:.82rem;font-weight:850;'
        f'margin-top:4px;">'
        f'Risk score {score}'
        f'</div>'

        f'</div>'

        f'</div>'

        # Risk metadata
        f'{risk_metadata_html}'

        # Optional recommendation metrics
        f'{recommendation_html}'

        # Recommended supplier
        f'{recommended_supplier_html}'

        # Why this is a risk
        f'<div class="reason-box">'
        f'<b>Why this is a risk</b><br>'
        f'{reason}'
        f'</div>'

        # Recommended next step
        f'<div class="action-box">'
        f'<b>Recommended next step</b><br>'
        f'{action}'
        f'</div>'

        f'</div>'
    )

    st.markdown(
        main_html,
        unsafe_allow_html=True,
    )


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:
    st.markdown('<div class="sidebar-brand"><div class="sidebar-brand-name">SupplySync⚡</div><div class="sidebar-brand-sub">AI-Powered Supply Chain<br>Decision Intelligence</div></div><div class="sidebar-rule"></div><div class="sidebar-label">Control Tower</div>', unsafe_allow_html=True)
    selected_page = st.radio(
        "Navigation",
        options=[
            "📊  Executive Dashboard",
            "🚨  Risk Center",
            "📦  Replenishment",
            "📤  Data Ingestion",
            "🤖  Ask SupplySync",
        ],
        index=0,
        label_visibility="collapsed",
    )
    st.markdown('<div class="sidebar-status"><div class="sidebar-status-title">● SupplySync operational</div><div class="sidebar-status-text">Connected to PostgreSQL decision engine</div></div>', unsafe_allow_html=True)


# ============================================================
# PAGE 1 — EXECUTIVE DASHBOARD
# ============================================================

if selected_page == "📊  Executive Dashboard":
    render_page_header(
        "SUPPLY CHAIN OVERVIEW",
        "Welcome Back!",
        "Understand the current operating position, identify priority exceptions and move directly to procurement action.",
        "DATA ENGINE",
        "PostgreSQL",
    )
    st.markdown('<div style="height:18px"></div>', unsafe_allow_html=True)
    try:
        total_orders = get_total_orders()
        otif_percentage = get_otif_percentage()
        products_at_risk = get_products_at_risk()
        critical_risks_count = get_critical_risk_count()
        health = get_supply_chain_health()
        critical_risks = as_records(get_critical_risks())
        all_risks = as_records(get_risk_center_data())
        replenishment = as_records(get_replenishment_recommendations())
    except Exception as e:
        st.error("Unable to load executive analytics from PostgreSQL.")
        st.caption(f"Technical detail: {str(e)}")
        st.stop()
    k1, k2, k3, k4 = st.columns(4, gap="medium")
    with k1: render_kpi("Total orders", f"📦{int(total_orders):,}", "Order-level volume")
    with k2: render_kpi("OTIF performance", f"📈{float(otif_percentage):.2f}%", "On-time in-full")
    with k3: render_kpi("Products at risk", f"⚠️{int(products_at_risk):,}", "Open high-impact SKUs")
    with k4: render_kpi("Critical risks", f"🚨{int(critical_risks_count):,}", "Immediate attention", alert=int(critical_risks_count) > 0)

    st.markdown('<div class="section-title">Current operating position</div><div class="section-caption">The control tower summarizes the database risk state before showing individual exceptions.</div>', unsafe_allow_html=True)
    health_status = str(health.get("overall_status", "Unknown")) if isinstance(health, dict) else "Unknown"
    hclass, hmessage = health_class(health_status)
    counts = {x: sum(1 for r in all_risks if str(r.get("risk_level", "")) == x) for x in ["Critical", "High", "Medium", "Low"]}
    with st.container(border=True):
        left, right = st.columns([2.15, 3.85], gap="large")
        with left:
            st.markdown(f'<div class="panel-title">Overall supply chain status</div><div class="health-status {hclass}">{health_status}</div><div class="health-message">{hmessage}</div>', unsafe_allow_html=True)
        with right:
            hc1, hc2, hc3, hc4 = st.columns(4)
            for col, label in zip([hc1, hc2, hc3, hc4], ["Critical", "High", "Medium", "Low"]):
                with col:
                    st.markdown(f'<div class="health-count"><div class="health-count-label">{label}</div><div class="health-count-value">{counts[label]}</div></div>', unsafe_allow_html=True)

    st.markdown('<div class="section-title">Priority risk queue</div><div class="section-caption">Highest-priority operational exceptions, ordered by the risk engine.</div>', unsafe_allow_html=True)
    if critical_risks:
        risk_cols = st.columns(2, gap="medium")
        for idx, risk in enumerate(critical_risks[:4]):
            with risk_cols[idx % 2]:
                render_risk_card(risk, compact=True)
    else:
        st.markdown('<div class="panel empty-state"><div class="empty-state-title">No critical operational exceptions</div><div class="empty-state-text">The current database does not contain critical risks.</div></div>', unsafe_allow_html=True)

    st.markdown('<div class="section-title">Procurement action center</div><div class="section-caption">Translate the risk state into concrete replenishment decisions.</div>', unsafe_allow_html=True)
    if replenishment:
        rdf = pd.DataFrame(replenishment)
        total_qty = int(rdf["recommended_order_qty"].sum()) if "recommended_order_qty" in rdf else 0
        total_cost = float(rdf["estimated_cost"].sum()) if "estimated_cost" in rdf else 0
        a1, a2, a3 = st.columns(3)
        with a1: render_kpi("SKUs requiring action", f"{len(rdf):,}", "Current replenishment queue")
        with a2: render_kpi("Recommended quantity", f"{total_qty:,}", "Units to procure")
        with a3: render_kpi("Estimated commitment", money_inr(total_cost), "Calculated from recommendation data")
        show = rdf[[c for c in ["product_name", "risk_level", "recommended_order_qty", "supplier_name", "estimated_cost"] if c in rdf.columns]].head(6)
        st.dataframe(show, use_container_width=True, hide_index=True)
    else:
        st.markdown('<div class="panel empty-state"><div class="empty-state-title">No replenishment actions</div><div class="empty-state-text">Current inventory does not require procurement action.</div></div>', unsafe_allow_html=True)

    st.markdown('<div class="section-title">AI executive briefing</div><div class="section-caption">A concise operational interpretation built from the same live database signals.</div>', unsafe_allow_html=True)
    if critical_risks:
        first = critical_risks[0]
        st.markdown(f'<div class="ai-answer"><div class="panel-title">SUPPLYSYNC AI BRIEFING</div><div style="color:#1E293B;font-size:.86rem;line-height:1.55;margin-top:8px;">The highest-priority current exception is <b>{first.get("product_name", "the flagged product")}</b> at <b>risk score {int(float(first.get("risk_score", 0) or 0))}</b>. The risk engine indicates that operational attention should focus on inventory coverage and the associated supplier conditions. Review the Risk Center for evidence and Replenishment for the purchasing response.</div></div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="ai-answer"><div class="panel-title">SUPPLYSYNC AI BRIEFING</div><div style="color:#1E293B;font-size:.86rem;line-height:1.55;margin-top:8px;">No critical risk is currently flagged. Continue monitoring inventory coverage, supplier performance and fulfillment service levels.</div></div>', unsafe_allow_html=True)


# ============================================================
# PAGE 2 — RISK CENTER
# ============================================================

elif selected_page == "🚨  Risk Center":

    render_page_header(
        "RISK MANAGEMENT",
        "Risk Center",
        "Monitor supply-chain exceptions by severity, risk type, product and supplier, then inspect the evidence behind each risk.",
        "RISK ENGINE",
        "Active",
    )

    try:
        risk_data = as_records(get_risk_center_data())

    except Exception as e:
        st.error("Unable to load active risk data from PostgreSQL.")
        st.caption(f"Technical detail: {str(e)}")
        st.stop()

    if not risk_data:

        st.markdown(
            '<div class="panel empty-state">'
            '<div class="empty-state-title">No active supply-chain risks</div>'
            '<div class="empty-state-text">'
            'The current database contains no open risks requiring attention.'
            '</div></div>',
            unsafe_allow_html=True,
        )

    else:

        # -----------------------------------------------------
        # Risk severity summary
        # -----------------------------------------------------

        critical = sum(
            1 for r in risk_data
            if r.get("risk_level") == "Critical"
        )

        high = sum(
            1 for r in risk_data
            if r.get("risk_level") == "High"
        )

        medium = sum(
            1 for r in risk_data
            if r.get("risk_level") == "Medium"
        )

        low = sum(
            1 for r in risk_data
            if r.get("risk_level") == "Low"
        )

        c1, c2, c3, c4 = st.columns(4, gap="medium")

        with c1:
            render_kpi(
                "Critical",
                critical,
                "Immediate action",
                alert=critical > 0,
            )

        with c2:
            render_kpi(
                "High",
                high,
                "Near-term action",
            )

        with c3:
            render_kpi(
                "Medium",
                medium,
                "Monitor",
            )

        with c4:
            render_kpi(
                "Low",
                low,
                "Background exposure",
            )

        # -----------------------------------------------------
        # Risk data
        # -----------------------------------------------------

        rdf = pd.DataFrame(risk_data)

        st.markdown(
            '<div class="section-title">Risk filters</div>'
            '<div class="section-caption">'
            'Narrow the operational queue by severity, risk type, '
            'product and supplier.'
            '</div>',
            unsafe_allow_html=True,
        )

        # -----------------------------------------------------
        # Four filters
        # -----------------------------------------------------

        f1, f2, f3, f4 = st.columns(4)

        # Severity
        with f1:

            levels = (
                ["All"]
                + sorted(
                    [
                        str(x)
                        for x in rdf["risk_level"].dropna().unique()
                    ]
                )
                if "risk_level" in rdf
                else ["All"]
            )

            selected_level = st.selectbox(
                "Severity",
                levels,
            )

        # Risk Type
        with f2:

            preferred_risk_types = [
                "Production",
                "Quality",
                "Supplier",
                "Delivery",
                "Inventory",
            ]

            if "risk_type" in rdf:

                existing_risk_types = {
                    str(x)
                    for x in rdf["risk_type"].dropna().unique()
                }

                ordered_risk_types = [
                    risk_type
                    for risk_type in preferred_risk_types
                    if risk_type in existing_risk_types
                ]

                # Include any unexpected future risk types
                # without breaking the filter.
                additional_risk_types = sorted(
                    existing_risk_types
                    - set(preferred_risk_types)
                )

                risk_types = (
                    ["All"]
                    + ordered_risk_types
                    + additional_risk_types
                )

            else:
                risk_types = ["All"]

            selected_risk_type = st.selectbox(
                "Risk Type",
                risk_types,
            )

        # Product
        with f3:

            products = (
                ["All"]
                + sorted(
                    [
                        str(x)
                        for x in rdf["product_name"].dropna().unique()
                    ]
                )
                if "product_name" in rdf
                else ["All"]
            )

            selected_product = st.selectbox(
                "Product",
                products,
            )

        # Supplier
        with f4:

            suppliers = (
                ["All"]
                + sorted(
                    [
                        str(x)
                        for x in rdf["supplier_name"].dropna().unique()
                    ]
                )
                if "supplier_name" in rdf
                else ["All"]
            )

            selected_supplier = st.selectbox(
                "Supplier",
                suppliers,
            )

        # -----------------------------------------------------
        # Apply filters
        # -----------------------------------------------------

        filtered = rdf.copy()

        if (
            selected_level != "All"
            and "risk_level" in filtered
        ):
            filtered = filtered[
                filtered["risk_level"] == selected_level
            ]

        if (
            selected_risk_type != "All"
            and "risk_type" in filtered
        ):
            filtered = filtered[
                filtered["risk_type"] == selected_risk_type
            ]

        if (
            selected_product != "All"
            and "product_name" in filtered
        ):
            filtered = filtered[
                filtered["product_name"] == selected_product
            ]

        if (
            selected_supplier != "All"
            and "supplier_name" in filtered
        ):
            filtered = filtered[
                filtered["supplier_name"] == selected_supplier
            ]

        # -----------------------------------------------------
        # Operational queue
        # -----------------------------------------------------

        st.markdown(
            f'<div class="section-title">'
            f'Operational exception queue · '
            f'{len(filtered)} result(s)'
            f'</div>',
            unsafe_allow_html=True,
        )

        if filtered.empty:

            st.markdown(
                '<div class="panel empty-state">'
                '<div class="empty-state-title">'
                'No matching risks'
                '</div>'
                '<div class="empty-state-text">'
                'Adjust the filters to inspect another operational condition.'
                '</div></div>',
                unsafe_allow_html=True,
            )

        else:

            for _, row in filtered.sort_values(
                "risk_score",
                ascending=False,
            ).iterrows():

                render_risk_card(
                    row.to_dict()
                )

        # -----------------------------------------------------
        # Risk registry
        # -----------------------------------------------------

        with st.expander(
            "View risk registry data"
        ):

            st.dataframe(
                filtered,
                use_container_width=True,
                hide_index=True,
            )

            st.download_button(
                label="⬇️ Download Risk Center CSV",
                data=filtered.to_csv(
                    index=False
                ).encode("utf-8"),
                file_name="supplysync_risk_center.csv",
                mime="text/csv",
                use_container_width=True,
                key="download_risk_center_csv",
            )

# ============================================================
# PAGE 3 — REPLENISHMENT
# ============================================================

elif selected_page == "📦  Replenishment":
    render_page_header(
        "PROCUREMENT INTELLIGENCE",
        "Replenishment",
        "Turn inventory exposure into prioritized purchase recommendations using the existing SupplySync decision engine.",
        "ACTION ENGINE",
        "Recommendations",
    )
    try:
        replenishment_data = as_records(get_replenishment_recommendations())
    except Exception as e:
        st.error("Unable to load replenishment recommendations from PostgreSQL.")
        st.caption(f"Technical detail: {str(e)}")
        st.stop()

    if not replenishment_data:
        st.markdown(
            '<div class="panel empty-state"><div class="empty-state-title">Inventory position is currently stable</div>'
            '<div class="empty-state-text">No products require procurement action at the current thresholds.</div></div>',
            unsafe_allow_html=True,
        )
    else:
        rdf = pd.DataFrame(replenishment_data)

        # Use only fields that are actually returned by the decision engine.
        total_qty = (
            pd.to_numeric(rdf["recommended_order_qty"], errors="coerce")
            .fillna(0)
            .sum()
            if "recommended_order_qty" in rdf
            else 0
        )
        total_cost = (
            pd.to_numeric(rdf["estimated_cost"], errors="coerce")
            .fillna(0)
            .sum()
            if "estimated_cost" in rdf
            else 0
        )
        critical = (
            int((rdf["risk_level"] == "Critical").sum())
            if "risk_level" in rdf
            else 0
        )
        high = (
            int((rdf["risk_level"] == "High").sum())
            if "risk_level" in rdf
            else 0
        )

        # Build display-only aliases. This does not modify the database data.
        rdf["_display_product"] = rdf.apply(
            lambda row: str(
                _first_present(
                    row.to_dict(),
                    "product_name",
                    "item_name",
                    "reference_id",
                    default="Unknown item",
                )
            ),
            axis=1,
        )
        rdf["_display_supplier"] = rdf.apply(
            lambda row: str(
                _first_present(
                    row.to_dict(),
                    "supplier_name",
                    "recommended_supplier_name",
                    default="Supplier not assigned",
                )
            ),
            axis=1,
        )

        p1, p2, p3, p4 = st.columns(4, gap="medium")
        with p1:
            render_kpi("SKUs to replenish", len(rdf), "Procurement queue")
        with p2:
            render_kpi("Recommended units", f"{int(total_qty):,}", "Current decision output")
        with p3:
            render_kpi("Estimated cost", money_inr(total_cost), "Recommendation value")
        with p4:
            render_kpi(
                "Critical SKUs",
                critical,
                f"{high} additional high-risk",
                alert=critical > 0,
            )

        st.markdown(
            '<div class="section-title">Top procurement priority</div>'
            '<div class="section-caption">The first recommendation is surfaced as an operational decision, not just a row in a table.</div>',
            unsafe_allow_html=True,
        )

        sort_col = "risk_score" if "risk_score" in rdf.columns else "priority"
        if sort_col == "risk_score":
            rdf["_sort_score"] = pd.to_numeric(
                rdf["risk_score"], errors="coerce"
            ).fillna(0)
            top = rdf.sort_values("_sort_score", ascending=False).iloc[0]
        else:
            top = rdf.iloc[0]

        top_dict = top.to_dict()
        top_product = _first_present(
            top_dict,
            "_display_product",
            "product_name",
            "item_name",
            "reference_id",
            default="Unknown item",
        )
        top_supplier = _first_present(
            top_dict,
            "_display_supplier",
            "supplier_name",
            "recommended_supplier_name",
            default="Supplier not assigned",
        )
        top_score = _display_number(top_dict.get("risk_score"))
        top_level = str(top_dict.get("risk_level") or top_dict.get("priority") or "Review")
        top_order_qty = _display_number(top_dict.get("recommended_order_qty"))
        top_cost = money_inr(top_dict.get("estimated_cost", 0))

        # These fields are optional in the current decision query. Display
        # an em dash when they are not returned instead of inventing zeroes.
        top_available = _display_number(top_dict.get("available_qty"))
        top_reorder = _display_number(top_dict.get("reorder_point_qty"))

        st.markdown(
            f'<div class="procurement-hero">'
            f'<div class="procurement-eyebrow">Priority {top_score} · {top_level.upper()}</div>'
            f'<div class="procurement-product">{top_product}</div>'
            f'<div class="procurement-supplier">Preferred supplier · {top_supplier}</div>'
            f'<div style="display:flex;gap:40px;flex-wrap:wrap;">'
            f'<div><div class="procurement-label">Current stock</div><div class="procurement-number">{top_available}</div></div>'
            f'<div><div class="procurement-label">Reorder point</div><div class="procurement-number">{top_reorder}</div></div>'
            f'<div><div class="procurement-label">Recommended order</div><div class="procurement-number">{top_order_qty}</div></div>'
            f'<div><div class="procurement-label">Estimated cost</div><div class="procurement-number">{top_cost}</div></div>'
            f'</div></div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            '<div class="section-title">Procurement filters</div>'
            '<div class="section-caption">Review the recommendation queue by operational priority.</div>',
            unsafe_allow_html=True,
        )

        f1, f2, f3 = st.columns(3)

        with f1:
            risk_options = (
                ["All"] + sorted(rdf["risk_level"].astype(str).unique().tolist())
                if "risk_level" in rdf
                else ["All"]
            )
            sel_risk = st.selectbox("Risk level", risk_options)

        with f2:
            product_options = ["All"] + sorted(
                rdf["_display_product"].astype(str).unique().tolist()
            )
            sel_product = st.selectbox("Product / reference", product_options)

        with f3:
            supplier_options = ["All"] + sorted(
                rdf["_display_supplier"].astype(str).unique().tolist()
            )
            sel_supplier = st.selectbox("Supplier", supplier_options)

        filtered = rdf.copy()

        if sel_risk != "All" and "risk_level" in filtered:
            filtered = filtered[filtered["risk_level"].astype(str) == sel_risk]

        if sel_product != "All":
            filtered = filtered[filtered["_display_product"] == sel_product]

        if sel_supplier != "All":
            filtered = filtered[filtered["_display_supplier"] == sel_supplier]

        st.markdown(
            f'<div class="section-title">Recommended procurement · {len(filtered)} result(s)</div>',
            unsafe_allow_html=True,
        )

        if filtered.empty:
            st.info("No recommendations match the selected filters.")
        else:
            for _, item in filtered.sort_values(
                "_sort_score" if "_sort_score" in filtered else "recommended_order_qty",
                ascending=False,
            ).iterrows():
                item_dict = item.to_dict()
                level = str(item_dict.get("risk_level", "Low"))
                card_cls, badge_cls = risk_class(level)

                product = _first_present(
                    item_dict,
                    "_display_product",
                    "product_name",
                    "item_name",
                    "reference_id",
                    default="Unknown item",
                )
                supplier = _first_present(
                    item_dict,
                    "_display_supplier",
                    "supplier_name",
                    "recommended_supplier_name",
                    default="Supplier not assigned",
                )
                category = _first_present(
                    item_dict,
                    "category",
                    "reference_type",
                    default="Replenishment",
                )
                current_stock = _display_number(item_dict.get("available_qty"))
                reorder_point = _display_number(item_dict.get("reorder_point_qty"))
                order_qty = _display_number(item_dict.get("recommended_order_qty"))
                lead_time = _display_number(item_dict.get("lead_time_days"), " days")
                estimated_cost = money_inr(item_dict.get("estimated_cost", 0))

                rationale = _first_present(
                    item_dict,
                    "rationale",
                    "recommended_action",
                    default="Review the current replenishment recommendation.",
                )

                st.markdown(
                    f'<div class="{card_cls}">'
                    f'<div style="display:flex;justify-content:space-between;align-items:flex-start;gap:12px;">'
                    f'<div><div class="risk-title">{product}</div>'
                    f'<div class="risk-subtitle">{supplier} · {category}</div></div>'
                    f'<span class="risk-badge {badge_cls}">{level.upper()} · {_display_number(item_dict.get("risk_score"))}</span>'
                    f'</div>'
                    f'<div style="display:flex;gap:25px;flex-wrap:wrap;margin-top:11px;">'
                    f'<div><div class="risk-metric-label">Current stock</div><div class="risk-metric-value">{current_stock}</div></div>'
                    f'<div><div class="risk-metric-label">Reorder point</div><div class="risk-metric-value">{reorder_point}</div></div>'
                    f'<div><div class="risk-metric-label">Order quantity</div><div class="risk-metric-value">{order_qty}</div></div>'
                    f'<div><div class="risk-metric-label">Lead time</div><div class="risk-metric-value">{lead_time}</div></div>'
                    f'<div><div class="risk-metric-label">Estimated cost</div><div class="risk-metric-value">{estimated_cost}</div></div>'
                    f'</div>'
                    f'<div class="reason-box"><b>Why replenish now</b><br>{rationale}</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

        with st.expander("View complete recommendation dataset"):
            # Hide only internal display helper columns from the raw-data view.
            display_df = filtered.drop(
                columns=[c for c in ["_display_product", "_display_supplier", "_sort_score"] if c in filtered.columns],
                errors="ignore",
            )
            st.dataframe(display_df, use_container_width=True, hide_index=True)

            st.download_button(
                label="⬇️ Download Replenishment CSV",
                data=display_df.to_csv(index=False).encode("utf-8"),
                file_name="supplysync_replenishment_recommendations.csv",
                mime="text/csv",
                use_container_width=True,
                key="download_replenishment_csv",
            )


# ============================================================
# PAGE 4 — DATA INGESTION
# ============================================================

elif selected_page == "📤  Data Ingestion":
    render_page_header(
        "DATA ENGINE",
        "Data Ingestion",
        "Bring new operational CSV data into SupplySync through validation, duplicate protection, PostgreSQL loading and audit logging.",
        "PIPELINE",
        "Ready",
    )

    st.markdown(
        '<div class="section-title">Ingestion flow</div><div class="section-caption">No database change occurs until the uploaded dataset passes the SupplySync data contract.</div>',
        unsafe_allow_html=True,
    )

    s1, s2, s3, s4, s5 = st.columns(5, gap="small")
    steps = [
        (s1, "01", "Receive", "CSV uploaded"),
        (s2, "02", "Validate", "Schema + values"),
        (s3, "03", "Protect", "Duplicates"),
        (s4, "04", "Load", "PostgreSQL"),
        (s5, "05", "Audit", "Ingestion log"),
    ]

    for col, num, title, sub in steps:
        with col:
            st.markdown(
                f'<div class="ingest-step"><div class="ingest-dot"></div><div><div class="ingest-step-text">{num} · {title}</div><div class="ingest-step-sub">{sub}</div></div></div>',
                unsafe_allow_html=True,
            )

    try:
        latest_ingestion = get_latest_ingestion()
    except Exception:
        latest_ingestion = None

    if latest_ingestion and latest_ingestion.get("status") == "SUCCESS":
        latest_time = latest_ingestion.get("uploaded_at")
        time_text = (
            latest_time.strftime("%d %b %Y, %H:%M")
            if hasattr(latest_time, "strftime")
            else str(latest_time)
        )

        st.markdown(
            f'<div class="panel" style="margin-top:10px;"><div class="panel-title">LATEST SUCCESSFUL UPDATE</div><div style="color:#1E293B;font-size:.9rem;font-weight:800;margin-top:5px;">{latest_ingestion.get("dataset", "Unknown dataset")}</div><div class="panel-subtitle">{time_text} · {int(latest_ingestion.get("received_rows", 0)):,} rows received</div></div>',
            unsafe_allow_html=True,
        )

    # --------------------------------------------------------
    # RECENT INGESTION HISTORY
    # --------------------------------------------------------

    try:
        ingestion_history = get_ingestion_history(limit=20)
    except Exception as history_exc:
        ingestion_history = []
        st.warning(f"Unable to load ingestion history: {history_exc}")

    st.markdown(
        '<div class="section-title">Recent sync history</div>'
        '<div class="section-caption">'
        'Recent CSV-to-PostgreSQL synchronization events recorded by SupplySync.'
        '</div>',
        unsafe_allow_html=True,
    )

    if ingestion_history:
        history_df = pd.DataFrame(ingestion_history)

        history_df = history_df.rename(
            columns={
                "id": "ID",
                "dataset": "Dataset",
                "uploaded_at": "Time",
                "received_rows": "Received",
                "validated_rows": "Validated",
                "inserted_rows": "Inserted",
                "updated_rows": "Updated",
                "skipped_rows": "Skipped",
                "status": "Status",
            }
        )

        if "Time" in history_df.columns:
            history_df["Time"] = pd.to_datetime(
                history_df["Time"]
            ).dt.strftime("%d %b %Y, %H:%M")

        st.dataframe(
            history_df,
            use_container_width=True,
            hide_index=True,
        )

    else:
        st.info("No ingestion history is available yet.")

    st.markdown(
        '<div class="section-title">Upload operational dataset</div><div class="section-caption">SupplySync can now validate and load supported operational datasets directly into the plastic supply-chain PostgreSQL schema.</div>',
        unsafe_allow_html=True,
    )

    uploaded_file = st.file_uploader(
        "Choose a CSV file",
        type=["csv"],
        key="supplysync_csv_upload",
    )

    if uploaded_file is None:
        st.markdown(
            '<div class="panel empty-state"><div class="empty-state-title">Ready for upload</div><div class="empty-state-text">Upload a supported SupplySync CSV to begin validation.</div></div>',
            unsafe_allow_html=True,
        )

    else:
        try:
            uploaded_df = pd.read_csv(uploaded_file)

            # --------------------------------------------------------
            # DATASET DETECTION
            # --------------------------------------------------------
            schemas = get_supported_upload_schemas()
            matched_dataset = detect_plastic_dataset(uploaded_df.columns)

            row_count = len(uploaded_df)
            column_count = len(uploaded_df.columns)
            duplicate_rows = int(uploaded_df.duplicated().sum())
            missing_cells = int(uploaded_df.isna().sum().sum())

            c1, c2, c3, c4 = st.columns(4, gap="medium")

            with c1:
                render_kpi(
                    "Rows received",
                    f"{row_count:,}",
                    "Uploaded file",
                )

            with c2:
                render_kpi(
                    "Columns",
                    f"{column_count:,}",
                    "Detected fields",
                )

            with c3:
                render_kpi(
                    "Exact duplicates",
                    f"{duplicate_rows:,}",
                    "Handled by duplicate protection",
                )

            with c4:
                render_kpi(
                    "Missing cells",
                    f"{missing_cells:,}",
                    "Informational check",
                    alert=missing_cells > 0,
                )

            # --------------------------------------------------------
            # DATASET DETECTED
            # --------------------------------------------------------
            if matched_dataset:
                st.markdown(
                    f'<div class="panel" style="margin-top:10px;"><div class="panel-title">DATASET DETECTED</div><div style="color:#1E293B;font-size:.9rem;font-weight:800;margin-top:5px;">{matched_dataset}</div><div class="panel-subtitle">The uploaded columns match the PostgreSQL data contract for plastic.{matched_dataset}.</div></div>',
                    unsafe_allow_html=True,
                )

                # ----------------------------------------------------
                # VALIDATION
                # ----------------------------------------------------
                try:
                    validation = validate_plastic_upload(
                        matched_dataset,
                        uploaded_df,
                    )

                    validation_ok = validation.get("valid", False)
                    validation_errors = validation.get("errors", [])
                    validation_warnings = validation.get("warnings", [])

                except Exception as validation_exc:
                    validation_ok = False
                    validation_errors = [str(validation_exc)]
                    validation_warnings = []

                st.markdown(
                    '<div class="section-title">Validation result</div>',
                    unsafe_allow_html=True,
                )

                if validation_ok:
                    st.success(
                        "Dataset passed the SupplySync validation contract."
                    )

                else:
                    st.error(
                        "Dataset failed validation. No database changes have been made."
                    )

                    for error in validation_errors:
                        st.warning(str(error))

                for warning in validation_warnings:
                    st.info(str(warning))

                # ----------------------------------------------------
                # DATABASE ACTION
                # ----------------------------------------------------
                if validation_ok:
                    st.markdown(
                        '<div class="section-title">Database action</div><div class="section-caption">The validated dataset will be loaded into the matching table inside the plastic schema. Existing records are protected from accidental duplication.</div>',
                        unsafe_allow_html=True,
                    )

                    load_label = (
                        f"Load {matched_dataset} to PostgreSQL"
                    )

                    if st.button(
                        load_label,
                        type="primary",
                        use_container_width=True,
                    ):
                        try:
                            with st.spinner(
                                f"Validating and updating plastic.{matched_dataset}..."
                            ):
                                result = load_plastic_table_data(
                                    matched_dataset,
                                    uploaded_df,
                                )

                            # ----------------------------------------
                            # AUDIT LOG
                            # ----------------------------------------
                            audit_error = None

                            try:
                                log_ingestion(
                                    dataset=result.get(
                                        "dataset",
                                        matched_dataset,
                                    ),
                                    received_rows=result.get(
                                        "received",
                                        0,
                                    ),
                                    validated_rows=result.get(
                                        "validated",
                                        0,
                                    ),
                                    inserted_rows=result.get(
                                        "inserted",
                                        0,
                                    ),
                                    updated_rows=result.get(
                                        "updated",
                                        0,
                                    ),
                                    skipped_rows=result.get(
                                        "skipped",
                                        0,
                                    ),
                                    status="SUCCESS",
                                )

                            except Exception as audit_exc:
                                audit_error = str(audit_exc)

                            st.success(
                                f"{matched_dataset} uploaded successfully to PostgreSQL."
                            )

                            summary = [
                                f'Received: {result.get("received", 0):,}',
                                f'Validated: {result.get("validated", 0):,}',
                                f'Inserted: {result.get("inserted", 0):,}',
                                f'Updated: {result.get("updated", 0):,}',
                                f'Skipped: {result.get("skipped", 0):,}',
                            ]

                            if "duplicate_rows_in_file" in result:
                                summary.append(
                                    f'Duplicates removed: {result.get("duplicate_rows_in_file", 0):,}'
                                )

                            if "duplicate_primary_keys_in_file" in result:
                                summary.append(
                                    f'Duplicate keys resolved: {result.get("duplicate_primary_keys_in_file", 0):,}'
                                )

                            st.info("  |  ".join(summary))

                            if audit_error:
                                st.warning(
                                    "Data was loaded successfully, but the ingestion audit log could not be updated."
                                )
                                st.caption(
                                    f"Audit detail: {audit_error}"
                                )
                            else:
                                st.toast(
                                    "Database and ingestion audit updated",
                                    icon="✅",
                                )

                        except Exception as e:
                            st.error(
                                "SupplySync could not load the file into PostgreSQL."
                            )
                            st.caption(
                                f"Technical detail: {str(e)}"
                            )

            else:
                st.error(
                    "Unsupported dataset structure. No database changes have been made."
                )
                st.caption(
                    "Upload a CSV whose columns match one of the supported SupplySync PostgreSQL tables."
                )

            # --------------------------------------------------------
            # COLUMN REVIEW
            # --------------------------------------------------------
            st.markdown(
                '<div class="section-title">Column review</div>',
                unsafe_allow_html=True,
            )

            column_df = pd.DataFrame(
                {
                    "Column": uploaded_df.columns,
                    "Data Type": [
                        str(uploaded_df[c].dtype)
                        for c in uploaded_df.columns
                    ],
                    "Missing Values": [
                        int(uploaded_df[c].isna().sum())
                        for c in uploaded_df.columns
                    ],
                }
            )

            st.dataframe(
                column_df,
                use_container_width=True,
                hide_index=True,
            )

            # --------------------------------------------------------
            # DATA PREVIEW
            # --------------------------------------------------------
            st.markdown(
                '<div class="section-title">Data preview</div><div class="section-caption">First 10 records only. The uploaded file remains unchanged.</div>',
                unsafe_allow_html=True,
            )

            st.dataframe(
                uploaded_df.head(10),
                use_container_width=True,
                hide_index=True,
            )

        except Exception as e:
            st.error(
                "SupplySync could not read this CSV file."
            )
            st.caption(
                f"Technical detail: {str(e)}"
            )
            
# ============================================================
# PAGE 5 — ASK SUPPLYSYNC
# ============================================================

elif selected_page == "🤖  Ask SupplySync":
    render_page_header(
        "DECISION INTELLIGENCE",
        "Ask SupplySync 🤖",
        "Use natural language to interrogate the supply-chain decision engine. Responses are grounded in retrieved PostgreSQL evidence.",
        "AI GROUNDING",
        "PostgreSQL + Gemini",
    )
    st.markdown('<div class="ai-hero"><div class="ai-eyebrow">SUPPLYSYNC AI</div><div class="ai-title">Your supply-chain decision analyst</div><div class="ai-subtitle">Ask about inventory, stockout exposure, suppliers, demand, OTIF or replenishment. SupplySync retrieves the relevant database evidence before Gemini generates the explanation.</div><div class="ai-status">● Grounded analysis · PostgreSQL evidence</div></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Suggested operational questions</div><div class="section-caption">Choose a decision question or write your own.</div>', unsafe_allow_html=True)
    q1, q2, q3 = st.columns(3, gap="medium")
    with q1:
        if st.button("Which products should I reorder?", use_container_width=True):
            st.session_state["ai_question"] = "Which products should I reorder?"
    with q2:
        if st.button("Which products are at risk of stockout?", use_container_width=True):
            st.session_state["ai_question"] = "Which products are at risk of stockout?"
    with q3:
        if st.button("Which suppliers need attention?", use_container_width=True):
            st.session_state["ai_question"] = "Which suppliers need attention?"
    question = st.text_area("Business question", value=st.session_state.get("ai_question", ""), placeholder="Example: Why is OTIF underperforming and what should I focus on?", height=105)
    ask1, ask2 = st.columns([1.2, 4.8], gap="medium")
    with ask1:
        ask_button = st.button("Analyze with SupplySync", type="primary", use_container_width=True)
    with ask2:
        st.caption("The AI does not receive arbitrary data. SupplySync first selects the relevant analytics tool and passes the returned evidence to the model.")
    if ask_button:
        if not question.strip():
            st.warning("Enter a supply-chain question first.")
        else:
            try:
                with st.spinner("Retrieving evidence and generating analysis..."):
                    result = ask_supplysync(question.strip())
                st.session_state["ai_result"] = result
                st.session_state["ai_question"] = question.strip()
            except Exception as e:
                st.error("SupplySync could not complete the analysis.")
                st.caption(f"Technical detail: {str(e)}")
    if "ai_result" in st.session_state:
        result = st.session_state["ai_result"]
        st.markdown('<div class="section-title">Decision analysis</div><div class="section-caption">AI-generated interpretation grounded in the retrieved SupplySync evidence.</div>', unsafe_allow_html=True)
        answer = result.get("answer", "No analysis returned.") if isinstance(result, dict) else str(result)
        st.markdown(f'<div class="ai-answer"><div class="panel-title">SUPPLYSYNC RECOMMENDATION</div><div style="margin-top:9px;color:#1E293B;font-size:.86rem;line-height:1.6;">{answer}</div></div>', unsafe_allow_html=True)
        meta1, meta2 = st.columns(2, gap="medium")
        with meta1:
            intent = str(result.get("intent", "General analysis")).replace("_", " ").title() if isinstance(result, dict) else "General analysis"
            st.markdown(f'<div class="panel"><div class="panel-title">ANALYSIS TYPE</div><div style="color:#1E293B;font-size:.84rem;font-weight:800;margin-top:5px;">{intent}</div></div>', unsafe_allow_html=True)
        with meta2:
            tool = str(result.get("tool", "SupplySync analytics")).replace("_", " ").title() if isinstance(result, dict) else "SupplySync analytics"
            st.markdown(f'<div class="panel"><div class="panel-title">EVIDENCE TOOL</div><div style="color:#1E293B;font-size:.84rem;font-weight:800;margin-top:5px;">{tool}</div></div>', unsafe_allow_html=True)
        evidence = result.get("evidence") if isinstance(result, dict) else None
        if evidence:
            with st.expander("View evidence used for this analysis"):
                st.caption("These records were retrieved by SupplySync and supplied as evidence for the AI response.")
                st.dataframe(pd.DataFrame(evidence), use_container_width=True, hide_index=True)

