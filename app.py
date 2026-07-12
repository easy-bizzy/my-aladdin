import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import requests
from datetime import datetime, timedelta
import re

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

def get_coupon_dates(ticker, coupon_rate, face_value=1000):
    coupon_schedule = {
        'SU26238RMFS4': (4, 15, 10, 15),
        'SU26246RMFS7': (3, 22, 9, 22),
        'SU26247RMFS5': (5, 18, 11, 18),
        'SU26248RMFS3': (2, 12, 8, 12),
        'SU26254RMFS1': (6, 25, 12, 25),
    }
    if ticker not in coupon_schedule:
        return []
    m1, d1, m2, d2 = coupon_schedule[ticker]
    coupon_amount = face_value * coupon_rate / 2
    today = datetime.now()
    coupons = []
    for year_offset in range(2):
        for month, day in [(m1, d1), (m2, d2)]:
            coupon_date = datetime(today.year + year_offset, month, day)
            if coupon_date >= today:
                coupons.append({'date': coupon_date, 'amount': coupon_amount, 'ticker': ticker})
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
        return "🏆 Мифическая честь", "level-badge-mythic-honor", 5_000_000, "До Славы"
    elif total_value < 7_500_000:
        return "🔥 Мифическая слава", "level-badge-mythic-glory", 7_500_000, "До Легиона"
    elif total_value < 10_000_000:
        return "⚔️ Мифический легион", "level-badge-mythic-legion", 10_000_000, "До Бессмертного"
    else:
        return " Мифический бессмертный", "level-badge-mythic-immortal", 10_000_000, "MAX!"

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
        {'name': 'Полмиллиона', 'icon': '', 'description': '500 000 ₽', 'unlocked': metrics['total_value'] >= 500_000, 'condition': f"{metrics['total_value']:,.0f} / 500 000"},
        {'name': 'Миллионер', 'icon': '🤑', 'description': '1 000 000 ₽', 'unlocked': metrics['total_value'] >= 1_000_000, 'condition': f"{metrics['total_value']:,.0f} / 1 000 000"},
        {'name': 'Диверсификация', 'icon': '📊', 'description': '5 облигаций', 'unlocked': len(st.session_state.positions) >= 5, 'condition': f"{len(st.session_state.positions)} / 5"},
        {'name': 'В плюсе', 'icon': '📈', 'description': 'P&L > 0', 'unlocked': metrics['total_pnl'] > 0, 'condition': f"{metrics['total_pnl']:+,.0f} ₽"},
        {'name': '25 звезд', 'icon': '⭐', 'description': 'Купон 250 000 ₽', 'unlocked': metrics['annual_coupon'] >= 250_000, 'condition': f"{metrics['annual_coupon']:,.0f} / 250 000"},
        {'name': '50 звезд', 'icon': '⭐', 'description': 'Купон 500 000 ₽', 'unlocked': metrics['annual_coupon'] >= 500_000, 'condition': f"{metrics['annual_coupon']:,.0f} / 500 000"},
        {'name': '100 звезд', 'icon': '⭐', 'description': 'Купон 1 000 000 ₽', 'unlocked': metrics['annual_coupon'] >= 1_000_000, 'condition': f"{metrics['annual_coupon']:,.0f} / 1 000 000"},
        {'name': 'Мифический легион', 'icon': '️', 'description': '7 500 000 ₽', 'unlocked': metrics['total_value'] >= 7_500_000, 'condition': f"{metrics['total_value']:,.0f} / 7 500 000"},
        {'name': 'Мифический бессмертный', 'icon': '', 'description': '10 000 000 ₽', 'unlocked': metrics['total_value'] >= 10_000_000, 'condition': f"{metrics['total_value']:,.0f} / 10 000 000"},
    ]

# ==================== ИНИЦИАЛИЗАЦИЯ ====================

DEFAULT_POSITIONS = [
    {'ticker': 'SU26238RMFS4', 'short_name': 'ОФЗ 26238', 'qty': 41, 'buy_price': 59.2, 'coupon_rate': 0.071, 'duration': 7.2, 'maturity_years': 15},
    {'ticker': 'SU26246RMFS7', 'short_name': 'ОФЗ 26246', 'qty': 65, 'buy_price': 88.4, 'coupon_rate': 0.12, 'duration': 5.6, 'maturity_years': 8},
    {'ticker': 'SU26247RMFS5', 'short_name': 'ОФЗ 26247', 'qty': 149, 'buy_price': 89.0, 'coupon_rate': 0.1225, 'duration': 6.08, 'maturity_years': 8},
    {'ticker': 'SU26248RMFS3', 'short_name': 'ОФЗ 26248', 'qty': 174, 'buy_price': 88.1, 'coupon_rate': 0.1225, 'duration': 6.2, 'maturity_years': 9},
    {'ticker': 'SU26254RMFS1', 'short_name': 'ОФЗ 26254', 'qty': 250, 'buy_price': 93.0, 'coupon_rate': 0.13, 'duration': 6.06, 'maturity_years': 10}
]

if 'positions' not in st.session_state or len(st.session_state.positions) == 0:
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
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Стоимость", f"{metrics['total_value']:,.0f} ₽", f"{metrics['total_pnl']:+,.0f} ₽")
    with col2:
        st.metric("Доходность", f"{metrics['total_pnl_pct']:+.2f}%", "vs покупка")
    with col3:
        st.metric("Дюрация", f"{metrics['weighted_duration']:.2f} лет")
    with col4:
        st.metric("DV01", f"{metrics['dv01']:,.0f} ₽")
    
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
    st.subheader("Прогресс к цели 10 000 000 ₽")
    st.progress(min(metrics['total_value'] / 10_000_000, 1.0))
    st.caption(f"{metrics['total_value']:,.0f} ₽ ({metrics['total_value']/10_000_000*100:.1f}%)")
    
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Купон в год", f"{metrics['annual_coupon']:,.0f} ₽")
    with col2:
        st.metric("Купон в месяц", f"{metrics['annual_coupon']/12:,.0f} ₽")
    with col3:
        st.metric("Купон в день", f"{metrics['annual_coupon']/365:,.0f} ₽")

# ==================== ПОЗИЦИИ ====================

elif page == "Позиции":
    st.title("💼 Управление позициями")
    st.subheader("Текущие позиции")
    df_display = metrics['details'][['short_name', 'ticker', 'qty', 'buy_price', 'current_price', 'market_value', 'pnl']].copy()
    df_display.columns = ['Облигация', 'Тикер', 'Кол-во', 'Покупка %', 'Сейчас %', 'Стоимость ₽', 'P&L ₽']
    st.dataframe(df_display, use_container_width=True)
    
    st.markdown("---")
    st.subheader("Редактирование позиции")
    position_options = [f"{pos['short_name']} ({pos['qty']} шт)" for pos in st.session_state.positions]
    selected = st.selectbox("Выберите:", position_options)
    
    if selected:
        idx = position_options.index(selected)
        pos = st.session_state.positions[idx]
        col1, col2, col3 = st.columns(3)
        with col1:
            new_qty = st.number_input("Количество", value=int(pos['qty']), key=f"qty_{idx}")
            new_ticker = st.text_input("Тикер", value=pos['ticker'], key=f"ticker_{idx}")
            new_name = st.text_input("Название", value=pos['short_name'], key=f"name_{idx}")
        with col2:
            new_buy = st.number_input("Цена покупки %", value=float(pos['buy_price']), step=0.1, key=f"buy_{idx}")
            new_coupon = st.number_input("Купон %", value=float(pos['coupon_rate']*100), step=0.1, key=f"coupon_{idx}")
            new_dur = st.number_input("Дюрация", value=float(pos['duration']), step=0.1, key=f"dur_{idx}")
        with col3:
            new_mat = st.number_input("Лет до погашения", value=int(pos.get('maturity_years', 5)), key=f"mat_{idx}")
        
        if st.button("💾 Сохранить"):
            st.session_state.positions[idx] = {
                'ticker': new_ticker, 'short_name': new_name, 'qty': int(new_qty),
                'buy_price': float(new_buy), 'coupon_rate': float(new_coupon)/100,
                'duration': float(new_dur), 'maturity_years': int(new_mat),
                'current_price': pos['current_price']
            }
            st.success("✅ Сохранено!")
            st.rerun()
        
        if st.button("️ Удалить"):
            st.session_state.positions.pop(idx)
            st.success("✅ Удалено!")
            st.rerun()
    
    st.markdown("---")
    st.subheader("Добавить позицию")
    col1, col2 = st.columns(2)
    with col1:
        add_ticker = st.text_input("Тикер", key="add_t")
        add_name = st.text_input("Название", key="add_n")
        add_qty = st.number_input("Кол-во", value=10, key="add_q")
    with col2:
        add_buy = st.number_input("Цена %", value=90.0, key="add_b")
        add_coupon = st.number_input("Купон %", value=10.0, key="add_c")
        add_dur = st.number_input("Дюрация", value=5.0, key="add_d")
        add_mat = st.number_input("Лет до погашения", value=5, key="add_m")
    
    if st.button("➕ Добавить"):
        if add_ticker and add_name:
            st.session_state.positions.append({
                'ticker': add_ticker, 'short_name': add_name, 'qty': int(add_qty),
                'buy_price': float(add_buy), 'coupon_rate': float(add_coupon)/100,
                'duration': float(add_dur), 'maturity_years': int(add_mat),
                'current_price': float(add_buy)
            })
            st.success("✅ Добавлено!")
            st.rerun()

# ==================== КУПОННЫЙ КАЛЕНДАРЬ ====================

elif page == "Купонный календарь":
    st.title("📅 Купонный календарь")
    
    st.subheader("💰 Доход до погашения")
    maturity_data = []
    total_coupons = 0
    total_nominal = 0
    
    for pos in st.session_state.positions:
        mat_years = pos.get('maturity_years', 5)
        coupon_per_year = pos['qty'] * 1000 * pos['coupon_rate']
        total_c = coupon_per_year * mat_years
        nominal = pos['qty'] * 1000
        cost = pos['qty'] * pos['buy_price'] * 10
        profit = total_c + nominal - cost
        total_coupons += total_c
        total_nominal += nominal
        maturity_data.append({
            'Облигация': pos['short_name'],
            'Лет': mat_years,
            'Купоны ₽': f"{total_c:,.0f}",
            'Номинал ₽': f"{nominal:,.0f}",
            'Доход ₽': f"{total_c + nominal:,.0f}",
            'Прибыль ₽': f"{profit:+,.0f}"
        })
    
    st.dataframe(pd.DataFrame(maturity_data), use_container_width=True, hide_index=True)
    
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Всего купонов", f"{total_coupons:,.0f} ₽")
    with col2:
        st.metric("Номинал", f"{total_nominal:,.0f} ₽")
    with col3:
        st.metric("Общий доход", f"{total_coupons + total_nominal:,.0f} ₽")
    
    st.markdown("---")
    st.subheader(" Ближайшие выплаты")
    all_coupons = []
    for pos in st.session_state.positions:
        for c in get_coupon_dates(pos['ticker'], pos['coupon_rate']):
            c['short_name'] = pos['short_name']
            c['total'] = c['amount'] * pos['qty']
            all_coupons.append(c)
    all_coupons = sorted(all_coupons, key=lambda x: x['date'])
    today = datetime.now()
    upcoming = [c for c in all_coupons if c['date'] <= today + timedelta(days=90)]
    
    if upcoming:
        total_up = sum(c['total'] for c in upcoming)
        st.success(f"Итого за 90 дней: {total_up:,.0f} ₽")
        for c in upcoming:
            days = (c['date'] - today).days
            st.markdown(f"""
            <div class='coupon-upcoming'>
                <h4>{c['short_name']} — {c['date'].strftime('%d.%m.%Y')}</h4>
                <p>💵 {c['total']:,.0f} ₽ | ⏰ Через {days} дн.</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Нет выплат в ближайшие 90 дней")

# ==================== СТРЕСС-ТЕСТЫ ====================

elif page == "Стресс-тесты":
    st.title(" Стресс-тесты")
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
    
    st.info(" Если импорт не работает — используйте вкладку 'Позиции' для ручного редактирования")
    
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
            
            if st.button("🚀 Импортировать"):
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
    st.subheader("📝 Ручное обновление цен покупки")
    st.info("Если импорт не работает — обновите цены вручную:")
    
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
    st.title("🎮 Достижения")
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
