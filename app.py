"""
B2B Order Processing Analytics Dashboard
Part C: Streamlit Interactive Dashboard
Course: Applied Programming Tools for B2B Business
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import os

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="B2B Order Analytics Dashboard",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# CUSTOM CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
    /* Main background */
    .main { background-color: #0f1117; }

    /* KPI card style */
    .kpi-card {
        background: linear-gradient(135deg, #1e2130, #252840);
        border-radius: 12px;
        padding: 20px 24px;
        border-left: 4px solid;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        margin-bottom: 8px;
    }
    .kpi-card h3 {
        margin: 0;
        font-size: 13px;
        color: #9aa0b4;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-weight: 500;
    }
    .kpi-card .value {
        font-size: 36px;
        font-weight: 700;
        color: #ffffff;
        margin: 6px 0 2px 0;
        line-height: 1.1;
    }
    .kpi-card .delta {
        font-size: 12px;
        color: #9aa0b4;
    }

    /* Header */
    .dashboard-header {
        background: linear-gradient(90deg, #1a1d2e, #252840);
        border-radius: 12px;
        padding: 20px 28px;
        margin-bottom: 24px;
        border-bottom: 2px solid #3d4266;
    }
    .dashboard-header h1 {
        color: #ffffff;
        font-size: 26px;
        font-weight: 700;
        margin: 0;
    }
    .dashboard-header p {
        color: #9aa0b4;
        margin: 4px 0 0 0;
        font-size: 14px;
    }

    /* Section titles */
    .section-title {
        font-size: 16px;
        font-weight: 600;
        color: #c8cde8;
        margin: 24px 0 12px 0;
        padding-left: 4px;
        border-left: 3px solid #5c7cfa;
        padding-left: 10px;
    }

    /* Insight cards */
    .insight-card {
        background: linear-gradient(135deg, #1e2130, #252840);
        border-radius: 10px;
        padding: 16px 20px;
        margin-bottom: 12px;
        border-left: 3px solid;
    }
    .insight-card h4 {
        color: #ffffff;
        font-size: 14px;
        margin: 0 0 6px 0;
    }
    .insight-card p {
        color: #9aa0b4;
        font-size: 13px;
        margin: 0;
        line-height: 1.5;
    }

    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: #13151f;
    }
    section[data-testid="stSidebar"] .stMultiSelect label,
    section[data-testid="stSidebar"] .stSelectbox label {
        color: #c8cde8 !important;
        font-size: 13px;
    }

    /* Plotly chart containers */
    .plot-container { border-radius: 12px; overflow: hidden; }

    /* Remove default streamlit padding */
    .block-container { padding-top: 1.5rem; padding-bottom: 1rem; }

    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        background-color: #1e2130;
        border-radius: 10px;
        padding: 4px;
    }
    .stTabs [data-baseweb="tab"] {
        color: #9aa0b4;
        border-radius: 8px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #5c7cfa !important;
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# DATA LOADING
# ─────────────────────────────────────────────
@st.cache_data
def load_data():
    # Resolve dataset path relative to this script file
    base_dir = os.path.dirname(os.path.abspath(__file__))
    filename = "B2B_Order_Dataset.xlsx"

    possible_paths = [
        os.path.join(base_dir, filename),          # same folder as app.py  ✅
        filename,                                   # cwd fallback
        os.path.join(os.getcwd(), filename),        # explicit cwd
    ]

    df = None
    for path in possible_paths:
        if os.path.exists(path):
            df = pd.read_excel(path)
            break

    if df is None:
        st.error(
            f"⚠️ Dataset not found.\n\n"
            f"Looked in:\n" + "\n".join(f"- `{p}`" for p in possible_paths) +
            f"\n\nPlease ensure `{filename}` is in the **same folder** as `app.py`."
        )
        st.stop()

    df["Order_Date"] = pd.to_datetime(df["Order_Date"])
    df["Delivery_Date"] = pd.to_datetime(df["Delivery_Date"])
    df["Delivery_Time"] = (df["Delivery_Date"] - df["Order_Date"]).dt.days
    df["Month"] = df["Order_Date"].dt.to_period("M").astype(str)
    df["Month_dt"] = df["Order_Date"].dt.to_period("M").dt.to_timestamp()
    return df


df_raw = load_data()

# ─────────────────────────────────────────────
# SIDEBAR FILTERS
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🎛️ Dashboard Filters")
    st.markdown("---")

    # Region filter
    st.markdown("**📍 Region**")
    all_regions = sorted(df_raw["Region"].unique())
    sel_regions = st.multiselect(
        "Select Region(s)",
        options=all_regions,
        default=all_regions,
        label_visibility="collapsed",
    )

    st.markdown("**🏷️ Product Category**")
    all_cats = sorted(df_raw["Product_Category"].unique())
    sel_cats = st.multiselect(
        "Select Category(ies)",
        options=all_cats,
        default=all_cats,
        label_visibility="collapsed",
    )

    st.markdown("**📋 Order Status**")
    all_statuses = sorted(df_raw["Status"].unique())
    sel_statuses = st.multiselect(
        "Select Status(es)",
        options=all_statuses,
        default=all_statuses,
        label_visibility="collapsed",
    )

    st.markdown("---")

    # Date range
    st.markdown("**📅 Date Range**")
    min_date = df_raw["Order_Date"].min().date()
    max_date = df_raw["Order_Date"].max().date()
    date_range = st.date_input(
        "Order Date",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
        label_visibility="collapsed",
    )

    st.markdown("---")
    st.markdown(
        "<small style='color:#666'>📦 B2B Order Analytics<br>End Term Project Dashboard</small>",
        unsafe_allow_html=True,
    )

# ─────────────────────────────────────────────
# APPLY FILTERS
# ─────────────────────────────────────────────
df = df_raw.copy()

if sel_regions:
    df = df[df["Region"].isin(sel_regions)]
if sel_cats:
    df = df[df["Product_Category"].isin(sel_cats)]
if sel_statuses:
    df = df[df["Status"].isin(sel_statuses)]
if len(date_range) == 2:
    df = df[
        (df["Order_Date"].dt.date >= date_range[0])
        & (df["Order_Date"].dt.date <= date_range[1])
    ]

# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
st.markdown("""
<div class="dashboard-header">
    <h1>📦 B2B Order Processing Analytics Dashboard</h1>
    <p>Real-time monitoring of order fulfillment, delivery performance, and business insights</p>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["📊 Overview & KPIs", "📈 Deep Dive Analysis", "💡 Business Insights"])

# ══════════════════════════════════════════
# TAB 1 — OVERVIEW & KPIs
# ══════════════════════════════════════════
with tab1:

    # ── KPI CARDS ──────────────────────────
    st.markdown('<div class="section-title">Key Performance Indicators</div>', unsafe_allow_html=True)

    total_orders = len(df)
    completed = (df["Status"] == "Completed").sum()
    pending = (df["Status"] == "Pending").sum()
    delayed = (df["Status"] == "Delayed").sum()
    avg_delivery = df["Delivery_Time"].mean()
    total_value = df["Order_Value"].sum()

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.markdown(f"""
        <div class="kpi-card" style="border-color:#5c7cfa;">
            <h3>📦 Total Orders</h3>
            <div class="value">{total_orders:,}</div>
            <div class="delta">Across all regions</div>
        </div>""", unsafe_allow_html=True)

    with col2:
        comp_pct = (completed / total_orders * 100) if total_orders else 0
        st.markdown(f"""
        <div class="kpi-card" style="border-color:#40c057;">
            <h3>✅ Completed</h3>
            <div class="value">{completed:,}</div>
            <div class="delta">{comp_pct:.1f}% completion rate</div>
        </div>""", unsafe_allow_html=True)

    with col3:
        pend_pct = (pending / total_orders * 100) if total_orders else 0
        st.markdown(f"""
        <div class="kpi-card" style="border-color:#fab005;">
            <h3>⏳ Pending</h3>
            <div class="value">{pending:,}</div>
            <div class="delta">{pend_pct:.1f}% of total orders</div>
        </div>""", unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class="kpi-card" style="border-color:#f03e3e;">
            <h3>🕐 Avg Delivery Time</h3>
            <div class="value">{avg_delivery:.1f}<span style="font-size:18px"> days</span></div>
            <div class="delta">Min: {df['Delivery_Time'].min()} | Max: {df['Delivery_Time'].max()}</div>
        </div>""", unsafe_allow_html=True)

    with col5:
        st.markdown(f"""
        <div class="kpi-card" style="border-color:#ae3ec9;">
            <h3>💰 Total Order Value</h3>
            <div class="value">₹{total_value/1e6:.2f}M</div>
            <div class="delta">Avg: ₹{df['Order_Value'].mean():,.0f} / order</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── ROW 1: Region + Status ─────────────
    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown('<div class="section-title">Orders by Region</div>', unsafe_allow_html=True)
        region_df = df.groupby("Region").agg(
            Total=("Order_ID", "count"),
            Completed=("Status", lambda x: (x == "Completed").sum()),
            Pending=("Status", lambda x: (x == "Pending").sum()),
            Delayed=("Status", lambda x: (x == "Delayed").sum()),
        ).reset_index()

        fig_region = px.bar(
            region_df,
            x="Region",
            y=["Completed", "Pending", "Delayed"],
            barmode="stack",
            color_discrete_map={"Completed": "#40c057", "Pending": "#fab005", "Delayed": "#f03e3e"},
            template="plotly_dark",
        )
        fig_region.update_layout(
            paper_bgcolor="rgba(30,33,48,0.8)",
            plot_bgcolor="rgba(30,33,48,0)",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            margin=dict(l=10, r=10, t=10, b=10),
            height=320,
            xaxis_title="",
            yaxis_title="Number of Orders",
            font=dict(color="#c8cde8"),
        )
        st.plotly_chart(fig_region, use_container_width=True)

    with col_b:
        st.markdown('<div class="section-title">Status Distribution</div>', unsafe_allow_html=True)
        status_df = df["Status"].value_counts().reset_index()
        status_df.columns = ["Status", "Count"]
        color_map = {"Completed": "#40c057", "Pending": "#fab005", "Delayed": "#f03e3e"}

        fig_pie = px.pie(
            status_df,
            names="Status",
            values="Count",
            color="Status",
            color_discrete_map=color_map,
            hole=0.55,
            template="plotly_dark",
        )
        fig_pie.update_traces(textposition="outside", textinfo="percent+label")
        fig_pie.update_layout(
            paper_bgcolor="rgba(30,33,48,0.8)",
            plot_bgcolor="rgba(30,33,48,0)",
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=-0.1, xanchor="center", x=0.5),
            margin=dict(l=10, r=10, t=10, b=30),
            height=320,
            font=dict(color="#c8cde8"),
            annotations=[dict(text=f"{total_orders}<br>Total", x=0.5, y=0.5,
                              font_size=16, showarrow=False, font_color="#fff")]
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    # ── ROW 2: Delivery Time + Order Value Trend ──
    col_c, col_d = st.columns(2)

    with col_c:
        st.markdown('<div class="section-title">Delivery Time Distribution</div>', unsafe_allow_html=True)
        fig_hist = px.histogram(
            df,
            x="Delivery_Time",
            color="Status",
            nbins=15,
            color_discrete_map=color_map,
            template="plotly_dark",
            opacity=0.85,
            barmode="overlay",
        )
        fig_hist.update_layout(
            paper_bgcolor="rgba(30,33,48,0.8)",
            plot_bgcolor="rgba(30,33,48,0)",
            margin=dict(l=10, r=10, t=10, b=10),
            height=300,
            xaxis_title="Days to Deliver",
            yaxis_title="Number of Orders",
            font=dict(color="#c8cde8"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        )
        st.plotly_chart(fig_hist, use_container_width=True)

    with col_d:
        st.markdown('<div class="section-title">Monthly Order Value Trend</div>', unsafe_allow_html=True)
        monthly = (
            df.groupby("Month_dt")["Order_Value"]
            .sum()
            .reset_index()
            .sort_values("Month_dt")
        )
        monthly["Order_Value_M"] = monthly["Order_Value"] / 1e6

        fig_line = px.area(
            monthly,
            x="Month_dt",
            y="Order_Value_M",
            template="plotly_dark",
            color_discrete_sequence=["#5c7cfa"],
        )
        fig_line.update_traces(fill="tozeroy", line_width=2.5, fillcolor="rgba(92,124,250,0.15)")
        fig_line.update_layout(
            paper_bgcolor="rgba(30,33,48,0.8)",
            plot_bgcolor="rgba(30,33,48,0)",
            margin=dict(l=10, r=10, t=10, b=10),
            height=300,
            xaxis_title="Month",
            yaxis_title="Order Value (₹ Millions)",
            font=dict(color="#c8cde8"),
        )
        st.plotly_chart(fig_line, use_container_width=True)


# ══════════════════════════════════════════
# TAB 2 — DEEP DIVE ANALYSIS
# ══════════════════════════════════════════
with tab2:

    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="section-title">Average Delivery Time by Region</div>', unsafe_allow_html=True)
        region_del = df.groupby("Region")["Delivery_Time"].mean().reset_index().sort_values("Delivery_Time", ascending=True)
        fig_hbar = px.bar(
            region_del,
            x="Delivery_Time",
            y="Region",
            orientation="h",
            color="Delivery_Time",
            color_continuous_scale="RdYlGn_r",
            template="plotly_dark",
            text=region_del["Delivery_Time"].round(1),
        )
        fig_hbar.update_traces(texttemplate="%{text} days", textposition="outside")
        fig_hbar.update_layout(
            paper_bgcolor="rgba(30,33,48,0.8)",
            plot_bgcolor="rgba(30,33,48,0)",
            coloraxis_showscale=False,
            margin=dict(l=10, r=40, t=10, b=10),
            height=280,
            xaxis_title="Avg Days",
            yaxis_title="",
            font=dict(color="#c8cde8"),
        )
        st.plotly_chart(fig_hbar, use_container_width=True)

    with col2:
        st.markdown('<div class="section-title">Order Value by Product Category</div>', unsafe_allow_html=True)
        cat_val = df.groupby("Product_Category")["Order_Value"].sum().reset_index().sort_values("Order_Value", ascending=False)
        cat_val["Order_Value_M"] = cat_val["Order_Value"] / 1e6
        fig_cat = px.bar(
            cat_val,
            x="Product_Category",
            y="Order_Value_M",
            color="Product_Category",
            template="plotly_dark",
            color_discrete_sequence=px.colors.qualitative.Pastel,
            text=cat_val["Order_Value_M"].round(2),
        )
        fig_cat.update_traces(texttemplate="₹%{text}M", textposition="outside")
        fig_cat.update_layout(
            paper_bgcolor="rgba(30,33,48,0.8)",
            plot_bgcolor="rgba(30,33,48,0)",
            showlegend=False,
            margin=dict(l=10, r=10, t=10, b=10),
            height=280,
            xaxis_title="",
            yaxis_title="Value (₹ Millions)",
            font=dict(color="#c8cde8"),
        )
        st.plotly_chart(fig_cat, use_container_width=True)

    col3, col4 = st.columns(2)

    with col3:
        st.markdown('<div class="section-title">Delivery Time by Category (Box Plot)</div>', unsafe_allow_html=True)
        fig_box = px.box(
            df,
            x="Product_Category",
            y="Delivery_Time",
            color="Product_Category",
            template="plotly_dark",
            color_discrete_sequence=px.colors.qualitative.Pastel,
        )
        fig_box.update_layout(
            paper_bgcolor="rgba(30,33,48,0.8)",
            plot_bgcolor="rgba(30,33,48,0)",
            showlegend=False,
            margin=dict(l=10, r=10, t=10, b=10),
            height=300,
            xaxis_title="",
            yaxis_title="Delivery Days",
            font=dict(color="#c8cde8"),
        )
        st.plotly_chart(fig_box, use_container_width=True)

    with col4:
        st.markdown('<div class="section-title">Region × Category Heatmap (Avg Delivery Days)</div>', unsafe_allow_html=True)
        pivot = df.pivot_table(
            values="Delivery_Time",
            index="Region",
            columns="Product_Category",
            aggfunc="mean",
        ).round(1)
        fig_heat = px.imshow(
            pivot,
            color_continuous_scale="RdYlGn_r",
            template="plotly_dark",
            text_auto=True,
            aspect="auto",
        )
        fig_heat.update_layout(
            paper_bgcolor="rgba(30,33,48,0.8)",
            margin=dict(l=10, r=10, t=10, b=10),
            height=300,
            font=dict(color="#c8cde8"),
            coloraxis_colorbar=dict(title="Days"),
        )
        st.plotly_chart(fig_heat, use_container_width=True)

    # Monthly breakdown by region
    st.markdown('<div class="section-title">Monthly Orders by Region</div>', unsafe_allow_html=True)
    monthly_region = (
        df.groupby(["Month_dt", "Region"])["Order_ID"]
        .count()
        .reset_index()
        .rename(columns={"Order_ID": "Orders"})
    )
    fig_line2 = px.line(
        monthly_region,
        x="Month_dt",
        y="Orders",
        color="Region",
        template="plotly_dark",
        markers=True,
        color_discrete_sequence=["#5c7cfa", "#40c057", "#fab005", "#f03e3e"],
    )
    fig_line2.update_layout(
        paper_bgcolor="rgba(30,33,48,0.8)",
        plot_bgcolor="rgba(30,33,48,0)",
        margin=dict(l=10, r=10, t=10, b=10),
        height=300,
        xaxis_title="Month",
        yaxis_title="Number of Orders",
        font=dict(color="#c8cde8"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    st.plotly_chart(fig_line2, use_container_width=True)

    # Scatter: Order Value vs Delivery Time
    st.markdown('<div class="section-title">Order Value vs Delivery Time (Scatter)</div>', unsafe_allow_html=True)
    fig_scatter = px.scatter(
        df.sample(min(500, len(df)), random_state=42),
        x="Delivery_Time",
        y="Order_Value",
        color="Status",
        size="Order_Value",
        hover_data=["Region", "Product_Category", "Client_Name"],
        template="plotly_dark",
        color_discrete_map={"Completed": "#40c057", "Pending": "#fab005", "Delayed": "#f03e3e"},
        opacity=0.7,
    )
    fig_scatter.update_layout(
        paper_bgcolor="rgba(30,33,48,0.8)",
        plot_bgcolor="rgba(30,33,48,0)",
        margin=dict(l=10, r=10, t=10, b=10),
        height=320,
        xaxis_title="Delivery Time (Days)",
        yaxis_title="Order Value (₹)",
        font=dict(color="#c8cde8"),
    )
    st.plotly_chart(fig_scatter, use_container_width=True)


# ══════════════════════════════════════════
# TAB 3 — BUSINESS INSIGHTS (Part D)
# ══════════════════════════════════════════
with tab3:

    st.markdown('<div class="section-title">Part D: Business Insights & Recommendations</div>', unsafe_allow_html=True)

    # Compute answers from filtered data
    region_delay = df.groupby("Region")["Delivery_Time"].mean().sort_values(ascending=False)
    worst_region = region_delay.index[0]
    worst_delay = region_delay.iloc[0]

    cat_value = df.groupby("Product_Category")["Order_Value"].sum().sort_values(ascending=False)
    top_cat = cat_value.index[0]
    top_val = cat_value.iloc[0]

    cv = df["Delivery_Time"].std() / df["Delivery_Time"].mean() * 100  # coefficient of variation
    consistency = "inconsistent" if cv > 40 else "moderately consistent" if cv > 25 else "consistent"

    # Q1
    st.markdown(f"""
    <div class="insight-card" style="border-color:#f03e3e;">
        <h4>🔴 Q1. Which region has the highest delivery delays?</h4>
        <p><strong style="color:#f03e3e;">{worst_region} Region</strong> has the highest average delivery time of
        <strong>{worst_delay:.2f} days</strong>.<br>
        Regional breakdown: {" | ".join([f"{r}: {v:.1f}d" for r, v in region_delay.items()])}<br>
        The East region consistently logs the longest fulfillment cycles, suggesting logistics or
        warehousing bottlenecks that require immediate attention.</p>
    </div>""", unsafe_allow_html=True)

    # Q2
    st.markdown(f"""
    <div class="insight-card" style="border-color:#ae3ec9;">
        <h4>💜 Q2. Which product category generates the highest order value?</h4>
        <p><strong style="color:#ae3ec9;">{top_cat}</strong> leads all categories with a total order value of
        <strong>₹{top_val/1e6:.2f} Million</strong>.<br>
        Category breakdown: {" | ".join([f"{c}: ₹{v/1e6:.2f}M" for c, v in cat_value.items()])}<br>
        Textiles and Pharma are the top two revenue drivers — strategic focus on these categories
        can maximize revenue impact.</p>
    </div>""", unsafe_allow_html=True)

    # Q3
    st.markdown(f"""
    <div class="insight-card" style="border-color:#fab005;">
        <h4>🟡 Q3. Is delivery time consistent across orders?</h4>
        <p>Delivery time is <strong style="color:#fab005;">{consistency}</strong> with a Coefficient of Variation (CV) of
        <strong>{cv:.1f}%</strong>.<br>
        Mean: {df['Delivery_Time'].mean():.1f} days | Std Dev: {df['Delivery_Time'].std():.1f} days |
        Range: {df['Delivery_Time'].min()} – {df['Delivery_Time'].max()} days<br>
        The wide spread from 1 to 15 days reveals significant variability in fulfillment,
        indicating a lack of standardized delivery SLAs across regions and product categories.</p>
    </div>""", unsafe_allow_html=True)

    # Q4 — 3 Improvements
    st.markdown('<div class="section-title" style="margin-top:28px;">🚀 3 Strategic Improvement Recommendations</div>', unsafe_allow_html=True)

    improvements = [
        {
            "icon": "🗺️",
            "color": "#5c7cfa",
            "title": "1. Region-Specific Logistics Optimization",
            "body": (
                f"The <strong>{worst_region} Region</strong> averages <strong>{worst_delay:.1f} days</strong> for delivery — "
                "the highest across all regions. Deploy dedicated regional distribution centers "
                "or partner with local 3PL providers in high-delay zones. Introduce dynamic "
                "routing algorithms that factor in traffic, distance, and carrier performance. "
                "Expected outcome: <strong>20–30% reduction in delivery time</strong> in underperforming regions."
            ),
        },
        {
            "icon": "⚙️",
            "color": "#40c057",
            "title": "2. Automate Order Confirmation & Tracking (Make.com / Zapier)",
            "body": (
                f"With <strong>{pending:,} orders currently pending</strong> ({pend_pct:.1f}% of total), "
                "delays in processing are a key risk. Implement automated workflows that: "
                "(a) trigger confirmation emails upon order creation, "
                "(b) auto-notify logistics teams for dispatch, and "
                "(c) send real-time delivery status updates to clients. "
                "This reduces manual intervention and processing delays by up to <strong>40%</strong>."
            ),
        },
        {
            "icon": "📊",
            "color": "#fab005",
            "title": "3. Delivery SLA Enforcement & Predictive Alerting",
            "body": (
                "The coefficient of variation of <strong>{:.1f}%</strong> reveals inconsistent delivery SLAs. "
                "Establish category- and region-specific SLA benchmarks (e.g., Pharma: ≤5 days, Electronics: ≤7 days). "
                "Integrate a predictive alert system that flags orders at risk of breaching SLA thresholds "
                "before they become delayed. Use ML models on historical data to predict delivery risk scores. "
                "Target: <strong>reduce delayed order rate by 35%</strong> within 2 quarters.".format(cv)
            ),
        },
    ]

    for imp in improvements:
        st.markdown(f"""
        <div class="insight-card" style="border-color:{imp['color']}; padding: 20px 24px;">
            <h4 style="font-size:15px;">{imp['icon']} {imp['title']}</h4>
            <p>{imp['body']}</p>
        </div>""", unsafe_allow_html=True)

    # Summary metrics table
    st.markdown('<div class="section-title" style="margin-top:24px;">📋 Summary Statistics Table</div>', unsafe_allow_html=True)

    summary_data = {
        "Metric": [
            "Total Orders", "Completed Orders", "Pending Orders", "Delayed Orders",
            "Completion Rate", "Avg Delivery Time", "Std Dev (Delivery)", "Highest Value Category",
            "Highest Delay Region", "Total Revenue",
        ],
        "Value": [
            f"{total_orders:,}", f"{completed:,}", f"{pending:,}", f"{delayed:,}",
            f"{comp_pct:.1f}%", f"{avg_delivery:.2f} days",
            f"{df['Delivery_Time'].std():.2f} days",
            f"{top_cat} (₹{top_val/1e6:.2f}M)",
            f"{worst_region} ({worst_delay:.2f} days)",
            f"₹{total_value/1e6:.2f} Million",
        ],
    }
    st.dataframe(
        pd.DataFrame(summary_data),
        use_container_width=True,
        hide_index=True,
    )

# ─────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<center><small style='color:#555;'>B2B Order Processing Analytics Dashboard · "
    "Applied Programming Tools for B2B Business · End Term Project</small></center>",
    unsafe_allow_html=True,
)
