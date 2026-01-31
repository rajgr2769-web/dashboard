import streamlit as st
import pandas as pd
from datetime import timedelta
import os

from engine.revenue_metrics import (
    prepare_revenue_data,
    compute_revenue_metrics,
    compute_revenue_changes
)
from engine.revenue_risk import revenue_signals


# =====================================================
# PAGE CONFIG
# =====================================================
st.set_page_config(
    page_title="Arista Vault – Revenue Command",
    layout="wide"
)


# =====================================================
# 🔐 AUTHENTICATION (FOUNDER ONLY)
# =====================================================
APP_PASSWORD = os.getenv("DASHBOARD_PASSWORD")

if APP_PASSWORD is None:
    st.error("Password not configured. Contact admin.")
    st.stop()

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title(" Restricted Access")
    st.caption("Confidential revenue dashboard")

    password = st.text_input("Enter access password", type="password")

    if st.button("Login"):
        if password == APP_PASSWORD:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Invalid password")

    st.stop()


# =====================================================
# DATA LOAD
# =====================================================
@st.cache_data
def load_data():
    df = pd.read_csv("data/orders_by_date.csv")
    df = prepare_revenue_data(df)

    # Enforce last 30 days
    max_date = df["day"].max()
    df = df[df["day"] >= max_date - timedelta(days=30)]

    return df


def signal(pct):
    if pct is None:
        return "N/A", "⚪"
    if pct <= -10:
        return f"{pct}%", "🔴"
    elif pct < 0:
        return f"{pct}%", "🟡"
    else:
        return f"{pct}%", "🟢"


# =====================================================
# COMPUTE METRICS
# =====================================================
df = load_data()

metrics = compute_revenue_metrics(df)
changes = compute_revenue_changes(df)
alerts, discount_pct, discount_roi = revenue_signals(metrics)

wow, wow_icon = signal(changes.get("wow_pct"))
mom, mom_icon = signal(changes.get("mom_pct"))
aov_wow, aov_icon = signal(changes.get("aov_wow"))


# =====================================================
# UI
# =====================================================
st.title(" Arista Vault – Revenue Command Dashboard")
st.caption("Founder Money View · Last 30 Days · Net Revenue First")


# KPIs
c1, c2, c3, c4, c5 = st.columns(5)

c1.metric("Net Revenue", f"₹{int(metrics['total_net']):,}")
c2.metric("WoW Revenue", wow, wow_icon)
c3.metric("MoM Revenue", mom, mom_icon)
c4.metric("Orders", metrics["orders"])
c5.metric(
    "Run Rate (Monthly)",
    f"₹{int(changes['run_rate']):,}" if changes.get("run_rate") else "N/A"
)

st.metric("AOV (Net)", f"₹{metrics['aov']:,}", aov_wow)

st.divider()


# =====================================================
# EXECUTIVE SUMMARY
# =====================================================
st.subheader("🧠 Executive Summary – What Changed vs Previous Day")

day_delta = changes.get("day_delta")
latest_day = changes.get("latest_day")

if day_delta is not None and latest_day is not None:
    arrow = "⬆️" if day_delta > 0 else "⬇️"
    st.info(
        f"Net revenue changed by **₹{abs(int(day_delta)):,} {arrow}** "
        f"compared to {latest_day.date()}."
    )
else:
    st.info("Not enough data to compute daily change.")

st.divider()


# =====================================================
# REVENUE TREND
# =====================================================
st.subheader("📈 Net Revenue Trend (Last 30 Days)")
st.line_chart(metrics["revenue_by_day"])

st.divider()


# =====================================================
# REVENUE CONCENTRATION
# =====================================================
st.subheader("⚠️ Revenue Concentration")

st.write(
    f"""
- **Top 1 Product:** {metrics['top_1']}%  
- **Top 3 Products:** {metrics['top_3']}%  
- **Top 5 Products:** {metrics['top_5']}%
"""
)

st.bar_chart(metrics["revenue_by_product"].head(10))

st.divider()


# =====================================================
# DISCOUNT EFFICIENCY
# =====================================================
st.subheader("🏷️ Discount Efficiency")

st.write(f"**Discount %:** {discount_pct}%")

if discount_roi:
    st.write(f"**Discount ROI:** ₹{discount_roi} revenue per ₹1 discount")
else:
    st.write("**Discount ROI:** N/A")

discount_table = metrics["discount_by_product"].copy()

discount_table["discount_ratio_%"] = round(
    discount_table["discounts"] /
    (discount_table["net sales"] + discount_table["discounts"]) * 100,
    2
)

st.table(
    discount_table
    .sort_values("discount_ratio_%", ascending=False)
    .head(10)
)

st.divider()


# =====================================================
# NEW vs REPEAT (PROXY)
# =====================================================
st.subheader("🔁 New vs Repeat Revenue")
st.caption("Proxy based on order value distribution (not customer identity)")

st.bar_chart({
    "New Revenue": metrics["new_revenue"],
    "Repeat Revenue": metrics["repeat_revenue"]
})

st.divider()


# =====================================================
# FOUNDER ALERTS
# =====================================================
st.subheader("🚨 Founder Signals")

if alerts:
    for alert in alerts:
        st.warning(alert)
else:
    st.success("No critical revenue risks detected.")
