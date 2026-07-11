import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import requests
from datetime import datetime, timedelta

st.set_page_config(
    page_title="Mini-Aladdin",
    page_icon="📊",
    layout="wide"
)

st.markdown("""
<style>
    @media (prefers-color-scheme: light) {
        .main, .main *, body, html { background-color: #ffffff !important; }
        h1, h2, h3, h4, h5, h6, p, span, div, label, li, td, th { color: #000000 !important; }
        div[data-testid="stMetric"] { background-color: #f8f9fa !important; border: 2px solid #e0e0e0 !important; }
        div[data-testid="stMetric"] p { color: #000000 !important; }
        div[data-testid="stMetric"] label { color: #333333 !important; }
        .stDataFrame th { background-color: #f0f0f0 !important; color: #000000 !important; }
        .stDataFrame td { color: #000000 !important; }
        input, textarea, select { background-color: #ffffff !important; color: #000000 !important; }
    }
    
    @media (prefers-color-scheme: dark) {
        .main, .main *, body, html { background-color: #0e1117 !important; }
        h1, h2, h3, h4, h5, h6, p, span, div, label, li, td, th { color: #ffffff !important; }
        div[data-testid="stMetric"] { background-color: #1e2937 !important; border: 2px solid #313846 !important; }
        div[data-testid="stMetric"] p { color: #ffffff !important; }
        div[data-testid="stMetric"] label { color: #b0b0b0 !important; }
        .stDataFrame th { background-color: #1e2937 !important; color: #ffffff !important; }
        .stDataFrame td { color: #ffffff !important; }
        input, textarea, select { background-color: #1e2937 !important; color: #ffffff !important; }
        .stSuccess { background-color: #0f5132 !important; color: #ffffff !important; }
        .stError { background-color: #842029 !important; color: #ffffff !important; }
    }
    
    div[data-testid="stMetric"] { border-radius: 10px !important; padding: 15px !important; }
    div[data-testid="stMetric"] p { font-weight: bold !important; font-size: 24px !important; }
    div[data-testid="stMetric"] label { font-size: 14px !important; }
    
    section[data-testid="stSidebar"] { background-color: #1e3a5f !important; }
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] div { color: #ffffff !important; }
    
    .stButton button {
        background-color: #4a90e2 !important;
        color: #ffffff !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        padding: 10px 20px !important;
    }
    
    footer { visibility: hidden; }
    
    @media (max-width: 768px) {
        div[data-testid="stMetric"] p { font-size: 18px !important; }
        h1 { font-size: 22px !important; }
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data(ttl=300, show_spinner="Loading prices from MOEX...")
def get_moex_prices(tickers):
    prices = {}
    base_url = "https://iss.moex.com/iss/engines/stock/markets/bonds/boards/TQOB/securities"
    
    for ticker in tickers:
        try:
            url = f"{base_url}/{ticker}.json"
            response = requests.get(url, timeout=10)
            data = response.json()
            
            columns = data.get('marketdata', {}).get('columns', [])
            rows = data.get('marketdata', {}).get('data', [])
            
            if not rows:
                prices[ticker] = None
                continue
            
            price = None
            if 'LAST' in columns:
                last_idx = columns.index('LAST')
                val = rows[0][last_idx]
                if val is not None:
                    price = val
            
            if price is None and 'PREVPRICE' in columns:
                prev_idx = columns.index('PREVPRICE')
                val = rows[0][prev_idx]
                if val is not None:
                    price = val
            
            if price is None and 'LASTTOPREVPRICE' in columns:
                ltp_idx = columns.index('LASTTOPREVPRICE')
                val = rows[0][ltp_idx]
                if val is not None:
                    price = val
            
            prices[ticker] = price
            
        except Exception as e:
            prices[ticker] = None
    
    return prices


if 'positions' not in st.session_state:
    st.session_state.positions = [
        {'ticker': 'SU26238RMFS4', 'short_name': 'OFZ 26238', 'qty': 41, 'buy_price': 59.2, 'coupon_rate': 0.071, 'duration': 7.2},
        {'ticker': 'SU26246RMFS5', 'short_name': 'OFZ 26246', 'qty': 65, 'buy_price': 88.4, 'coupon_rate': 0.12, 'duration': 5.6},
        {'ticker': 'SU26247RMFS1', 'short_name': 'OFZ 26247', 'qty': 149, 'buy_price': 89.0, 'coupon_rate': 0.1225, 'duration': 6.08},
        {'ticker': 'SU26248RMFS9', 'short_name': 'OFZ 26248', 'qty': 174, 'buy_price': 88.1, 'coupon_rate': 0.1225, 'duration': 6.2},
        {'ticker': 'SU26254RMFS6', 'short_name': 'OFZ 26254', 'qty': 250, 'buy_price': 93.0, 'coupon_rate': 0.13, 'duration': 6.06}
    ]


tickers = [pos['ticker'] for pos in st.session_state.positions]
live_prices = get_moex_prices(tickers)

for pos in st.session_state.positions:
    price_from_moex = live_prices.get(pos['ticker'])
    if price_from_moex is not None:
        pos['current_price'] = price_from_moex
    elif 'current_price' not in pos or pos['current_price'] is None:
        pos['current_price'] = pos['buy_price']


def calculate_metrics(positions):
    df = pd.DataFrame(positions)
    df['market_value'] = df['qty'] * df['current_price'] * 10
    df['cost_basis'] = df['qty'] * df['buy_price'] * 10
    df['pnl'] = df['market_value'] - df['cost_basis']
    df['pnl_pct'] = (df['pnl'] / df['cost_basis']) * 100
    
    total_value = df['market_value'].sum()
    df['weight'] = df['market_value'] / total_value
    weighted_duration = (df['weight'] * df['duration']).sum()
    dv01 = total_value * weighted_duration * 0.0001
    annual_coupon = (df['qty'] * 1000 * df['coupon_rate']).sum()
    
    return {
        'total_value': total_value,
        'cost_basis': df['cost_basis'].sum(),
        'total_pnl': df['pnl'].sum(),
        'total_pnl_pct': (df['pnl'].sum() / df['cost_basis'].sum()) * 100,
        'weighted_duration': weighted_duration,
        'dv01': dv01,
        'annual_coupon': annual_coupon,
        'details': df
    }

metrics = calculate_metrics(st.session_state.positions)


with st.sidebar:
    st.title("Mini-Aladdin")
    st.markdown("---")
    
    page = st.radio(
        "Navigation",
        ["Home", "Positions", "Stress Tests", "Goal Forecast"],
        index=0
    )
    
    st.markdown("---")
    st.caption(f"Updated: {datetime.now().strftime('%H:%M')}")
    st.caption(f"Source: MOEX ISS API")
    
    if st.button("Refresh Prices"):
        st.cache_data.clear()
        st.rerun()


if page == "Home":
    st.title("Portfolio Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Value", f"{metrics['total_value']:,.0f} RUB", 
                 f"{metrics['total_pnl']:+,.0f} RUB")
    
    with col2:
        st.metric("Return", f"{metrics['total_pnl_pct']:+.2f}%", "vs purchase")
    
    with col3:
        st.metric("Duration", f"{metrics['weighted_duration']:.2f} years", "weighted avg")
    
    with col4:
        st.metric("DV01", f"{metrics['dv01']:,.0f} RUB", "risk per 0.01%")
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Portfolio Distribution")
        try:
            fig_pie = px.pie(metrics['details'], values='market_value', 
                            names='short_name', hole=0.4,
                            color_discrete_sequence=px.colors.qualitative.Set3)
            fig_pie.update_layout(height=400, template='plotly_white')
            st.plotly_chart(fig_pie, use_container_width=True)
        except Exception as e:
            st.info("Chart temporarily unavailable")
    
    with col2:
        st.subheader("P&L by Position")
        try:
            colors = ['rgb(46, 204, 113)' if x > 0 else 'rgb(231, 76, 60)' 
                      for x in metrics['details']['pnl']]
            fig_bar = go.Figure(go.Bar(
                x=metrics['details']['short_name'],
                y=metrics['details']['pnl'],
                marker_color=colors
            ))
            fig_bar.update_layout(height=400, showlegend=False, template='plotly_white')
            st.plotly_chart(fig_bar, use_container_width=True)
        except Exception as e:
            st.info("Chart temporarily unavailable")
    
    st.markdown("---")
    st.subheader("Progress to Goal: 5,000,000 RUB")
    progress = min(metrics['total_value'] / 5_000_000, 1.0)
    st.progress(progress)
    st.caption(f"Achieved: {metrics['total_value']:,.0f} RUB ({progress*100:.1f}%)")
    
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Coupon per year", f"{metrics['annual_coupon']:,.0f} RUB")
    with col2:
        st.metric("Coupon per month", f"{metrics['annual_coupon']/12:,.0f} RUB")
    with col3:
        st.metric("Coupon per day", f"{metrics['annual_coupon']/365:,.0f} RUB")


elif page == "Positions":
    st.title("Manage Positions")
    
    st.subheader("Current Positions (prices from MOEX)")
    
    df_display = metrics['details'][['short_name', 'ticker', 'qty', 'buy_price', 
                                     'current_price', 'market_value', 'pnl', 'pnl_pct']].copy()
    df_display.columns = ['Bond', 'Ticker', 'Qty', 'Buy %', 
                          'Current %', 'Value RUB', 'P&L RUB', 'P&L %']
    st.dataframe(df_display, use_container_width=True)
    
    st.markdown("---")
    
    st.subheader("Edit Position")
    
    position_options = [f"{pos['short_name']} ({pos['qty']} pcs)" 
                        for pos in st.session_state.positions]
    
    selected_position = st.selectbox(
        "Select bond:",
        position_options,
        key="select_position"
    )
    
    if selected_position:
        idx = position_options.index(selected_position)
        pos = st.session_state.positions[idx]
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            new_qty = st.number_input(
                "Quantity (pcs)",
                min_value=0,
                value=int(pos['qty']),
                step=1,
                key=f"qty_{idx}"
            )
        
        with col2:
            new_ticker = st.text_input(
                "Ticker",
                value=pos['ticker'],
                key=f"ticker_{idx}"
            )
        
        with col3:
            new_name = st.text_input(
                "Name",
                value=pos['short_name'],
                key=f"name_{idx}"
            )
        
        col4, col5, col6 = st.columns(3)
        
        with col4:
            new_buy_price = st.number_input(
                "Buy Price (%)",
                value=float(pos['buy_price']),
                step=0.1,
                key=f"buy_price_{idx}"
            )
        
        with col5:
            new_coupon = st.number_input(
                "Coupon (%)",
                value=float(pos['coupon_rate'] * 100),
                step=0.1,
                key=f"coupon_{idx}"
            )
        
        with col6:
            new_duration = st.number_input(
                "Duration (years)",
                value=float(pos['duration']),
                step=0.1,
                key=f"duration_{idx}"
            )
        
        col_btn1, col_btn2 = st.columns(2)
        
        with col_btn1:
            if st.button("Save Changes", key=f"save_{idx}"):
                st.session_state.positions[idx] = {
                    'ticker': new_ticker,
                    'short_name': new_name,
                    'qty': int(new_qty),
                    'buy_price': float(new_buy_price),
                    'coupon_rate': float(new_coupon) / 100,
                    'duration': float(new_duration),
                    'current_price': pos['current_price']
                }
                st.success(f"Position '{new_name}' updated!")
                st.rerun()
        
        with col_btn2:
            if st.button("Delete Position", key=f"delete_{idx}"):
                name = pos['short_name']
                st.session_state.positions.pop(idx)
                st.success(f"Position '{name}' deleted!")
                st.rerun()
    
    st.markdown("---")
    
    st.subheader("Add New Position")
    
    col1, col2 = st.columns(2)
    
    with col1:
        add_ticker = st.text_input("Ticker (SU...)", "", key="add_ticker")
        add_name = st.text_input("Name", "", key="add_name")
        add_qty = st.number_input("Quantity", min_value=1, value=10, key="add_qty")
    
    with col2:
        add_buy_price = st.number_input("Buy Price (%)", value=90.0, step=0.1, key="add_buy_price")
        add_coupon = st.number_input("Coupon (%)", value=10.0, step=0.1, key="add_coupon")
        add_duration = st.number_input("Duration (years)", value=5.0, step=0.1, key="add_duration")
    
    if st.button("Add Position", key="add_position_btn"):
        if add_ticker and add_name:
            st.session_state.positions.append({
                'ticker': add_ticker,
                'short_name': add_name,
                'qty': int(add_qty),
                'buy_price': float(add_buy_price),
                'coupon_rate': float(add_coupon) / 100,
                'duration': float(add_duration),
                'current_price': None
            })
            st.success(f"Added: {add_name}")
            st.cache_data.clear()
            st.rerun()
        else:
            st.error("Enter ticker and name!")


elif page == "Stress Tests":
    st.title("Stress Testing")
    
    col1, col2 = st.columns(2)
    with col1:
        rate_shock = st.slider("Rate Change (%)", -5.0, 10.0, 0.0, 0.1)
    with col2:
        fx_shock = st.slider("RUB Weakening (%)", 0.0, 50.0, 0.0, 1.0)
    
    duration = metrics['weighted_duration']
    current_value = metrics['total_value']
    
    value_change = current_value * (-duration * rate_shock / 100)
    if fx_shock > 0:
        value_change -= current_value * (duration * fx_shock * 0.15 / 100)
    
    new_value = current_value + value_change
    change_pct = (value_change / current_value) * 100
    
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Current Value", f"{current_value:,.0f} RUB")
    with col2:
        st.metric("Change", f"{value_change:+,.0f} RUB", f"{change_pct:+.2f}%")
    with col3:
        st.metric("New Value", f"{new_value:,.0f} RUB")
    
    st.markdown("---")
    st.subheader("Scenarios")
    
    scenarios = [
        ("Strong rate cut", -3.0, 0),
        ("Moderate rate cut", -1.5, 0),
        ("No change", 0, 0),
        ("Small rate hike", 1.0, 0),
        ("Significant rate hike", 2.0, 0),
        ("Crisis", 5.0, 20),
    ]
    
    scenario_data = []
    for name, rate, fx in scenarios:
        change = current_value * (-duration * rate / 100)
        if fx > 0:
            change -= current_value * (duration * fx * 0.15 / 100)
        scenario_data.append({
            'Scenario': name,
            'Rate Shock': f"{rate:+.1f}%",
            'Change RUB': f"{change:+,.0f}",
            'New Value RUB': f"{current_value + change:,.0f}"
        })
    
    st.dataframe(pd.DataFrame(scenario_data), use_container_width=True, hide_index=True)


elif page == "Goal Forecast":
    st.title("Goal Achievement Forecast")
    
    target = st.number_input("Goal (RUB)", value=5_000_000, step=100_000)
    monthly = st.number_input("Monthly Investment (RUB)", value=100_000, step=10_000)
    
    forecasts = []
    for pos in st.session_state.positions:
        value = pos['qty'] * pos['current_price'] * 10
        coupon = pos['coupon_rate']
        
        months = 0
        total_coupons = 0
        while value < target and months < 600:
            months += 1
            value += monthly
            if months % 6 == 0:
                coupon_income = value * coupon / 2
                value += coupon_income
                total_coupons += coupon_income
        
        forecasts.append({
            'Bond': pos['short_name'],
            'Years to Goal': round(months / 12, 1),
            'Coupon %': f"{coupon*100:.2f}%",
            'Reinvested Coupons RUB': f"{total_coupons:,.0f}"
        })
    
    df_forecast = pd.DataFrame(forecasts).sort_values('Years to Goal')
    
    st.markdown("---")
    st.subheader("Time to Goal by Bond")
    
    try:
        fig = go.Figure(go.Bar(
            x=df_forecast['Bond'],
            y=df_forecast['Years to Goal'],
            marker_color=px.colors.sequential.Viridis[:len(df_forecast)],
            text=df_forecast['Years to Goal'].apply(lambda x: f"{x:.1f} years"),
            textposition='auto'
        ))
        fig.update_layout(height=400, template='plotly_white', yaxis_title="Years")
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.info("Chart temporarily unavailable")
    
    st.dataframe(df_forecast, use_container_width=True, hide_index=True)
    
    if len(df_forecast) > 0:
        best = df_forecast.iloc[0]
        st.success(f"**Best choice:** {best['Bond']} - {best['Years to Goal']:.1f} years")
