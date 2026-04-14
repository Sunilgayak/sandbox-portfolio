import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import json
import os

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SandBox Portfolio Workshop",
    page_icon="📈",
    layout="wide"
)

# ── Asset classes & historical mock returns (monthly %) ───────────────────────
ASSETS = {
    "US Equities":        {"color": "#2196F3", "avg_return": 0.008},
    "European Equities":  {"color": "#4CAF50", "avg_return": 0.006},
    "Emerging Markets":   {"color": "#FF9800", "avg_return": 0.007},
    "Global Bonds":       {"color": "#9C27B0", "avg_return": 0.003},
    "Real Estate (REIT)": {"color": "#F44336", "avg_return": 0.005},
    "Gold":               {"color": "#FFD700", "avg_return": 0.004},
    "Cash":               {"color": "#607D8B", "avg_return": 0.001},
}

INITIAL_INVESTMENT = 5_000_000
TOTAL_MONTHS = 360  # 10 years
COVID_CRASH_MONTH = 46  # March 2020

# ── Generate historical data ──────────────────────────────────────────────────
@st.cache_data
def generate_historical_data():
    np.random.seed(42)
    months = range(TOTAL_MONTHS + 1)
    data = {}
    for asset, info in ASSETS.items():
        returns = []
        cumulative = 1.0
        for m in months:
            if m == 0:
                returns.append(1.0)
            else:
                # Covid crash at month 46
                if m == COVID_CRASH_MONTH:
                    shock = -0.25 if "Equities" in asset or "REIT" in asset else -0.05
                    monthly_r = shock
                elif COVID_CRASH_MONTH < m < COVID_CRASH_MONTH + 12:
                    monthly_r = np.random.normal(info["avg_return"] + 0.01, 0.03)
                else:
                    monthly_r = np.random.normal(info["avg_return"], 0.02)
                cumulative *= (1 + monthly_r)
                returns.append(round(cumulative, 6))
        data[asset] = returns
    return pd.DataFrame(data, index=list(months))

# ── Persistent storage using a simple JSON file ───────────────────────────────
DATA_FILE = "participants.json"

def load_participants():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

def save_participants(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

# ── Session state init ────────────────────────────────────────────────────────
if "username" not in st.session_state:
    st.session_state.username = None
if "page" not in st.session_state:
    st.session_state.page = "login"
if "current_month" not in st.session_state:
    st.session_state.current_month = 120  # Demo: show month 120

hist = generate_historical_data()
participants = load_participants()

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 1 — LOGIN
# ══════════════════════════════════════════════════════════════════════════════
def page_login():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("---")
        st.markdown("## 📈 SandBox Portfolio Workshop")
        st.markdown("### NextGen Investment Challenge")
        st.markdown("---")
        st.markdown("**Welcome!** You will manage a **$5,000,000** portfolio over a simulated 10-year period using real historical data.")
        st.markdown("")

        username = st.text_input("Enter your name to join:", placeholder="e.g. John Smith")

        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("🚀 Join Workshop", use_container_width=True, type="primary"):
                if username.strip():
                    st.session_state.username = username.strip()
                    if username.strip() not in participants:
                        participants[username.strip()] = {
                            "allocation": {a: 0 for a in ASSETS},
                            "validated": False,
                            "joined": datetime.now().isoformat()
                        }
                        save_participants(participants)
                    st.session_state.page = "allocation"
                    st.rerun()
                else:
                    st.error("Please enter your name!")

        with col_b:
            if st.button("👔 CIO Admin View", use_container_width=True):
                st.session_state.username = "CIO_ADMIN"
                st.session_state.page = "dashboard"
                st.rerun()

        st.markdown("---")
        st.info(f"👥 **{len(participants)}** participant(s) already joined")

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 2 — ASSET ALLOCATION
# ══════════════════════════════════════════════════════════════════════════════
def page_allocation():
    st.markdown(f"## 💼 Asset Allocation — Welcome, **{st.session_state.username}**!")

    user_data = participants.get(st.session_state.username, {})
    current_allocation = user_data.get("allocation", {a: 0 for a in ASSETS})

    st.info("🎯 **Your goal:** Allocate your portfolio weights. Total must equal **100%**. You can rebalance during the Market Event and Session 2.")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("### Set Your Allocation")
        new_allocation = {}
        for asset in ASSETS:
            new_allocation[asset] = st.slider(
                f"{asset}",
                min_value=0,
                max_value=100,
                value=int(current_allocation.get(asset, 0)),
                step=5,
                help=f"Allocate % to {asset}"
            )

        total = sum(new_allocation.values())
        if total == 100:
            st.success(f"✅ Total: {total}% — Ready to validate!")
        elif total > 100:
            st.error(f"❌ Total: {total}% — Over by {total - 100}%")
        else:
            st.warning(f"⚠️ Total: {total}% — Remaining: {100 - total}%")

        col_a, col_b, col_c = st.columns(3)
        with col_a:
            if st.button("✅ Validate Allocation", type="primary", disabled=(total != 100)):
                participants[st.session_state.username]["allocation"] = new_allocation
                participants[st.session_state.username]["validated"] = True
                save_participants(participants)
                st.success("🎉 Allocation saved!")
                st.balloons()
        with col_b:
            if st.button("📊 View Dashboard"):
                st.session_state.page = "dashboard"
                st.rerun()
        with col_c:
            if st.button("🚪 Logout"):
                st.session_state.username = None
                st.session_state.page = "login"
                st.rerun()

    with col2:
        st.markdown("### Your Portfolio Mix")
        if total > 0:
            labels = [a for a, v in new_allocation.items() if v > 0]
            values = [v for v in new_allocation.values() if v > 0]
            colors = [ASSETS[a]["color"] for a in labels]
            fig = go.Figure(go.Pie(
                labels=labels, values=values,
                marker_colors=colors,
                hole=0.4
            ))
            fig.update_layout(margin=dict(t=0, b=0, l=0, r=0), height=300, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.markdown("*Set your allocation to see the pie chart*")

        st.markdown("### Quick Presets")
        if st.button("🛡️ Conservative"):
            st.session_state._preset = "conservative"
            st.rerun()
        if st.button("⚖️ Balanced"):
            st.session_state._preset = "balanced"
            st.rerun()
        if st.button("🚀 Aggressive"):
            st.session_state._preset = "aggressive"
            st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 3 — MAIN DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
def page_dashboard():
    user = st.session_state.username
    is_admin = user == "CIO_ADMIN"

    # Header
    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        title = "📊 CIO Dashboard — All Portfolios" if is_admin else f"📊 {user}'s Portfolio Dashboard"
        st.markdown(f"## {title}")
    with col2:
        if not is_admin:
            if st.button("💼 Edit Allocation"):
                st.session_state.page = "allocation"
                st.rerun()
    with col3:
        if st.button("🚪 Logout"):
            st.session_state.username = None
            st.session_state.page = "login"
            st.rerun()

    # ── Progress bar ──────────────────────────────────────────────────────────
    month = st.session_state.current_month
    progress = month / TOTAL_MONTHS
    sim_year = 2016 + month // 12
    sim_month_name = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"][month % 12]

    st.markdown("### ⏱️ Simulation Progress")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Simulated Date", f"{sim_month_name} {sim_year}")
    col2.metric("Month", f"{month} / {TOTAL_MONTHS}")
    col3.metric("Years Elapsed", f"{month/12:.1f} / 10")
    if month >= COVID_CRASH_MONTH and month < COVID_CRASH_MONTH + 3:
        col4.metric("🚨 Market Event", "COVID CRASH!")
    else:
        col4.metric("Status", "Running" if month < TOTAL_MONTHS else "Complete")

    st.progress(progress)

    # Demo slider
    with st.expander("🎮 Demo Controls (for presentation)"):
        st.session_state.current_month = st.slider(
            "Simulate month:", 1, TOTAL_MONTHS,
            st.session_state.current_month
        )
        st.caption("In the real workshop, this advances automatically every 15 minutes")

    st.markdown("---")

    # ── Portfolio Performance ─────────────────────────────────────────────────
    validated_participants = {
        k: v for k, v in participants.items()
        if v.get("validated") and any(val > 0 for val in v["allocation"].values())
    }

    if not validated_participants:
        st.warning("No participants have validated their allocation yet.")
        return

    # Calculate portfolio values
    def calc_portfolio_value(allocation, up_to_month):
        total = 0
        for asset, weight in allocation.items():
            if weight > 0 and asset in hist.columns:
                asset_return = hist.loc[up_to_month, asset]
                total += (weight / 100) * INITIAL_INVESTMENT * asset_return
        return total

    results = {}
    for name, data in validated_participants.items():
        value = calc_portfolio_value(data["allocation"], month)
        pct_change = ((value - INITIAL_INVESTMENT) / INITIAL_INVESTMENT) * 100
        results[name] = {"value": value, "pct_change": pct_change}

    avg_return = np.mean([r["pct_change"] for r in results.values()])

    # ── KPI cards ─────────────────────────────────────────────────────────────
    st.markdown("### 💰 Portfolio Performance")

    if not is_admin and user in results:
        my = results[user]
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Your Portfolio Value", f"${my['value']:,.0f}", f"{my['pct_change']:+.1f}%")
        col2.metric("Initial Investment", f"${INITIAL_INVESTMENT:,.0f}")
        col3.metric("Gain / Loss", f"${my['value'] - INITIAL_INVESTMENT:,.0f}")
        col4.metric("Avg Participant Return", f"{avg_return:+.1f}%")
    else:
        col1, col2, col3 = st.columns(3)
        col1.metric("Participants", len(results))
        col2.metric("Avg Return", f"{avg_return:+.1f}%")
        best = max(results.items(), key=lambda x: x[1]["pct_change"])
        col3.metric("🏆 Best Performer", best[0], f"{best[1]['pct_change']:+.1f}%")

    st.markdown("---")

    # ── Charts ────────────────────────────────────────────────────────────────
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 📈 Portfolio Growth Over Time")
        fig = go.Figure()
        for name, data in validated_participants.items():
            monthly_values = [
                calc_portfolio_value(data["allocation"], m)
                for m in range(0, month + 1, max(1, month // 50))
            ]
            months_x = list(range(0, month + 1, max(1, month // 50)))
            highlight = name == user and not is_admin
            fig.add_trace(go.Scatter(
                x=months_x,
                y=monthly_values,
                name=name,
                line=dict(width=3 if highlight else 1.5),
                opacity=1.0 if highlight else 0.6
            ))
        fig.add_hline(y=INITIAL_INVESTMENT, line_dash="dash", line_color="gray",
                      annotation_text="Initial $5M")
        fig.update_layout(
            xaxis_title="Month",
            yaxis_title="Portfolio Value ($)",
            height=350,
            legend=dict(orientation="h", yanchor="bottom", y=1.02)
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("### 🏆 Leaderboard")
        sorted_results = sorted(results.items(), key=lambda x: x[1]["pct_change"], reverse=True)
        lb_data = []
        for i, (name, r) in enumerate(sorted_results):
            medal = ["🥇", "🥈", "🥉"][i] if i < 3 else f"#{i+1}"
            lb_data.append({
                "Rank": medal,
                "Participant": name,
                "Portfolio Value": f"${r['value']:,.0f}",
                "Return": f"{r['pct_change']:+.1f}%"
            })
        st.dataframe(pd.DataFrame(lb_data), hide_index=True, use_container_width=True)

        # Bar chart
        names = [x[0] for x in sorted_results]
        returns = [x[1]["pct_change"] for x in sorted_results]
        colors = ["green" if r > 0 else "red" for r in returns]
        fig2 = go.Figure(go.Bar(x=names, y=returns, marker_color=colors))
        fig2.update_layout(
            yaxis_title="Return (%)", height=200,
            margin=dict(t=10, b=10)
        )
        st.plotly_chart(fig2, use_container_width=True)

    # ── Asset breakdown ───────────────────────────────────────────────────────
    if not is_admin and user in validated_participants:
        st.markdown("---")
        st.markdown("### 📋 Your Asset Breakdown")
        alloc = validated_participants[user]["allocation"]
        rows = []
        for asset, weight in alloc.items():
            if weight > 0:
                asset_val = (weight / 100) * INITIAL_INVESTMENT * hist.loc[month, asset]
                asset_return = (hist.loc[month, asset] - 1) * 100
                rows.append({
                    "Asset": asset,
                    "Weight": f"{weight}%",
                    "Current Value": f"${asset_val:,.0f}",
                    "Return Since Start": f"{asset_return:+.1f}%"
                })
        st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True)

    # ── Market event alert ────────────────────────────────────────────────────
    if COVID_CRASH_MONTH - 2 <= month <= COVID_CRASH_MONTH + 2:
        st.markdown("---")
        st.error("🚨 **MARKET EVENT: COVID-19 CRASH** — Participants may rebalance their portfolios now! Window open for 15 minutes.")

# ══════════════════════════════════════════════════════════════════════════════
# ROUTER
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.page == "login":
    page_login()
elif st.session_state.page == "allocation":
    page_allocation()
elif st.session_state.page == "dashboard":
    page_dashboard()
