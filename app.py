import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import requests
from datetime import datetime, timedelta

st.set_page_config(
    page_title="Mini-Aladdin",
    page_icon="",
    layout="wide"
)

# ==================== CSS СТИЛИ ====================

st.markdown("""
<style>
    /* Адаптивные цвета для светлой и темной темы */
    @media (prefers-color-scheme: light) {
        .main, .main *, body, html { background-color: #ffffff !important; }
        h1, h2, h3, h4, h5, h6, p, span, div, label, li, td, th { color: #000000 !important; }
        div[data-testid="stMetric"] { background-color: #f8f9fa !important; border: 2px solid #e0e0e0 !important; }
        div[data-testid="stMetric"] p { color: #000000 !important; }
        div[data-testid="stMetric"] label { color: #333333 !important; }
        .stDataFrame th { background-color: #f0f0f0 !important; color: #000000 !important; }
        .stDataFrame td { color: #000000 !important; }
    }
    
    @media (prefers-color-scheme: dark) {
        .main, .main *, body, html { background-color: #0e1117 !important; }
        h1, h2, h3, h4, h5, h6, p, span, div, label, li, td, th { color: #ffffff !important; }
        div[data-testid="stMetric"] { background-color: #1e2937 !important; border: 2px solid #313846 !important; }
        div[data-testid="stMetric"] p { color: #ffffff !important; }
        div[data-testid="stMetric"] label { color: #b0b0b0 !important; }
        .stDataFrame th { background-color: #1e2937 !important; color: #ffffff !important; }
        .stDataFrame td { color: #ffffff !important; }
    }
    
    /* Общие стили */
    div[data-testid="stMetric"] { border-radius: 10px !important; padding: 15px !important; }
    div[data-testid="stMetric"] p { font-weight: bold !important; font-size: 24px !important; }
    
    section[data-testid="stSidebar"] { background-color: #1e3a5f !important; }
    section[data-testid="stSidebar"] * { color: #ffffff !important; }
    
    .stButton button {
        background-color: #4a90e2 !important;
        color: #ffffff !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
    }
    
    footer { visibility: hidden; }
    
    /* Стили для уровней */
    .level-badge {
        padding: 10px 20px;
        border-radius: 50px;
        display: inline-block;
        font-size: 20px;
        font-weight: bold;
        margin: 10px 0;
        text-align: center;
        box-shadow: 0 4px 10px rgba(0,0,0,0.2);
    }
    
    /* Цвета уровней */
    .level-novice { background: #e0e0e0; color: #333 !important; }
    .level-epic { background: linear-gradient(135deg, #00c853 0%, #69f0ae 100%); color: white !important; }
    .level-legend { background: linear-gradient(135deg, #ffd700 0%, #ffa000 100%); color: #333 !important; }
    .level-mythic { background: linear-gradient(135deg, #9c27b0 0%, #7c4dff 100%); color: white !important; }
    .level-honor { background: linear-gradient(135deg, #d32f2f 0%, #7b1fa2 100%); color: white !important; }
    .level-glory { background: linear-gradient(135deg, #ff6f00 0%, #ffd700 100%); color: #333 !important; }
    .level-legion { background: linear-gradient(90deg, #ff1744, #d500f9, #2979ff, #00e676); color: white !important; }
    .level-immortal { background: linear-gradient(90deg, #000000, #1a237e, #4a148c, #ffd700); color: #ffd700 !important; animation: pulse 2s infinite; }
    
    @keyframes pulse { 0% { transform: scale(1); } 50% { transform: scale(1.05); } 100% { transform: scale(1); } }
    
    /* Звезды */
    .stars-badge {
        background: #fff9c4;
        border: 2px solid #ffd700;
        padding: 10px 20px;
        border-radius: 50px;
        display: inline-block;
        font-size: 18px;
        font-weight: bold;
        color: #333 !important;
        margin: 10px 0;
    }
    
    @media (max-width: 768px) {
        div[data-testid="stMetric"] p { font-size: 18px !important; }
    }
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
                if val is not None: price = val
            if price is None and 'PREVPRICE' in columns:
                val = rows[0][columns.index('PREVPRICE')]
                if val is not None: price = val
            prices[ticker] = price
        except:
            prices[ticker] = None
    return prices

def get_coupon_dates(ticker, coupon_rate):
    schedule = {
        'SU26238RMFS4': (4, 15, 10, 15), 'SU26246RMFS7': (3, 22, 9, 22),
        'SU26247RMFS5': (5, 18, 11, 18), 'SU26248RMFS3': (2, 12, 8, 12),
        'SU26254RMFS1': (6, 25, 12, 25),
    }
    if ticker not in schedule: return []
    m1, d1, m2, d2 = schedule[ticker]
    amount = 1000 * coupon_rate / 2
    today = datetime.now()
    coupons = []
    for y in range(2):
        for m, d in [(m1, d1), (m2, d2)]:
            dt = datetime(today.year + y, m, d)
            if dt >= today:
                coupons.append({'date': dt, 'amount': amount, 'ticker': ticker})
    return sorted(coupons, key=lambda x: x['date'])[:4]

# ИСПРАВЛЕННАЯ ЛОГИКА УРОВНЕЙ
def get_investor_level(total_value):
    if total_value >= 10_000_000:
        return " Мифический бессмертный", "level-immortal", 10_000_000, "Максимум!"
    elif total_value >= 7_500_000:
        return "⚔️ Мифический легион", "level-legion", 10_000_000, "До Бессмертного"
    elif total_value >= 5_000_000:
        return "🔥 Мифическая слава", "level-glory", 7_500_000, "До Легиона"
    elif total_value >= 2_500_000:
        return " Мифическая честь", "level-honor", 5_000_000, "До Славы"
    elif total_value >= 1_000_000:
        return "🟣 Мифический уровень", "level-mythic", 2_500_000, "До Чести"
    elif total_value >= 750_000:
        return "🟡 Легенда", "level-legend", 1_000_000, "До Мифического"
    elif total_value >= 500_000:
        return "🟢 Эпик", "level-epic", 750_000, "До Легенды"
    else:
        return "🌱 Новичок", "level-novice", 500_000, "До Эпика"

def get_star_level(annual_coupon):
    if annual_coupon >= 1_000_000: return 100, "⭐"
    elif annual_coupon >= 500_000: return 50, "⭐"
    elif annual_coupon >= 250_000: return 25, "⭐"
    else: return 0, "⭐"

def get_achievements(metrics):
    ach = []
    ach.append({'name': 'Первые шаги', 'icon': '👶', 'desc': 'Создать портфель', 'unlocked': True})
    ach.append({'name': 'Сотня', 'icon': '💰', 'desc': '100 000 ₽', 'unlocked': metrics['total_value'] >= 100_000})
    ach.append({'name': 'Полмиллиона', 'icon': '💎', 'desc': '500 000 ₽', 'unlocked': metrics['total_value'] >= 500_000})
    ach.append({'name': 'Миллионер', 'icon': '🤑', 'desc': '1 000 000 ₽', 'unlocked': metrics['total_value'] >= 1_000_000})
    ach.append({'name': 'Эпик', 'icon': '🟢', 'desc': 'Уровень Эпик', 'unlocked': metrics['total_value'] >= 500_000})
    ach.append({'name': 'Легион', 'icon': '️', 'desc': '7 500 000 ₽', 'unlocked': metrics['total_value'] >= 7_500_000})
    ach.append({'name': 'Бессмертный', 'icon': '🌟', 'desc': '10 000 000 ₽', 'unlocked': metrics['total_value'] >= 10_000_000})
    ach.append({'name': '25 Звезд', 'icon': '⭐', 'desc': 'Купон 250к', 'unlocked': metrics['annual_coupon'] >= 250_000})
    ach.append({'name': '50 Звезд', 'icon': '⭐', 'desc': 'Купон 500к', 'unlocked': metrics['annual_coupon'] >= 500_000})
    ach.append({'name': '100 Звезд', 'icon': '⭐', 'desc': 'Купон 1млн', 'unlocked': metrics['annual_coupon'] >= 1_000_000})
    return ach

# ==================== ИНИЦИАЛИЗАЦИЯ ====================

if 'positions' not in st.session_state:
    st.session_state.positions = [
        {'ticker': 'SU26238RMFS4', 'short_name': 'ОФЗ 26238', 'qty': 41, 'buy_price': 59.2, 'coupon_rate': 0.071, 'duration': 7.2},
        {'ticker': 'SU26246RMFS7', 'short_name': 'ОФЗ 26246', 'qty': 65, 'buy_price': 88.4, 'coupon_rate': 0.12, 'duration': 5.6},
        {'ticker': 'SU26247RMFS5', 'short_name': 'ОФЗ 26247', 'qty': 149, 'buy_price': 89.0, 'coupon_rate': 0.1225, 'duration': 6.08},
        {'ticker': 'SU26248RMFS3', 'short_name': 'ОФЗ 26248', 'qty': 174, 'buy_price': 88.1, 'coupon_rate': 0.1225, 'duration': 6.2},
        {'ticker': 'SU26254RMFS1', 'short_name': 'ОФЗ 26254', 'qty': 250, 'buy_price': 93.0, 'coupon_rate': 0.13, 'duration': 6.06}
    ]

tickers = [p['ticker'] for p in st.session_state.positions]
prices = get_moex_prices(tickers)

for p in st.session_state.positions:
    if prices.get(p['ticker']):
        p['current_price'] = prices[p['ticker']]
    elif 'current_price' not in p:
        p['current_price'] = p['buy_price']

df = pd.DataFrame(st.session_state.positions)
df['market_value'] = df['qty'] * df['current_price'] * 10
df['cost_basis'] = df['qty'] * df['buy_price'] * 10
df['pnl'] = df['market_value'] - df['cost_basis']
df['pnl_pct'] = (df['pnl'] / df['cost_basis']) * 100
df['weight'] = df['market_value'] / df['market_value'].sum()

metrics = {
    'total_value': df['market_value'].sum(),
    'total_pnl': df['pnl'].sum(),
    'total_pnl_pct': (df['pnl'].sum() / df['cost_basis'].sum()) * 100,
    'weighted_duration': (df['weight'] * df['duration']).sum(),
    'dv01': df['market_value'].sum() * (df['weight'] * df['duration']).sum() * 0.0001,
    'annual_coupon': (df['qty'] * 1000 * df['coupon_rate']).sum(),
    'details': df
}

level_name, level_css, next_level, level_msg = get_investor_level(metrics['total_value'])
stars_count, star_icon = get_star_level(metrics['annual_coupon'])

# ==================== САЙДБАР ====================

with st.sidebar:
    st.title("Mini-Aladdin")
    st.markdown("---")
    page = st.radio("Навигация", ["Главная", "Позиции", "Купоны", "Стресс-тесты", "Цель", "Импорт", " Достижения"])
    
    st.markdown("---")
    st.markdown(f'<div class="level-badge {level_css}">{level_name}</div>', unsafe_allow_html=True)
    if stars_count > 0:
        st.markdown(f'<div class="stars-badge">{star_icon} {stars_count} звезд</div>', unsafe_allow_html=True)
    
    if st.button("🔄 Обновить цены"):
        st.rerun()

# ==================== СТРАНИЦЫ ====================

if page == "Главная":
    st.title("Обзор портфеля")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("Стоимость", f"{metrics['total_value']:,.0f} ₽", f"{metrics['total_pnl']:+,.0f} ₽")
    with col2: st.metric("Доходность", f"{metrics['total_pnl_pct']:+.2f}%")
    with col3: st.metric("Дюрация", f"{metrics['weighted_duration']:.2f} лет")
    with col4: st.metric("DV01", f"{metrics['dv01']:,.0f} ₽")
    
    st.markdown("---")
    st.subheader("Прогресс к цели 10 000 000 ₽")
    st.progress(min(metrics['total_value'] / 10_000_000, 1.0))
    st.caption(f"{metrics['total_value']:,.0f} ₽ / 10 000 000 ₽")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Распределение")
        fig = px.pie(metrics['details'], values='market_value', names='short_name', hole=0.4)
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        st.subheader("P&L")
        colors = ['green' if x > 0 else 'red' for x in metrics['details']['pnl']]
        fig = go.Figure(go.Bar(y=metrics['details']['short_name'], x=metrics['details']['pnl'], marker_color=colors, orientation='h'))
        st.plotly_chart(fig, use_container_width=True)

elif page == "Позиции":
    st.title("Позиции")
    st.dataframe(metrics['details'][['short_name', 'qty', 'buy_price', 'current_price', 'pnl']], use_container_width=True)
    
    st.subheader("Добавить/Изменить")
    c1, c2 = st.columns(2)
    with c1:
        t = st.text_input("Тикер")
        n = st.text_input("Название")
        q = st.number_input("Кол-во", value=10)
    with c2:
        bp = st.number_input("Цена покупки %", value=90.0)
        cp = st.number_input("Купон %", value=10.0)
        d = st.number_input("Дюрация", value=5.0)
    
    if st.button("Сохранить"):
        if t and n:
            found = False
            for p in st.session_state.positions:
                if p['ticker'] == t:
                    p.update({'short_name': n, 'qty': int(q), 'buy_price': float(bp), 'coupon_rate': float(cp)/100, 'duration': float(d)})
                    found = True
            if not found:
                st.session_state.positions.append({'ticker': t, 'short_name': n, 'qty': int(q), 'buy_price': float(bp), 'coupon_rate': float(cp)/100, 'duration': float(d), 'current_price': float(bp)})
            st.success("Сохранено!")
            st.rerun()

elif page == "Купоны":
    st.title("Купонный календарь")
    st.metric("Годовой купон", f"{metrics['annual_coupon']:,.0f} ₽")
    st.metric("За 10 лет (прогноз)", f"{metrics['annual_coupon'] * 10:,.0f} ₽")
    
    all_c = []
    for p in st.session_state.positions:
        for c in get_coupon_dates(p['ticker'], p['coupon_rate']):
            c['total'] = c['amount'] * p['qty']
            c['name'] = p['short_name']
            all_c.append(c)
    
    for c in sorted(all_c, key=lambda x: x['date']):
        st.write(f"**{c['name']}** — {c['date'].strftime('%d.%m.%Y')} —  {c['total']:,.0f} ₽")

elif page == "Стресс-тесты":
    st.title("Стресс-тесты")
    shock = st.slider("Шок ставки %", -5.0, 10.0, 0.0)
    val = metrics['total_value'] * (-metrics['weighted_duration'] * shock / 100)
    st.metric("Влияние на портфель", f"{val:+,.0f} ₽")

elif page == "Цель":
    st.title("Прогноз цели 10 млн ₽")
    m = st.number_input("Вложения в мес", value=100_000)
    months = 0
    v = metrics['total_value']
    while v < 10_000_000 and months < 600:
        months += 1
        v += m
        if months % 6 == 0: v += v * 0.10 / 2 # Упрощенно
    st.success(f"Достигнете цели через {months/12:.1f} лет")

elif page == "Импорт":
    st.title("Импорт из брокера")
    f = st.file_uploader("Загрузить CSV/HTML", type=['csv', 'html'])
    if f:
        if f.name.endswith('.csv'):
            df_imp = pd.read_csv(f, sep=';')
        else:
            df_imp = pd.read_html(f.read())[0]
        st.dataframe(df_imp.head())
        st.info("Функция импорта в разработке. Пока используйте ручное добавление.")

elif page == "🎮 Достижения":
    st.title("🎮 Достижения")
    
    st.markdown(f"### Уровень: {level_name}")
    st.markdown(f'<div class="level-badge {level_css}">{level_name}</div>', unsafe_allow_html=True)
    
    if stars_count > 0:
        st.markdown(f'<div class="stars-badge">{star_icon} {stars_count} звезд</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    st.subheader("Список достижений")
    
    achievements = get_achievements(metrics)
    
    for a in achievements:
        if a['unlocked']:
            st.success(f"{a['icon']} **{a['name']}** — {a['desc']} ✅")
        else:
            st.info(f"{a['icon']} **{a['name']}** — {a['desc']} 🔒")
