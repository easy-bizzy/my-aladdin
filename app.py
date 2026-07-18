import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import requests
from datetime import datetime, timedelta
import re
import time

st.set_page_config(page_title="Mini-Aladdin", page_icon="📊", layout="wide")

# ==================== CSS ====================
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
    section[data-testid="stSidebar"] h1, section[data-testid="stSidebar"] h2, section[data-testid="stSidebar"] h3, section[data-testid="stSidebar"] p, section[data-testid="stSidebar"] label, section[data-testid="stSidebar"] span, section[data-testid="stSidebar"] div { color: #ffffff !important; }
    .stButton button { background-color: #4a90e2 !important; color: #ffffff !important; border-radius: 8px !important; font-weight: 600 !important; padding: 10px 20px !important; }
    footer { visibility: hidden; }
    @media (max-width: 768px) { div[data-testid="stMetric"] p { font-size: 18px !important; } h1 { font-size: 22px !important; } }
    .level-badge-epic { background: linear-gradient(135deg, #00c853, #69f0ae); padding: 15px 30px; border-radius: 50px; color: white !important; font-weight: bold; display: inline-block; }
    .level-badge-legend { background: linear-gradient(135deg, #ffd700, #ffa000); padding: 15px 30px; border-radius: 50px; color: #333 !important; font-weight: bold; display: inline-block; }
    .level-badge-mythic { background: linear-gradient(135deg, #9c27b0, #7c4dff); padding: 15px 30px; border-radius: 50px; color: white !important; font-weight: bold; display: inline-block; }
    .level-badge-mythic-honor { background: linear-gradient(135deg, #d32f2f, #9c27b0); padding: 15px 30px; border-radius: 50px; color: white !important; font-weight: bold; display: inline-block; }
    .level-badge-mythic-glory { background: linear-gradient(135deg, #ff6f00, #ffd700); padding: 15px 30px; border-radius: 50px; color: #333 !important; font-weight: bold; display: inline-block; }
    .level-badge-mythic-legion { background: linear-gradient(135deg, #ff1744, #2979ff, #00e676); padding: 15px 30px; border-radius: 50px; color: white !important; font-weight: bold; display: inline-block; }
    .level-badge-mythic-immortal { background: linear-gradient(135deg, #000000, #4a148c, #ffd700); padding: 15px 30px; border-radius: 50px; color: #ffd700 !important; font-weight: bold; display: inline-block; }
    .stars-display { background: linear-gradient(135deg, #fff9c4, #fff176); padding: 15px 25px; border-radius: 15px; border: 2px solid #ffd700; color: #333 !important; font-weight: bold; display: inline-block; }
    .achievement-card { background: linear-gradient(135deg, #667eea, #764ba2); padding: 20px; border-radius: 15px; margin: 10px 0; color: white !important; }
    .achievement-card * { color: white !important; }
    .coupon-upcoming { background: linear-gradient(135deg, #11998e, #38ef7d); padding: 15px; border-radius: 10px; color: white !important; margin: 5px 0; }
    .coupon-upcoming * { color: white !important; }
</style>
""", unsafe_allow_html=True)

# ==================== НАСТРОЙКИ JSONBIN ====================

try:
    JSONBIN_BIN_ID = st.secrets["JSONBIN_BIN_ID"]
    JSONBIN_API_KEY = st.secrets["JSONBIN_API_KEY"]
    JSONBIN_URL = f"https://api.jsonbin.io/v3/b/{JSONBIN_BIN_ID}"
    CLOUD_ENABLED = True
except:
    CLOUD_ENABLED = False
    st.sidebar.warning("️ JSONBin не настроен. Данные не сохраняются в облаке.")

def load_from_cloud():
    if not CLOUD_ENABLED:
        return None
    try:
        headers = {"X-Master-Key": JSONBIN_API_KEY}
        response = requests.get(f"{JSONBIN_URL}/latest", headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if 'record' in data:
                return data['record']
            return data
    except:
        pass
    return None

def save_to_cloud(positions):
    if not CLOUD_ENABLED:
        return False
    try:
        headers = {
            "X-Master-Key": JSONBIN_API_KEY,
            "Content-Type": "application/json"
        }
        response = requests.put(JSONBIN_URL, json=positions, headers=headers, timeout=10)
        return response.status_code == 200
    except:
        return False

# ==================== ФУНКЦИИ ====================

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
                val = rows[0][columns.index('LAST')]
                if val is not None:
                    price = val
            if price is None and 'PREVPRICE' in columns:
                val = rows[0][columns.index('PREVPRICE')]
                if val is not None:
                    price = val
            prices[ticker] = price
        except:
            prices[ticker] = None
    return prices

def get_coupon_dates(ticker, coupon_rate, qty, face_value=1000):
    coupon_schedule = {
        'SU26238RMFS4': {'dates': [(12, 2), (6, 2)], 'amount_per_bond': 35.4},
        'SU26246RMFS7': {'dates': [(9, 23), (3, 23)], 'amount_per_bond': 59.84},
        'SU26247RMFS5': {'dates': [(11, 25), (5, 25)], 'amount_per_bond': 61.08},
        'SU26248RMFS3': {'dates': [(12, 2), (6, 2)], 'amount_per_bond': 61.08},
        'SU26254RMFS1': {'dates': [(10, 21), (4, 21)], 'amount_per_bond': 64.82}
    }
    if ticker not in coupon_schedule:
        return []
    schedule = coupon_schedule[ticker]
    today = datetime.now()
    coupons = []
    for year_offset in range(2):
        for month, day in schedule['dates']:
            coupon_date = datetime(today.year + year_offset, month, day)
            if coupon_date >= today:
                coupons.append({
                    'date': coupon_date,
                    'amount': schedule['amount_per_bond'] * qty,
                    'ticker': ticker
                })
    return sorted(coupons, key=lambda x: x['date'])[:4]

def get_investor_level(total_value):
    if total_value < 500_000:
        return "🌱 Новичок", "level-badge-epic", 500_000, "До Эпика"
    elif total_value < 750_000:
        return "🟢 Эпик", "level-badge-epic", 750_000, "До Легенды"
    elif total_value < 1_000_000:
        return "👑 Легенда", "level-badge-legend", 1_000_000, "До Мифического"
    elif total_value < 2_500_000:
        return "🔮 Мифический", "level-badge-mythic", 2_500_000, "До Чести"
    elif total_value < 5_000_000:
        return " Мифическая честь", "level-badge-mythic-honor", 5_000_000, "До Славы"
    elif total_value < 7_500_000:
        return "🔥 Мифическая слава", "level-badge-mythic-glory", 7_500_000, "До Легиона"
    elif total_value < 10_000_000:
        return "⚔️ Мифический легион", "level-badge-mythic-legion", 10_000_000, "До Бессмертного"
    else:
        return "🌟 Мифический бессмертный", "level-badge-mythic-immortal", 10_000_000, "MAX!"

def get_star_level(annual_coupon):
    if annual_coupon >= 1_000_000:
        return 100, "⭐"
    elif annual_coupon >= 500_000:
        return 50, "⭐"
    elif annual_coupon >= 250_000:
        return 25, "⭐"
    else:
        return 0, "⭐"

def get_achievements(metrics):
    return [
        {'name': 'Первые шаги', 'icon': '👶', 'description': 'Создать портфель', 'unlocked': True, 'condition': '✅'},
        {'name': 'Сотня', 'icon': '💰', 'description': '100 000 ₽', 'unlocked': metrics['total_value'] >= 100_000, 'condition': f"{metrics['total_value']:,.0f} / 100 000"},
        {'name': 'Полмиллиона', 'icon': '💎', 'description': '500 000 ₽', 'unlocked': metrics['total_value'] >= 500_000, 'condition': f"{metrics['total_value']:,.0f} / 500 000"},
        {'name': 'Миллионер', 'icon': '', 'description': '1 000 000 ₽', 'unlocked': metrics['total_value'] >= 1_000_000, 'condition': f"{metrics['total_value']:,.0f} / 1 000 000"},
        {'name': 'Диверсификация', 'icon': '📊', 'description': '5 облигаций', 'unlocked': len(st.session_state.positions) >= 5, 'condition': f"{len(st.session_state.positions)} / 5"},
        {'name': 'В плюсе', 'icon': '', 'description': 'P&L > 0', 'unlocked': metrics['total_pnl'] > 0, 'condition': f"{metrics['total_pnl']:+,.0f} ₽"},
        {'name': '25 звезд', 'icon': '⭐', 'description': 'Купон 250 000 ₽', 'unlocked': metrics['annual_coupon'] >= 250_000, 'condition': f"{metrics['annual_coupon']:,.0f} / 250 000"},
        {'name': '50 звезд', 'icon': '⭐', 'description': 'Купон 500 000 ₽', 'unlocked': metrics['annual_coupon'] >= 500_000, 'condition': f"{metrics['annual_coupon']:,.0f} / 500 000"},
        {'name': '100 звезд', 'icon': '⭐', 'description': 'Купон 1 000 000 ₽', 'unlocked': metrics['annual_coupon'] >= 1_000_000, 'condition': f"{metrics['annual_coupon']:,.0f} / 1 000 000"},
        {'name': 'Мифический легион', 'icon': '️', 'description': '7 500 000 ₽', 'unlocked': metrics['total_value'] >= 7_500_000, 'condition': f"{metrics['total_value']:,.0f} / 7 500 000"},
        {'name': 'Мифический бессмертный', 'icon': '🌟', 'description': '10 000 000 ₽', 'unlocked': metrics['total_value'] >= 10_000_000, 'condition': f"{metrics['total_value']:,.0f} / 10 000 000"},
    ]

# ==================== ИНИЦИАЛИЗАЦИЯ ====================

DEFAULT_POSITIONS = [
    {'ticker': 'SU26238RMFS4', 'short_name': 'ОФЗ 26238', 'qty': 41, 'buy_price': 65.0, 'coupon_rate': 0.071, 'duration': 7.2, 'maturity_years': 15},
    {'ticker': 'SU26246RMFS7', 'short_name': 'ОФЗ 26246', 'qty': 76, 'buy_price': 91.0, 'coupon_rate': 0.12, 'duration': 5.6, 'maturity_years': 8},
    {'ticker': 'SU26247RMFS5', 'short_name': 'ОФЗ 26247', 'qty': 179, 'buy_price': 92.0, 'coupon_rate': 0.1225, 'duration': 6.08, 'maturity_years': 8},
    {'ticker': 'SU26248RMFS3', 'short_name': 'ОФЗ 26248', 'qty': 210, 'buy_price': 91.5, 'coupon_rate': 0.1225, 'duration': 6.2, 'maturity_years': 9},
    {'ticker': 'SU26254RMFS1', 'short_name': 'ОФЗ 26254', 'qty': 298, 'buy_price': 93.5, 'coupon_rate': 0.13, 'duration': 6.06, 'maturity_years': 10}
]

if 'positions' not in st.session_state or len(st.session_state.positions) == 0:
    cloud_data = load_from_cloud()
    if cloud_data and len(cloud_data) > 0:
        st.session_state.positions = cloud_data
    else:
        st.session_state.positions = [p.copy() for p in DEFAULT_POSITIONS]

tickers = [pos['ticker'] for pos in st.session_state.positions]
live_prices = get_moex_prices(tickers)
price_update_time = datetime.now()

for pos in st.session_state.positions:
    price = live_prices.get(pos['ticker'])
    if price is not None:
        pos['current_price'] = price
    elif 'current_price' not in pos:
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
    avg_annual_return = 0
    if total_value > 0:
        for _, row in df.iterrows():
            weight = row['market_value'] / total_value
            avg_annual_return += weight * row['coupon_rate'] * 100
    return {
        'total_value': total_value,
        'cost_basis': df['cost_basis'].sum(),
        'total_pnl': df['pnl'].sum(),
        'total_pnl_pct': (df['pnl'].sum() / df['cost_basis'].sum()) * 100,
        'weighted_duration': weighted_duration,
        'dv01': dv01,
        'annual_coupon': annual_coupon,
        'avg_annual_return': avg_annual_return,
        'details': df
    }

metrics = calculate_metrics(st.session_state.positions)

# ==================== САЙДБАР ====================

with st.sidebar:
    st.title("📊 Mini-Aladdin")
    st.markdown("---")
    page = st.radio("Навигация", ["Главная", "Позиции", "Купонный календарь", "Стресс-тесты", "Прогноз цели", "Импорт из брокера", "Достижения"], index=0)
    st.markdown("---")
    st.caption(f"Цены: {price_update_time.strftime('%H:%M')}")
    level_name, level_css, next_level, _ = get_investor_level(metrics['total_value'])
    st.caption(f"Уровень: {level_name}")
    stars_count, star_icon = get_star_level(metrics['annual_coupon'])
    if stars_count > 0:
        st.caption(f"Звезды: {star_icon} {stars_count}")
    
    st.markdown("---")
    st.subheader("💾 Облако")
    
    if CLOUD_ENABLED:
        if st.button("💾 Сохранить в облако", type="primary", use_container_width=True):
            if save_to_cloud(st.session_state.positions):
                st.success("✅ Сохранено!")
                st.balloons()
            else:
                st.error("❌ Ошибка")
        
        if st.button("🔄 Загрузить из облака"):
            cloud_data = load_from_cloud()
            if cloud_data and len(cloud_data) > 0:
                st.session_state.positions = cloud_data
                st.success("✅ Загружено!")
                st.rerun()
            else:
                st.error("❌ Не удалось")
        
        st.caption(f"Bin: {JSONBIN_BIN_ID[:8]}...")
    else:
        st.warning("JSONBin не настроен")
    
    if st.button("🔄 Сбросить портфель"):
        st.session_state.positions = [p.copy() for p in DEFAULT_POSITIONS]
        st.success("✅ Сброшено! Обновите страницу (F5)")
        st.stop()
    
    if st.button("Обновить цены"):
        st.rerun()

# ==================== ГЛАВНАЯ ====================

if page == "Главная":
    st.title("💼 Обзор портфеля")
    level_name, level_css, next_level, level_msg = get_investor_level(metrics['total_value'])
    stars_count, star_icon = get_star_level(metrics['annual_coupon'])
    
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.markdown(f"### Ваш уровень: {level_name}")
        if metrics['total_value'] < 10_000_000:
            st.progress(min(metrics['total_value'] / next_level, 1.0))
            st.caption(f"{level_msg}: {next_level - metrics['total_value']:,.0f} ₽")
    with col2:
        st.markdown(f'<div class="{level_css}">{level_name}</div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="stars-display">{star_icon} {stars_count} звезд</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Счетчик обратного отсчета
    target_date = datetime(2031, 12, 31)
    today = datetime.now()
    
    if today >= target_date:
        countdown_text = "⏰ Время пришло!"
        total_days = 0
    else:
        delta = target_date - today
        total_days = delta.days
        
        years_left = target_date.year - today.year
        months_left = target_date.month - today.month
        days_left = target_date.day - today.day
        
        if days_left < 0:
            months_left -= 1
            prev_month = target_date.month - 1 if target_date.month > 1 else 12
            prev_year = target_date.year if target_date.month > 1 else target_date.year - 1
            if prev_month in [1, 3, 5, 7, 8, 10, 12]:
                days_in_prev = 31
            elif prev_month in [4, 6, 9, 11]:
                days_in_prev = 30
            else:
                days_in_prev = 29 if (prev_year % 4 == 0 and (prev_year % 100 != 0 or prev_year % 400 == 0)) else 28
            days_left += days_in_prev
        
        if months_left < 0:
            years_left -= 1
            months_left += 12
        
        time_parts = []
        if years_left > 0:
            time_parts.append(f"{years_left} г.")
        if months_left > 0:
            time_parts.append(f"{months_left} мес.")
        if days_left > 0:
            time_parts.append(f"{days_left} дн.")
        
        countdown_text = " ".join(time_parts) if time_parts else "0 дн."
    
    # 4 метрики: Стоимость, Доходность, Средний % годовых, Счетчик
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("💰 Стоимость", f"{metrics['total_value']:,.0f} ₽", f"{metrics['total_pnl']:+,.0f} ₽")
    with col2:
        st.metric("📈 Доходность", f"{metrics['total_pnl_pct']:+.2f}%", "vs покупка")
    with col3:
        st.metric("📊 Средний % годовых", f"{metrics['avg_annual_return']:.2f}%", "взвешенный")
    with col4:
        st.metric("⏰ До 31.12.2031", countdown_text, f"{total_days:,} дн.")
    
    st.markdown("---")
    
    # План накоплений
    remaining = 10_000_000 - metrics['total_value']
    total_months_left = years_left * 12 + months_left if today < target_date else 0
    monthly_coupon_income = metrics['annual_coupon'] / 12
    
    if total_months_left > 0 and remaining > 0:
        monthly_needed_with_coupons = max(0, (remaining - monthly_coupon_income * total_months_left) / total_months_left)
    else:
        monthly_needed_with_coupons = 0
    
    progress = min(metrics['total_value'] / 10_000_000, 1.0)
    
    st.subheader(f"🎯 Цель: 10 000 000 ₽ к 31.12.2031")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Текущая стоимость", f"{metrics['total_value']:,.0f} ₽")
    with col2:
        st.metric("Осталось накопить", f"{remaining:,.0f} ₽")
    with col3:
        st.metric("Прогресс", f"{progress*100:.1f}%")
    
    st.progress(progress)
    
    st.markdown("")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Без пополнений")
        st.info(f"""
        - Текущий портфель: **{metrics['total_value']:,.0f} ₽**
        - Купоны за {total_months_left} мес: **+{monthly_coupon_income * total_months_left:,.0f} ₽**
        - Итого к 2031: **{metrics['total_value'] + monthly_coupon_income * total_months_left:,.0f} ₽**
        - До цели: **{10_000_000 - (metrics['total_value'] + monthly_coupon_income * total_months_left):,.0f} ₽**
        """)
    
    with col2:
        st.markdown("#### С пополнениями")
        st.success(f"""
        - Нужно откладывать: **{monthly_needed_with_coupons:,.0f} ₽/мес**
        - С учетом купонов
        - К 2031 будет: **~10 000 000 ₽** ✅
        """)
    
    st.caption(f"💡 Купонный доход: {monthly_coupon_income:,.0f} ₽/мес | {metrics['annual_coupon']:,.0f} ₽/год")
    
    st.markdown("---")
    st.subheader("Текущие позиции")
    price_df = metrics['details'][['short_name', 'buy_price', 'current_price', 'pnl']].copy()
    price_df.columns = ['Облигация', 'Покупка %', 'Сейчас %', 'P&L ₽']
    st.dataframe(price_df, use_container_width=True)
    
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Распределение")
        try:
            fig = px.pie(metrics['details'], values='market_value', names='short_name', hole=0.4, color_discrete_sequence=px.colors.qualitative.Set3)
            fig.update_layout(height=400, template='plotly_white')
            st.plotly_chart(fig, use_container_width=True)
        except:
            st.info("График недоступен")
    with col2:
        st.subheader("P&L по позициям")
        try:
            colors = ['rgb(46, 204, 113)' if x > 0 else 'rgb(231, 76, 60)' for x in metrics['details']['pnl']]
            fig = go.Figure(go.Bar(y=metrics['details']['short_name'], x=metrics['details']['pnl'], marker_color=colors, orientation='h', text=metrics['details']['pnl'].apply(lambda x: f"{x:+,.0f} ₽")))
            fig.update_layout(height=400, template='plotly_white', xaxis_title="P&L (₽)")
            st.plotly_chart(fig, use_container_width=True)
        except:
            st.info("График недоступен")
    
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Купон в год", f"{metrics['annual_coupon']:,.0f} ₽")
    with col2:
        st.metric("Купон в месяц", f"{metrics['annual_coupon']/12:,.0f} ₽")
    with col3:
        st.metric("Купон в день", f"{metrics['annual_coupon']/365:,.0f} ₽")

# ==================== ПОЗИЦИИ (КАРТОЧКИ) ====================

elif page == "Позиции":
    st.title("💼 Управление позициями")
    
    # Список всех ОФЗ на Мосбирже
    ALL_OFZ = [
        {'ticker': 'SU26238RMFS4', 'name': 'ОФЗ 26238', 'coupon': 7.1, 'maturity': '2041'},
        {'ticker': 'SU26243RMFS9', 'name': 'ОФЗ 26243', 'coupon': 8.0, 'maturity': '2028'},
        {'ticker': 'SU26244RMFS7', 'name': 'ОФЗ 26244', 'coupon': 8.0, 'maturity': '2030'},
        {'ticker': 'SU26245RMFS4', 'name': 'ОФЗ 26245', 'coupon': 8.0, 'maturity': '2031'},
        {'ticker': 'SU26246RMFS7', 'name': 'ОФЗ 26246', 'coupon': 12.0, 'maturity': '2034'},
        {'ticker': 'SU26247RMFS5', 'name': 'ОФЗ 26247', 'coupon': 12.25, 'maturity': '2034'},
        {'ticker': 'SU26248RMFS3', 'name': 'ОФЗ 26248', 'coupon': 12.25, 'maturity': '2035'},
        {'ticker': 'SU26249RMFS1', 'name': 'ОФЗ 26249', 'coupon': 12.0, 'maturity': '2036'},
        {'ticker': 'SU26250RMFS9', 'name': 'ОФЗ 26250', 'coupon': 12.0, 'maturity': '2037'},
        {'ticker': 'SU26251RMFS7', 'name': 'ОФЗ 26251', 'coupon': 12.0, 'maturity': '2038'},
        {'ticker': 'SU26252RMFS5', 'name': 'ОФЗ 26252', 'coupon': 12.0, 'maturity': '2039'},
        {'ticker': 'SU26253RMFS3', 'name': 'ОФЗ 26253', 'coupon': 12.0, 'maturity': '2040'},
        {'ticker': 'SU26254RMFS1', 'name': 'ОФЗ 26254', 'coupon': 13.0, 'maturity': '2036'},
        {'ticker': 'SU26255RMFS8', 'name': 'ОФЗ 26255', 'coupon': 13.0, 'maturity': '2037'},
        {'ticker': 'SU26256RMFS6', 'name': 'ОФЗ 26256', 'coupon': 13.0, 'maturity': '2038'},
        {'ticker': 'SU26257RMFS4', 'name': 'ОФЗ 26257', 'coupon': 13.0, 'maturity': '2039'},
        {'ticker': 'SU26258RMFS2', 'name': 'ОФЗ 26258', 'coupon': 13.0, 'maturity': '2040'},
        {'ticker': 'SU26259RMFS0', 'name': 'ОФЗ 26259', 'coupon': 13.0, 'maturity': '2041'},
        {'ticker': 'SU26260RMFS5', 'name': 'ОФЗ 26260', 'coupon': 13.0, 'maturity': '2042'},
        {'ticker': 'SU26261RMFS3', 'name': 'ОФЗ 26261', 'coupon': 13.0, 'maturity': '2043'},
        {'ticker': 'SU26262RMFS1', 'name': 'ОФЗ 26262', 'coupon': 13.0, 'maturity': '2044'},
        {'ticker': 'SU26263RMFS9', 'name': 'ОФЗ 26263', 'coupon': 13.0, 'maturity': '2045'},
        {'ticker': 'SU26264RMFS7', 'name': 'ОФЗ 26264', 'coupon': 13.0, 'maturity': '2046'},
        {'ticker': 'SU26265RMFS4', 'name': 'ОФЗ 26265', 'coupon': 13.0, 'maturity': '2047'},
    ]
    
    # Флоатеры (ОФЗ-ПК с переменным купоном)
    FLOATERS = [
        {'ticker': 'SU29014RMFS4', 'name': 'ОФЗ 29014', 'coupon': 'RUONIA', 'maturity': '2028'},
        {'ticker': 'SU29015RMFS1', 'name': 'ОФЗ 29015', 'coupon': 'RUONIA', 'maturity': '2029'},
        {'ticker': 'SU29016RMFS9', 'name': 'ОФЗ 29016', 'coupon': 'RUONIA', 'maturity': '2030'},
        {'ticker': 'SU29017RMFS7', 'name': 'ОФЗ 29017', 'coupon': 'RUONIA', 'maturity': '2031'},
        {'ticker': 'SU29018RMFS5', 'name': 'ОФЗ 29018', 'coupon': 'RUONIA', 'maturity': '2032'},
        {'ticker': 'SU29019RMFS3', 'name': 'ОФЗ 29019', 'coupon': 'RUONIA', 'maturity': '2033'},
        {'ticker': 'SU29020RMFS8', 'name': 'ОФЗ 29020', 'coupon': 'RUONIA', 'maturity': '2034'},
        {'ticker': 'SU29021RMFS6', 'name': 'ОФЗ 29021', 'coupon': 'RUONIA', 'maturity': '2035'},
        {'ticker': 'SU29022RMFS4', 'name': 'ОФЗ 29022', 'coupon': 'RUONIA', 'maturity': '2036'},
        {'ticker': 'SU29023RMFS2', 'name': 'ОФЗ 29023', 'coupon': 'RUONIA', 'maturity': '2037'},
        {'ticker': 'SU29024RMFS0', 'name': 'ОФЗ 29024', 'coupon': 'RUONIA', 'maturity': '2038'},
        {'ticker': 'SU29025RMFS7', 'name': 'ОФЗ 29025', 'coupon': 'RUONIA', 'maturity': '2039'},
    ]
    
    # Получаем текущие цены для всех ОФЗ
    all_tickers = [ofz['ticker'] for ofz in ALL_OFZ + FLOATERS]
    all_prices = get_moex_prices(all_tickers)
    
    # ==================== ТЕКУЩИЙ ПОРТФЕЛЬ ====================
    
    st.subheader("📊 Ваш портфель")
    
    if len(st.session_state.positions) > 0:
        df_display = metrics['details'][['short_name', 'ticker', 'qty', 'buy_price', 'current_price', 'market_value', 'pnl']].copy()
        df_display.columns = ['Облигация', 'Тикер', 'Кол-во', 'Покупка %', 'Сейчас %', 'Стоимость ₽', 'P&L ₽']
        st.dataframe(df_display, use_container_width=True)
    else:
        st.info("Портфель пуст. Добавьте облигации ниже ️")
    
    st.markdown("---")
    
    # ==================== ДОБАВИТЬ ОФЗ С ФИКСИРОВАННЫМ КУПОНОМ ====================
    
    st.subheader("📋 ОФЗ с фиксированным купоном")
    
    # Фильтр
    search_fixed = st.text_input(" Поиск ОФЗ...", key="search_fixed")
    
    # Сетка карточек 3 в ряд
    cols = st.columns(3)
    
    for i, ofz in enumerate(ALL_OFZ):
        if search_fixed and search_fixed.lower() not in ofz['name'].lower():
            continue
        
        col = cols[i % 3]
        with col:
            # Получаем текущую цену
            current_price = all_prices.get(ofz['ticker'])
            price_display = f"{current_price:.2f}%" if current_price else "Нет данных"
            
            # Проверяем есть ли в портфеле
            in_portfolio = None
            for pos in st.session_state.positions:
                if pos['ticker'] == ofz['ticker']:
                    in_portfolio = pos
                    break
            
            # Карточка
            st.markdown(f"""
            <div style='background-color: #f8f9fa; border: 2px solid #e0e0e0; border-radius: 10px; padding: 15px; margin: 5px 0;'>
                <h4 style='margin: 0; color: #000000;'>{ofz['name']}</h4>
                <p style='margin: 5px 0; color: #666666; font-size: 14px;'>Купон: {ofz['coupon']}% | Погашение: {ofz['maturity']}</p>
                <p style='margin: 5px 0; color: #4a90e2; font-weight: bold; font-size: 18px;'>💰 {price_display}</p>
            """, unsafe_allow_html=True)
            
            if in_portfolio:
                st.markdown(f"<p style='margin: 5px 0; color: #00c853;'>✅ В портфеле: {in_portfolio['qty']} шт</p>", unsafe_allow_html=True)
                add_qty = st.number_input("Добавить кол-во", min_value=0, value=0, step=1, key=f"add_qty_{ofz['ticker']}", label_visibility="collapsed")
                if st.button(f"➕ Добавить", key=f"btn_add_{ofz['ticker']}"):
                    if add_qty > 0 and current_price:
                        # Добавляем к существующей позиции (средняя цена)
                        total_qty = in_portfolio['qty'] + add_qty
                        total_cost = (in_portfolio['buy_price'] * in_portfolio['qty']) + (current_price * add_qty)
                        avg_price = total_cost / total_qty
                        
                        in_portfolio['qty'] = total_qty
                        in_portfolio['buy_price'] = avg_price
                        in_portfolio['current_price'] = current_price
                        
                        st.success(f"✅ Добавлено {add_qty} шт по {current_price:.2f}%")
                        st.rerun()
            else:
                add_qty = st.number_input("Количество", min_value=1, value=10, step=1, key=f"new_qty_{ofz['ticker']}", label_visibility="collapsed")
                if st.button(f"🛒 Купить", key=f"btn_buy_{ofz['ticker']}"):
                    if current_price:
                        st.session_state.positions.append({
                            'ticker': ofz['ticker'],
                            'short_name': ofz['name'],
                            'qty': int(add_qty),
                            'buy_price': float(current_price),
                            'coupon_rate': ofz['coupon'] / 100,
                            'duration': 5.0,
                            'maturity_years': int(ofz['maturity']) - 2026 if ofz['maturity'].isdigit() else 5,
                            'current_price': float(current_price)
                        })
                        st.success(f"✅ Куплено {add_qty} шт по {current_price:.2f}%")
                        st.rerun()
            
            st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ==================== ФЛОАТЕРЫ ====================
    
    st.subheader("💧 Флоатеры (ОФЗ-ПК)")
    
    search_float = st.text_input("🔍 Поиск флоатеров...", key="search_float")
    
    cols = st.columns(3)
    
    for i, ofz in enumerate(FLOATERS):
        if search_float and search_float.lower() not in ofz['name'].lower():
            continue
        
        col = cols[i % 3]
        with col:
            current_price = all_prices.get(ofz['ticker'])
            price_display = f"{current_price:.2f}%" if current_price else "Нет данных"
            
            in_portfolio = None
            for pos in st.session_state.positions:
                if pos['ticker'] == ofz['ticker']:
                    in_portfolio = pos
                    break
            
            st.markdown(f"""
            <div style='background-color: #e3f2fd; border: 2px solid #90caf9; border-radius: 10px; padding: 15px; margin: 5px 0;'>
                <h4 style='margin: 0; color: #000000;'>{ofz['name']}</h4>
                <p style='margin: 5px 0; color: #666666; font-size: 14px;'>Купон: {ofz['coupon']} | Погашение: {ofz['maturity']}</p>
                <p style='margin: 5px 0; color: #1976d2; font-weight: bold; font-size: 18px;'>💰 {price_display}</p>
            """, unsafe_allow_html=True)
            
            if in_portfolio:
                st.markdown(f"<p style='margin: 5px 0; color: #00c853;'>✅ В портфеле: {in_portfolio['qty']} шт</p>", unsafe_allow_html=True)
                add_qty = st.number_input("Добавить", min_value=0, value=0, step=1, key=f"add_qty_float_{ofz['ticker']}", label_visibility="collapsed")
                if st.button(f"➕ Добавить", key=f"btn_add_float_{ofz['ticker']}"):
                    if add_qty > 0 and current_price:
                        total_qty = in_portfolio['qty'] + add_qty
                        total_cost = (in_portfolio['buy_price'] * in_portfolio['qty']) + (current_price * add_qty)
                        avg_price = total_cost / total_qty
                        
                        in_portfolio['qty'] = total_qty
                        in_portfolio['buy_price'] = avg_price
                        in_portfolio['current_price'] = current_price
                        
                        st.success(f"✅ Добавлено {add_qty} шт по {current_price:.2f}%")
                        st.rerun()
            else:
                add_qty = st.number_input("Количество", min_value=1, value=10, step=1, key=f"new_qty_float_{ofz['ticker']}", label_visibility="collapsed")
                if st.button(f"🛒 Купить", key=f"btn_buy_float_{ofz['ticker']}"):
                    if current_price:
                        st.session_state.positions.append({
                            'ticker': ofz['ticker'],
                            'short_name': ofz['name'],
                            'qty': int(add_qty),
                            'buy_price': float(current_price),
                            'coupon_rate': 0.10,
                            'duration': 0.5,
                            'maturity_years': int(ofz['maturity']) - 2026 if ofz['maturity'].isdigit() else 5,
                            'current_price': float(current_price)
                        })
                        st.success(f"✅ Куплено {add_qty} шт по {current_price:.2f}%")
                        st.rerun()
            
            st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Кнопка сохранения в облако
    if CLOUD_ENABLED:
        if st.button("💾 Сохранить портфель в облако", type="primary", use_container_width=True):
            if save_to_cloud(st.session_state.positions):
                st.success("✅ Сохранено!")
                st.balloons()
            else:
                st.error("❌ Ошибка сохранения")

# ==================== КУПОННЫЙ КАЛЕНДАРЬ ====================

elif page == "Купонный календарь":
    st.title("📅 Купонный календарь")
    
    st.subheader("💰 Доходы")
    
    annual_coupon = metrics['annual_coupon']
    current_value = metrics['total_value']
    
    with_reinvest_1y = current_value * (1 + annual_coupon/current_value) ** 1 - current_value
    with_reinvest_5y = current_value * (1 + annual_coupon/current_value) ** 5 - current_value
    with_reinvest_10y = current_value * (1 + annual_coupon/current_value) ** 10 - current_value
    
    without_reinvest_1y = annual_coupon * 1
    without_reinvest_5y = annual_coupon * 5
    without_reinvest_10y = annual_coupon * 10
    
    avg_maturity = np.mean([p.get('maturity_years', 5) for p in st.session_state.positions])
    with_reinvest_maturity = current_value * (1 + annual_coupon/current_value) ** avg_maturity - current_value
    without_reinvest_maturity = annual_coupon * avg_maturity
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🔄 С реинвестированием купонов")
        st.metric("За 1 год", f"{with_reinvest_1y:,.0f} ₽")
        st.metric("За 5 лет", f"{with_reinvest_5y:,.0f} ₽")
        st.metric("За 10 лет", f"{with_reinvest_10y:,.0f} ₽")
        st.metric(f"До погашения ({avg_maturity:.0f} лет)", f"{with_reinvest_maturity:,.0f} ₽")
    
    with col2:
        st.markdown("### 💵 Без реинвестирования")
        st.metric("За 1 год", f"{without_reinvest_1y:,.0f} ₽")
        st.metric("За 5 лет", f"{without_reinvest_5y:,.0f} ₽")
        st.metric("За 10 лет", f"{without_reinvest_10y:,.0f} ₽")
        st.metric(f"До погашения ({avg_maturity:.0f} лет)", f"{without_reinvest_maturity:,.0f} ₽")
    
    st.markdown("---")
    
    st.subheader("📈 Моделирование роста портфеля")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        years = st.slider("Период (лет)", 1, 20, 10)
    with col2:
        monthly_investment = st.slider("Ежемесячное пополнение (₽)", 0, 500000, 100000, 10000)
    with col3:
        annual_return = st.slider("Годовая доходность (%)", 0.0, 30.0, 12.0, 0.5)
    
    months = years * 12
    monthly_rate = annual_return / 100 / 12
    
    values_with_reinvest = [current_value]
    for m in range(months):
        new_value = values_with_reinvest[-1] * (1 + monthly_rate) + monthly_investment
        values_with_reinvest.append(new_value)
    
    values_no_return = [current_value]
    for m in range(months):
        new_value = values_no_return[-1] + monthly_investment
        values_no_return.append(new_value)
    
    values_no_action = [current_value]
    for m in range(months):
        new_value = values_no_action[-1] * (1 + monthly_rate)
        values_no_action.append(new_value)
    
    fig = go.Figure()
    months_list = list(range(months + 1))
    
    fig.add_trace(go.Scatter(x=months_list, y=values_with_reinvest, mode='lines', name='С реинвестированием + пополнение', line=dict(color='rgb(46, 204, 113)', width=3)))
    fig.add_trace(go.Scatter(x=months_list, y=values_no_action, mode='lines', name='Только доходность', line=dict(color='rgb(52, 152, 219)', width=3)))
    fig.add_trace(go.Scatter(x=months_list, y=values_no_return, mode='lines', name='Только пополнение', line=dict(color='rgb(231, 76, 60)', width=3)))
    
    fig.update_layout(height=500, template='plotly_white', xaxis_title="Месяцы", yaxis_title="Стоимость портфеля (₽)", hovermode='x unified')
    st.plotly_chart(fig, use_container_width=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("С реинвестированием + пополнение", f"{values_with_reinvest[-1]:,.0f} ₽", f"{values_with_reinvest[-1] - current_value:+,.0f} ₽")
    with col2:
        st.metric("Только доходность", f"{values_no_action[-1]:,.0f} ₽", f"{values_no_action[-1] - current_value:+,.0f} ₽")
    with col3:
        st.metric("Только пополнение", f"{values_no_return[-1]:,.0f} ₽", f"{values_no_return[-1] - current_value:+,.0f} ₽")
    
    st.markdown("---")
    
    st.subheader("📆 Ближайшие выплаты купонов")
    all_coupons = []
    for pos in st.session_state.positions:
        for c in get_coupon_dates(pos['ticker'], pos['coupon_rate'], pos['qty']):
            c['short_name'] = pos['short_name']
            all_coupons.append(c)
    all_coupons = sorted(all_coupons, key=lambda x: x['date'])
    today = datetime.now()
    upcoming = [c for c in all_coupons if c['date'] <= today + timedelta(days=180)]
    
    if upcoming:
        total_up = sum(c['amount'] for c in upcoming)
        st.success(f"Итого за 180 дней: {total_up:,.0f} ₽")
        for c in upcoming:
            days = (c['date'] - today).days
            st.markdown(f"""
            <div class='coupon-upcoming'>
                <h4>{c['short_name']} — {c['date'].strftime('%d.%m.%Y')}</h4>
                <p>💵 {c['amount']:,.2f} ₽ | ⏰ Через {days} дн.</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Нет выплат в ближайшие 180 дней")

# ==================== СТРЕСС-ТЕСТЫ ====================

elif page == "Стресс-тесты":
    st.title("🔥 Стресс-тесты")
    col1, col2 = st.columns(2)
    with col1:
        rate = st.slider("Ставка %", -5.0, 10.0, 0.0, 0.1)
    with col2:
        fx = st.slider("Рубль %", 0.0, 50.0, 0.0, 1.0)
    
    dur = metrics['weighted_duration']
    val = metrics['total_value']
    change = val * (-dur * rate / 100)
    if fx > 0:
        change -= val * (dur * fx * 0.15 / 100)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Текущая", f"{val:,.0f} ₽")
    with col2:
        st.metric("Изменение", f"{change:+,.0f} ₽", f"{(change/val*100):+.2f}%")
    with col3:
        st.metric("Новая", f"{val + change:,.0f} ₽")
    
    st.markdown("---")
    scenarios = [("Сильное снижение", -3.0, 0), ("Умеренное снижение", -1.5, 0), ("Без изменений", 0, 0), ("Небольшой рост", 1.0, 0), ("Значительный рост", 2.0, 0), ("Кризис", 5.0, 20)]
    data = []
    for name, r, f in scenarios:
        ch = val * (-dur * r / 100)
        if f > 0:
            ch -= val * (dur * f * 0.15 / 100)
        data.append({'Сценарий': name, 'Ставка': f"{r:+.1f}%", 'Изменение ₽': f"{ch:+,.0f}", 'Новая ₽': f"{val + ch:,.0f}"})
    st.dataframe(pd.DataFrame(data), use_container_width=True, hide_index=True)

# ==================== ПРОГНОЗ ЦЕЛИ ====================

elif page == "Прогноз цели":
    st.title("🎯 Прогноз цели")
    target = st.number_input("Цель ₽", value=10_000_000, step=100_000)
    monthly = st.number_input("Вложения в месяц ₽", value=100_000, step=10_000)
    
    forecasts = []
    for pos in st.session_state.positions:
        value = pos['qty'] * pos['current_price'] * 10
        coupon = pos['coupon_rate']
        months = 0
        while value < target and months < 600:
            months += 1
            value += monthly
            if months % 6 == 0:
                value += value * coupon / 2
        forecasts.append({'Облигация': pos['short_name'], 'Лет': round(months/12, 1)})
    
    df_f = pd.DataFrame(forecasts).sort_values('Лет')
    st.dataframe(df_f, use_container_width=True, hide_index=True)
    if len(df_f) > 0:
        best = df_f.iloc[0]
        st.success(f"🏆 Лучший: {best['Облигация']} — {best['Лет']:.1f} лет")

# ==================== ИМПОРТ ИЗ БРОКЕРА ====================

elif page == "Импорт из брокера":
    st.title("📥 Импорт из брокера")
    
    st.info("💡 Если импорт не работает — используйте вкладку 'Позиции' для ручного редактирования")
    
    uploaded = st.file_uploader("Загрузить файл", type=['csv', 'html', 'htm', 'xlsx', 'xls'])
    
    if uploaded:
        try:
            df = None
            file_name = uploaded.name.lower()
            
            if file_name.endswith('.csv'):
                try:
                    df = pd.read_csv(uploaded, sep=';', encoding='utf-8')
                except:
                    df = pd.read_csv(uploaded, sep=',', encoding='utf-8')
            elif file_name.endswith(('.html', '.htm')):
                html_content = uploaded.read().decode('utf-8', errors='ignore')
                tables = pd.read_html(html_content)
                if len(tables) > 0:
                    df = max(tables, key=len)
            elif file_name.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(uploaded)
            
            if df is None or len(df) == 0:
                st.error("❌ Не удалось прочитать файл")
                st.stop()
            
            st.success(f"✅ Загружено: {len(df)} строк")
            st.dataframe(df.head(20), use_container_width=True)
            
            st.markdown("---")
            st.subheader("Выберите колонки")
            cols = list(range(len(df.columns)))
            c1, c2, c3 = st.columns(3)
            with c1:
                t_col = st.selectbox("Тикер", cols, key="t_col")
            with c2:
                q_col = st.selectbox("Количество", cols, key="q_col")
            with c3:
                p_col = st.selectbox("Цена", cols, key="p_col")
            
            if st.button(" Импортировать"):
                def clean(v):
                    if pd.isna(v): return 0.0
                    s = str(v).replace(' ', '').replace('₽', '').replace(',', '.')
                    s = ''.join(c for c in s if c.isdigit() or c in '.-')
                    try: return float(s)
                    except: return 0.0
                
                tickers_imp = df.iloc[:, t_col].astype(str).str.strip()
                qtys_imp = df.iloc[:, q_col].apply(clean)
                prices_imp = df.iloc[:, p_col].apply(clean)
                
                mask = tickers_imp.str.contains('ОФЗ|SU|26', case=False, na=False)
                tickers_imp = tickers_imp[mask]
                qtys_imp = qtys_imp[mask]
                prices_imp = prices_imp[mask]
                
                updated = 0
                added = 0
                
                for i in range(len(tickers_imp)):
                    t = tickers_imp.iloc[i]
                    q = int(qtys_imp.iloc[i])
                    p = prices_imp.iloc[i]
                    
                    if not t or t == 'nan' or q == 0 or p == 0 or p > 200:
                        continue
                    
                    found = False
                    for pos in st.session_state.positions:
                        if t in pos['ticker'] or pos['ticker'] in t:
                            pos['qty'] = q
                            pos['buy_price'] = p
                            found = True
                            updated += 1
                            break
                    
                    if not found:
                        name = t
                        m = re.search(r'26\d{3}', t)
                        if m: name = f"ОФЗ {m.group()}"
                        st.session_state.positions.append({
                            'ticker': t, 'short_name': name, 'qty': q,
                            'buy_price': p, 'coupon_rate': 0.10, 'duration': 5.0,
                            'current_price': p, 'maturity_years': 5
                        })
                        added += 1
                
                st.success(f"✅ Обновлено: {updated}, Добавлено: {added}")
                st.rerun()
        
        except Exception as e:
            st.error(f"❌ Ошибка: {e}")
    
    st.markdown("---")
    st.subheader(" Ручное обновление цен покупки")
    
    for i, pos in enumerate(st.session_state.positions):
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"**{pos['short_name']}** ({pos['ticker']})")
        with col2:
            new_price = st.number_input("Цена %", value=float(pos['buy_price']), step=0.1, key=f"manual_{i}", label_visibility="collapsed")
            if st.button("", key=f"save_{i}"):
                st.session_state.positions[i]['buy_price'] = new_price
                st.success("✅")
                st.rerun()

# ==================== ДОСТИЖЕНИЯ ====================

elif page == "Достижения":
    st.title(" Достижения")
    level_name, level_css, next_level, level_msg = get_investor_level(metrics['total_value'])
    stars_count, star_icon = get_star_level(metrics['annual_coupon'])
    
    st.markdown(f"## {level_name}")
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        if metrics['total_value'] < 10_000_000:
            st.progress(min(metrics['total_value'] / next_level, 1.0))
            st.caption(f"{level_msg}: {next_level - metrics['total_value']:,.0f} ₽")
    with col2:
        st.markdown(f'<div class="{level_css}">{level_name}</div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="stars-display">{star_icon} {stars_count}</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    st.subheader("🏆 Достижения")
    achievements = get_achievements(metrics)
    
    left = [a for i, a in enumerate(achievements) if i % 2 == 0]
    right = [a for i, a in enumerate(achievements) if i % 2 != 0]
    
    col1, col2 = st.columns(2)
    
    with col1:
        for a in left:
            if a['unlocked']:
                st.markdown(f"""
                <div class='achievement-card'>
                    <h3>{a['icon']} {a['name']} ✅</h3>
                    <p>{a['description']}</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style='background:#e0e0e0; padding:20px; border-radius:15px; margin:10px 0; opacity:0.6;'>
                    <h3>{a['icon']} {a['name']} 🔒</h3>
                    <p>{a['description']}</p>
                    <p><small>{a['condition']}</small></p>
                </div>
                """, unsafe_allow_html=True)
    
    with col2:
        for a in right:
            if a['unlocked']:
                st.markdown(f"""
                <div class='achievement-card'>
                    <h3>{a['icon']} {a['name']} ✅</h3>
                    <p>{a['description']}</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style='background:#e0e0e0; padding:20px; border-radius:15px; margin:10px 0; opacity:0.6;'>
                    <h3>{a['icon']} {a['name']} 🔒</h3>
                    <p>{a['description']}</p>
                    <p><small>{a['condition']}</small></p>
                </div>
                """, unsafe_allow_html=True)
