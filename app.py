import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import requests
from datetime import datetime, timedelta
import re

st.set_page_config(page_title="Mini-Aladdin", page_icon="📊", layout="wide")

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
    .level-badge-epic { background: linear-gradient(135deg, #00c853 0%, #69f0ae 100%); padding: 15px 30px; border-radius: 50px; display: inline-block; font-size: 22px; font-weight: bold; color: white !important; margin: 10px 0; box-shadow: 0 4px 15px rgba(0, 200, 83, 0.4); }
    .level-badge-legend { background: linear-gradient(135deg, #ffd700 0%, #ffed4e 50%, #ffa000 100%); padding: 15px 30px; border-radius: 50px; display: inline-block; font-size: 22px; font-weight: bold; color: #333 !important; margin: 10px 0; box-shadow: 0 4px 15px rgba(255, 215, 0, 0.5); }
    .level-badge-mythic { background: linear-gradient(135deg, #9c27b0 0%, #e040fb 50%, #7c4dff 100%); padding: 15px 30px; border-radius: 50px; display: inline-block; font-size: 22px; font-weight: bold; color: white !important; margin: 10px 0; box-shadow: 0 4px 15px rgba(156, 39, 176, 0.5); }
    .level-badge-mythic-honor { background: linear-gradient(135deg, #d32f2f 0%, #9c27b0 100%); padding: 15px 30px; border-radius: 50px; display: inline-block; font-size: 22px; font-weight: bold; color: white !important; margin: 10px 0; box-shadow: 0 4px 15px rgba(211, 47, 47, 0.5); }
    .level-badge-mythic-glory { background: linear-gradient(135deg, #ff6f00 0%, #ffd700 50%, #ff6f00 100%); padding: 15px 30px; border-radius: 50px; display: inline-block; font-size: 22px; font-weight: bold; color: #333 !important; margin: 10px 0; box-shadow: 0 4px 15px rgba(255, 111, 0, 0.6); }
    .level-badge-mythic-legion { background: linear-gradient(135deg, #ff1744 0%, #d500f9 33%, #2979ff 66%, #00e676 100%); padding: 15px 30px; border-radius: 50px; display: inline-block; font-size: 22px; font-weight: bold; color: white !important; margin: 10px 0; box-shadow: 0 4px 20px rgba(213, 0, 249, 0.6); }
    .level-badge-mythic-immortal { background: linear-gradient(135deg, #000000 0%, #1a237e 25%, #4a148c 50%, #880e4f 75%, #ffd700 100%); padding: 15px 30px; border-radius: 50px; display: inline-block; font-size: 22px; font-weight: bold; color: #ffd700 !important; margin: 10px 0; box-shadow: 0 4px 25px rgba(255, 215, 0, 0.7); }
    .stars-display { background: linear-gradient(135deg, #fff9c4 0%, #fff176 100%); padding: 15px 25px; border-radius: 15px; display: inline-block; font-size: 20px; font-weight: bold; color: #333 !important; margin: 10px 0; border: 2px solid #ffd700; }
    .achievement-card { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; border-radius: 15px; margin: 10px 0; color: white !important; }
    .achievement-card p, .achievement-card h3, .achievement-card span { color: white !important; }
    .coupon-upcoming { background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); padding: 15px; border-radius: 10px; color: white !important; margin: 5px 0; }
    .coupon-upcoming p, .coupon-upcoming h4 { color: white !important; }
</style>
""", unsafe_allow_html=True)


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
            if price is None and 'WAPRICE' in columns:
                val = rows[0][columns.index('WAPRICE')]
                if val is not None:
                    price = val
            prices[ticker] = price
        except Exception as e:
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
        return "🌱 Новичок", "level-badge-epic", 500_000, "До Эпика осталось"
    elif total_value < 750_000:
        return "🟢 Эпик", "level-badge-epic", 750_000, "До Легенды осталось"
    elif total_value < 1_000_000:
        return " Легенда", "level-badge-legend", 1_000_000, "До Мифического уровня осталось"
    elif total_value < 2_500_000:
        return "🔮 Мифический уровень", "level-badge-mythic", 2_500_000, "До Мифической чести осталось"
    elif total_value < 5_000_000:
        return "🏆 Мифическая честь", "level-badge-mythic-honor", 5_000_000, "До Мифической славы осталось"
    elif total_value < 7_500_000:
        return "🔥 Мифическая слава", "level-badge-mythic-glory", 7_500_000, "До Мифического легиона осталось"
    elif total_value < 10_000_000:
        return "⚔️ Мифический легион", "level-badge-mythic-legion", 10_000_000, "До Мифического бессмертного осталось"
    else:
        return "🌟 Мифический бессмертный", "level-badge-mythic-immortal", 10_000_000, "Максимальный уровень!"


def get_star_level(annual_coupon):
    if annual_coupon >= 1_000_000:
        return 100, "⭐"
    elif annual_coupon >= 500_000:
        return 50, "⭐"
    elif annual_coupon >= 250_000:
        return 25, "⭐"
    else:
        return 0, "⭐"


def get_motivation_message(metrics):
    pnl_pct = metrics['total_pnl_pct']
    if pnl_pct > 10:
        return " Отличная работа! Ваш портфель показывает выдающиеся результаты!"
    elif pnl_pct > 5:
        return "📈 Превосходно! Вы на верном пути к финансовой свободе!"
    elif pnl_pct > 0:
        return "✅ Хороший результат! Продолжайте в том же духе!"
    elif pnl_pct > -5:
        return "💪 Небольшая просадка — это нормально. Долгосрочная стратегия важнее!"
    elif pnl_pct > -10:
        return "🛡️ Рынок штормит, но вы держитесь. Диверсификация — ваш щит!"
    else:
        return "🎓 Время учиться! Изучите стресс-тесты и оптимизируйте портфель."


def get_achievements(metrics):
    achievements = []
    achievements.append({'name': 'Первые шаги', 'icon': '👶', 'description': 'Создать первый портфель', 'unlocked': True, 'condition': 'Всегда открыто'})
    achievements.append({'name': 'Сотня', 'icon': '💰', 'description': 'Накопить 100 000 ₽', 'unlocked': metrics['total_value'] >= 100_000, 'condition': f"{metrics['total_value']:,.0f} / 100 000 ₽"})
    achievements.append({'name': 'Полмиллиона', 'icon': '💎', 'description': 'Накопить 500 000 ₽', 'unlocked': metrics['total_value'] >= 500_000, 'condition': f"{metrics['total_value']:,.0f} / 500 000 ₽"})
    achievements.append({'name': 'Миллионер', 'icon': '🤑', 'description': 'Накопить 1 000 000 ₽', 'unlocked': metrics['total_value'] >= 1_000_000, 'condition': f"{metrics['total_value']:,.0f} / 1 000 000 ₽"})
    achievements.append({'name': 'Диверсификация', 'icon': '📊', 'description': 'Иметь 5 разных облигаций', 'unlocked': len(st.session_state.positions) >= 5, 'condition': f"{len(st.session_state.positions)} / 5 облигаций"})
    achievements.append({'name': 'В плюсе', 'icon': '📈', 'description': 'Портфель в прибыли', 'unlocked': metrics['total_pnl'] > 0, 'condition': f"P&L: {metrics['total_pnl']:+,.0f} ₽"})
    achievements.append({'name': '25 звезд', 'icon': '⭐', 'description': 'Годовой купон 250 000 ₽', 'unlocked': metrics['annual_coupon'] >= 250_000, 'condition': f"{metrics['annual_coupon']:,.0f} / 250 000 ₽"})
    achievements.append({'name': '50 звезд', 'icon': '⭐', 'description': 'Годовой купон 500 000 ₽', 'unlocked': metrics['annual_coupon'] >= 500_000, 'condition': f"{metrics['annual_coupon']:,.0f} / 500 000 ₽"})
    achievements.append({'name': '100 звезд', 'icon': '⭐', 'description': 'Годовой купон 1 000 000 ₽', 'unlocked': metrics['annual_coupon'] >= 1_000_000, 'condition': f"{metrics['annual_coupon']:,.0f} / 1 000 000 ₽"})
    achievements.append({'name': 'Мифический легион', 'icon': '⚔️', 'description': 'Накопить 7 500 000 ₽', 'unlocked': metrics['total_value'] >= 7_500_000, 'condition': f"{metrics['total_value']:,.0f} / 7 500 000 ₽"})
    achievements.append({'name': 'Мифический бессмертный', 'icon': '🌟', 'description': 'Накопить 10 000 000 ₽', 'unlocked': metrics['total_value'] >= 10_000_000, 'condition': f"{metrics['total_value']:,.0f} / 10 000 000 ₽"})
    return achievements


if 'positions' not in st.session_state:
    st.session_state.positions = [
        {'ticker': 'SU26238RMFS4', 'short_name': 'ОФЗ 26238', 'qty': 41, 'buy_price': 59.2, 'coupon_rate': 0.071, 'duration': 7.2, 'maturity_years': 15},
        {'ticker': 'SU26246RMFS7', 'short_name': 'ОФЗ 26246', 'qty': 65, 'buy_price': 88.4, 'coupon_rate': 0.12, 'duration': 5.6, 'maturity_years': 8},
        {'ticker': 'SU26247RMFS5', 'short_name': 'ОФЗ 26247', 'qty': 149, 'buy_price': 89.0, 'coupon_rate': 0.1225, 'duration': 6.08, 'maturity_years': 8},
        {'ticker': 'SU26248RMFS3', 'short_name': 'ОФЗ 26248', 'qty': 174, 'buy_price': 88.1, 'coupon_rate': 0.1225, 'duration': 6.2, 'maturity_years': 9},
        {'ticker': 'SU26254RMFS1', 'short_name': 'ОФЗ 26254', 'qty': 250, 'buy_price': 93.0, 'coupon_rate': 0.13, 'duration': 6.06, 'maturity_years': 10}
    ]

tickers = [pos['ticker'] for pos in st.session_state.positions]
live_prices = get_moex_prices(tickers)
price_update_time = datetime.now()

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
        "Навигация",
        ["Главная", "Позиции", "Купонный календарь", "Стресс-тесты", "Прогноз цели", "Импорт из брокера", "Достижения"],
        index=0
    )
    st.markdown("---")
    st.caption(f"Цены обновлены: {price_update_time.strftime('%H:%M:%S')}")
    level_name, level_css, next_level, _ = get_investor_level(metrics['total_value'])
    st.caption(f"Уровень: {level_name}")
    stars_count, star_icon = get_star_level(metrics['annual_coupon'])
    if stars_count > 0:
        st.caption(f"Звезды: {star_icon} {stars_count}")
    if st.button("Обновить цены"):
        st.rerun()


if page == "Главная":
    st.title("Обзор портфеля")
    motivation = get_motivation_message(metrics)
    st.info(motivation)
    
    level_name, level_css, next_level, level_msg = get_investor_level(metrics['total_value'])
    stars_count, star_icon = get_star_level(metrics['annual_coupon'])
    
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.markdown(f"### Ваш уровень: {level_name}")
        if metrics['total_value'] < 10_000_000:
            progress_to_next = min(metrics['total_value'] / next_level, 1.0)
            st.progress(progress_to_next)
            st.caption(f"{level_msg}: {next_level - metrics['total_value']:,.0f} ₽")
        else:
            st.caption("🌟 Максимальный уровень достигнут!")
    with col2:
        st.markdown(f'<div class="{level_css}">{level_name}</div>', unsafe_allow_html=True)
    with col3:
        if stars_count > 0:
            st.markdown(f'<div class="stars-display">{star_icon} {stars_count} звезд</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="stars-display">⭐ 0 звезд</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Стоимость", f"{metrics['total_value']:,.0f} ₽", f"{metrics['total_pnl']:+,.0f} ₽")
    with col2:
        st.metric("Доходность", f"{metrics['total_pnl_pct']:+.2f}%", "vs покупка")
    with col3:
        st.metric("Дюрация", f"{metrics['weighted_duration']:.2f} лет", "средневзвеш.")
    with col4:
        st.metric("DV01", f"{metrics['dv01']:,.0f} ₽", "риск на 0.01%")
    
    st.markdown("---")
    st.subheader("Текущие цены облигаций")
    price_df = metrics['details'][['short_name', 'buy_price', 'current_price', 'pnl']].copy()
    price_df.columns = ['Облигация', 'Цена покупки %', 'Текущая цена %', 'P&L (₽)']
    st.dataframe(price_df, use_container_width=True)
    
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Распределение портфеля")
        try:
            fig_pie = px.pie(metrics['details'], values='market_value', names='short_name', hole=0.4, color_discrete_sequence=px.colors.qualitative.Set3)
            fig_pie.update_layout(height=400, template='plotly_white')
            st.plotly_chart(fig_pie, use_container_width=True)
        except Exception as e:
            st.info("График временно недоступен")
    with col2:
        st.subheader("P&L по позициям (в рублях)")
        try:
            colors = ['rgb(46, 204, 113)' if x > 0 else 'rgb(231, 76, 60)' for x in metrics['details']['pnl']]
            fig_bar = go.Figure(go.Bar(
                y=metrics['details']['short_name'],
                x=metrics['details']['pnl'],
                marker_color=colors,
                text=metrics['details']['pnl'].apply(lambda x: f"{x:+,.0f} ₽"),
                textposition='outside',
                orientation='h'
            ))
            fig_bar.update_layout(height=400, showlegend=False, template='plotly_white', xaxis_title="Прибыль/Убыток (₽)", yaxis_title="")
            st.plotly_chart(fig_bar, use_container_width=True)
        except Exception as e:
            st.info("График временно недоступен")
    
    st.markdown("---")
    st.subheader("Прогресс к цели 10 000 000 ₽")
    progress = min(metrics['total_value'] / 10_000_000, 1.0)
    st.progress(progress)
    st.caption(f"Достигнуто: {metrics['total_value']:,.0f} ₽ ({progress*100:.1f}%)")
    
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Купон в год", f"{metrics['annual_coupon']:,.0f} ₽")
    with col2:
        st.metric("Купон в месяц", f"{metrics['annual_coupon']/12:,.0f} ₽")
    with col3:
        st.metric("Купон в день", f"{metrics['annual_coupon']/365:,.0f} ₽")


elif page == "Позиции":
    st.title("Управление позициями")
    st.subheader("Текущие позиции (цены с MOEX)")
    df_display = metrics['details'][['short_name', 'ticker', 'qty', 'buy_price', 'current_price', 'market_value', 'pnl', 'pnl_pct']].copy()
    df_display.columns = ['Облигация', 'Тикер', 'Кол-во', 'Покупка %', 'Сейчас %', 'Стоимость ₽', 'P&L ₽', 'P&L %']
    st.dataframe(df_display, use_container_width=True)
    
    st.markdown("---")
    st.subheader("Редактирование позиции")
    position_options = [f"{pos['short_name']} ({pos['qty']} шт)" for pos in st.session_state.positions]
    selected_position = st.selectbox("Выберите облигацию:", position_options, key="select_position")
    
    if selected_position:
        idx = position_options.index(selected_position)
        pos = st.session_state.positions[idx]
        col1, col2, col3 = st.columns(3)
        with col1:
            new_qty = st.number_input("Количество (шт)", min_value=0, value=int(pos['qty']), step=1, key=f"qty_{idx}")
        with col2:
            new_ticker = st.text_input("Тикер", value=pos['ticker'], key=f"ticker_{idx}")
        with col3:
            new_name = st.text_input("Название", value=pos['short_name'], key=f"name_{idx}")
        col4, col5, col6 = st.columns(3)
        with col4:
            new_buy_price = st.number_input("Цена покупки (%)", value=float(pos['buy_price']), step=0.1, key=f"buy_price_{idx}")
        with col5:
            new_coupon = st.number_input("Купон (%)", value=float(pos['coupon_rate'] * 100), step=0.1, key=f"coupon_{idx}")
        with col6:
            new_duration = st.number_input("Дюрация (лет)", value=float(pos['duration']), step=0.1, key=f"duration_{idx}")
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("Сохранить", key=f"save_{idx}"):
                st.session_state.positions[idx] = {
                    'ticker': new_ticker, 'short_name': new_name, 'qty': int(new_qty),
                    'buy_price': float(new_buy_price), 'coupon_rate': float(new_coupon) / 100,
                    'duration': float(new_duration), 'current_price': pos['current_price'],
                    'maturity_years': pos.get('maturity_years', 5)
                }
                st.success(f"Позиция '{new_name}' обновлена!")
                st.rerun()
        with col_btn2:
            if st.button("Удалить", key=f"delete_{idx}"):
                name = pos['short_name']
                st.session_state.positions.pop(idx)
                st.success(f"Позиция '{name}' удалена!")
                st.rerun()
    
    st.markdown("---")
    st.subheader("Добавить новую позицию")
    col1, col2 = st.columns(2)
    with col1:
        add_ticker = st.text_input("Тикер (SU...)", "", key="add_ticker")
        add_name = st.text_input("Название", "", key="add_name")
        add_qty = st.number_input("Количество", min_value=1, value=10, key="add_qty")
    with col2:
        add_buy_price = st.number_input("Цена покупки (%)", value=90.0, step=0.1, key="add_buy_price")
        add_coupon = st.number_input("Купон (%)", value=10.0, step=0.1, key="add_coupon")
        add_duration = st.number_input("Дюрация (лет)", value=5.0, step=0.1, key="add_duration")
        add_maturity = st.number_input("Лет до погашения", value=5, step=1, key="add_maturity")
    if st.button("Добавить позицию", key="add_position_btn"):
        if add_ticker and add_name:
            st.session_state.positions.append({
                'ticker': add_ticker, 'short_name': add_name, 'qty': int(add_qty),
                'buy_price': float(add_buy_price), 'coupon_rate': float(add_coupon) / 100,
                'duration': float(add_duration), 'current_price': None,
                'maturity_years': int(add_maturity)
            })
            st.success(f"Добавлена: {add_name}")
            st.rerun()
        else:
            st.error("Введите тикер и название!")


elif page == "Купонный календарь":
    st.title("📅 Купонный календарь")
    st.markdown("---")
    
    st.subheader("💰 Доход до погашения каждой облигации")
    maturity_data = []
    total_coupons_all = 0
    total_nominal_all = 0
    total_profit_all = 0
    
    for pos in st.session_state.positions:
        maturity_years = pos.get('maturity_years', 5)
        coupon_per_year = pos['qty'] * 1000 * pos['coupon_rate']
        total_coupons = coupon_per_year * maturity_years
        nominal_return = pos['qty'] * 1000
        current_cost = pos['qty'] * pos['buy_price'] * 10
        total_income = total_coupons + nominal_return
        profit = total_income - current_cost
        profit_pct = (profit / current_cost) * 100 if current_cost > 0 else 0
        
        total_coupons_all += total_coupons
        total_nominal_all += nominal_return
        total_profit_all += profit
        
        maturity_data.append({
            'Облигация': pos['short_name'],
            'Лет до погашения': maturity_years,
            'Купоны всего ₽': total_coupons,
            'Номинал при погашении ₽': nominal_return,
            'Общий доход ₽': total_income,
            'Прибыль ₽': profit,
            'Доходность %': profit_pct
        })
    
    df_maturity = pd.DataFrame(maturity_data)
    df_maturity['Купоны всего ₽'] = df_maturity['Купоны всего ₽'].apply(lambda x: f"{x:,.0f}")
    df_maturity['Номинал при погашении ₽'] = df_maturity['Номинал при погашении ₽'].apply(lambda x: f"{x:,.0f}")
    df_maturity['Общий доход ₽'] = df_maturity['Общий доход ₽'].apply(lambda x: f"{x:,.0f}")
    df_maturity['Прибыль ₽'] = df_maturity['Прибыль ₽'].apply(lambda x: f"{x:+,.0f}")
    df_maturity['Доходность %'] = df_maturity['Доходность %'].apply(lambda x: f"{x:+.1f}%")
    st.dataframe(df_maturity, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    st.subheader("📊 Итоговый доход по всему портфелю до погашения")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Всего купонов", f"{total_coupons_all:,.0f} ₽")
    with col2:
        st.metric("Возврат номинала", f"{total_nominal_all:,.0f} ₽")
    with col3:
        st.metric("Общий доход", f"{total_coupons_all + total_nominal_all:,.0f} ₽")
    with col4:
        st.metric("Чистая прибыль", f"{total_profit_all:+,.0f} ₽")
    
    st.markdown("---")
    st.subheader("📈 Доход по каждой облигации до погашения")
    try:
        fig_income = go.Figure()
        fig_income.add_trace(go.Bar(
            y=[p['short_name'] for p in st.session_state.positions],
            x=[m['Купоны всего ₽'].replace(' ', '').replace(',', '') for m in maturity_data],
            name='Купоны',
            marker_color='rgb(46, 204, 113)',
            orientation='h'
        ))
        fig_income.add_trace(go.Bar(
            y=[p['short_name'] for p in st.session_state.positions],
            x=[m['Номинал при погашении ₽'].replace(' ', '').replace(',', '') for m in maturity_data],
            name='Номинал',
            marker_color='rgb(52, 152, 219)',
            orientation='h'
        ))
        fig_income.update_layout(barmode='stack', height=400, template='plotly_white', xaxis_title="Сумма (₽)", yaxis_title="")
        st.plotly_chart(fig_income, use_container_width=True)
    except Exception as e:
        st.info("График временно недоступен")
    
    st.markdown("---")
    st.subheader("📆 Ближайшие выплаты купонов")
    all_coupons = []
    for pos in st.session_state.positions:
        coupons = get_coupon_dates(pos['ticker'], pos['coupon_rate'])
        for c in coupons:
            c['short_name'] = pos['short_name']
            c['total_amount'] = c['amount'] * pos['qty']
            all_coupons.append(c)
    all_coupons = sorted(all_coupons, key=lambda x: x['date'])
    today = datetime.now()
    upcoming = [c for c in all_coupons if c['date'] <= today + timedelta(days=90)]
    
    st.markdown("### 🔥 Ближайшие 90 дней")
    if upcoming:
        total_upcoming = sum(c['total_amount'] for c in upcoming)
        st.success(f"**Итого к получению: {total_upcoming:,.0f} ₽**")
        for c in upcoming:
            days_until = (c['date'] - today).days
            pos_qty = next((p['qty'] for p in st.session_state.positions if p['ticker'] == c['ticker']), 0)
            st.markdown(f"""
            <div class='coupon-upcoming'>
                <h4>{c['short_name']} — {c['date'].strftime('%d.%m.%Y')}</h4>
                <p>💵 Сумма: {c['total_amount']:,.0f} ₽ ({c['amount']:,.2f} ₽ × {pos_qty} шт)</p>
                <p>⏰ Через {days_until} дн.</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Нет ближайших выплат в течение 90 дней")
    
    st.markdown("---")
    st.markdown("### 📊 Все будущие выплаты")
    coupon_df = pd.DataFrame([
        {
            'Дата': c['date'].strftime('%d.%m.%Y'),
            'Облигация': c['short_name'],
            'Купон на 1 шт': f"{c['amount']:,.2f} ₽",
            'Количество': next((p['qty'] for p in st.session_state.positions if p['ticker'] == c['ticker']), 0),
            'Итого': f"{c['total_amount']:,.0f} ₽"
        }
        for c in all_coupons
    ])
    st.dataframe(coupon_df, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    st.subheader(" Купонный доход по месяцам (12 месяцев)")
    monthly_coupons = {}
    for c in all_coupons:
        if c['date'] <= today + timedelta(days=365):
            month_key = c['date'].strftime('%Y-%m')
            if month_key not in monthly_coupons:
                monthly_coupons[month_key] = 0
            monthly_coupons[month_key] += c['total_amount']
    if monthly_coupons:
        months = sorted(monthly_coupons.keys())
        values = [monthly_coupons[m] for m in months]
        month_labels = [datetime.strptime(m, '%Y-%m').strftime('%b %Y') for m in months]
        fig = go.Figure(go.Bar(
            x=month_labels, y=values, marker_color='rgb(46, 204, 113)',
            text=[f"{v:,.0f} ₽" for v in values], textposition='auto'
        ))
        fig.update_layout(height=400, template='plotly_white', xaxis_title="Месяц", yaxis_title="Сумма купонов (₽)")
        st.plotly_chart(fig, use_container_width=True)


elif page == "Стресс-тесты":
    st.title("Стресс-тестирование")
    col1, col2 = st.columns(2)
    with col1:
        rate_shock = st.slider("Изменение ставки (%)", -5.0, 10.0, 0.0, 0.1)
    with col2:
        fx_shock = st.slider("Ослабление рубля (%)", 0.0, 50.0, 0.0, 1.0)
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
        st.metric("Текущая стоимость", f"{current_value:,.0f} ₽")
    with col2:
        st.metric("Изменение", f"{value_change:+,.0f} ₽", f"{change_pct:+.2f}%")
    with col3:
        st.metric("Новая стоимость", f"{new_value:,.0f} ₽")
    
    st.markdown("---")
    st.subheader("Сценарии")
    scenarios = [
        ("Сильное снижение ставки", -3.0, 0),
        ("Умеренное снижение", -1.5, 0),
        ("Без изменений", 0, 0),
        ("Небольшой рост", 1.0, 0),
        ("Значительный рост", 2.0, 0),
        ("Кризис", 5.0, 20),
    ]
    scenario_data = []
    for name, rate, fx in scenarios:
        change = current_value * (-duration * rate / 100)
        if fx > 0:
            change -= current_value * (duration * fx * 0.15 / 100)
        scenario_data.append({
            'Сценарий': name, 'Шок ставки': f"{rate:+.1f}%",
            'Изменение ₽': f"{change:+,.0f}", 'Новая стоимость ₽': f"{current_value + change:,.0f}"
        })
    st.dataframe(pd.DataFrame(scenario_data), use_container_width=True, hide_index=True)


elif page == "Прогноз цели":
    st.title("Прогноз достижения цели")
    target = st.number_input("Цель (₽)", value=10_000_000, step=100_000)
    monthly = st.number_input("Ежемесячные вложения (₽)", value=100_000, step=10_000)
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
            'Облигация': pos['short_name'],
            'Лет до цели': round(months / 12, 1),
            'Купон %': f"{coupon*100:.2f}%",
            'Реинвест. купоны ₽': f"{total_coupons:,.0f}"
        })
    df_forecast = pd.DataFrame(forecasts).sort_values('Лет до цели')
    st.markdown("---")
    st.subheader("Время достижения цели")
    try:
        fig = go.Figure(go.Bar(
            x=df_forecast['Облигация'], y=df_forecast['Лет до цели'],
            marker_color=px.colors.sequential.Viridis[:len(df_forecast)],
            text=df_forecast['Лет до цели'].apply(lambda x: f"{x:.1f} лет"),
            textposition='auto'
        ))
        fig.update_layout(height=400, template='plotly_white', yaxis_title="Лет")
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.info("График временно недоступен")
    st.dataframe(df_forecast, use_container_width=True, hide_index=True)
    if len(df_forecast) > 0:
        best = df_forecast.iloc[0]
        st.success(f"**Лучший выбор:** {best['Облигация']} — {best['Лет до цели']:.1f} лет")


elif page == "Импорт из брокера":
    st.title("📥 Импорт данных из брокера")
    st.markdown("""
    ### Поддерживаемые форматы:
    - **CSV** — лучший вариант ✅
    - **HTML** — отчеты Тинькофф, Сбер, ВТБ
    - **Excel (XLSX)** — если экспортировали из Excel
    
    ### Как работает импорт:
    1. Загрузите файл
    2. Укажите **номера колонок** (0, 1, 2...)
    3. Нажмите "Применить импорт"
    """)
    st.markdown("---")
    
    uploaded_file = st.file_uploader("Загрузить файл отчета", type=['html', 'htm', 'csv', 'xlsx', 'xls'])
    
    if uploaded_file is not None:
        try:
            df_import = None
            file_name = uploaded_file.name.lower()
            
            if file_name.endswith(('.html', '.htm')):
                html_content = uploaded_file.read().decode('utf-8', errors='ignore')
                tables = pd.read_html(html_content)
                if len(tables) > 0:
                    max_rows = 0
                    best_table_idx = 0
                    for i, table in enumerate(tables):
                        if len(table) > max_rows:
                            max_rows = len(table)
                            best_table_idx = i
                    df_import = tables[best_table_idx].copy()
                    st.success(f"✅ HTML файл обработан! Таблица с {len(df_import)} записями")
                else:
                    st.error("❌ В HTML файле не найдены таблицы")
                    
            elif file_name.endswith('.csv'):
                try:
                    df_import = pd.read_csv(uploaded_file, sep=';', encoding='utf-8')
                except:
                    try:
                        df_import = pd.read_csv(uploaded_file, sep=',', encoding='utf-8')
                    except:
                        df_import = pd.read_csv(uploaded_file, sep='\t', encoding='utf-8')
                st.success(f"✅ CSV файл загружен! Найдено {len(df_import)} записей")
                
            elif file_name.endswith(('.xlsx', '.xls')):
                df_import = pd.read_excel(uploaded_file)
                st.success(f"✅ Excel файл загружен! Найдено {len(df_import)} записей")
            
            if df_import is not None and len(df_import) > 0:
                # ✅ НОВОЕ: показываем превью с НОМЕРАМИ колонок
                st.subheader("Превью данных (с номерами колонок)")
                
                # Создаём копию для отображения с номерами колонок
                df_preview = df_import.head(10).copy()
                df_preview.columns = [f"Колонка {i}: {col}" for i, col in enumerate(df_import.columns)]
                st.dataframe(df_preview, use_container_width=True)
                
                st.markdown("---")
                st.subheader("Выбор колонок по номеру")
                st.info("Укажите номера колонок (начинаются с 0)")
                
                num_cols = len(df_import.columns)
                col_options = list(range(num_cols))
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    ticker_col_idx = st.selectbox("Колонка с тикером/названием", col_options, key="ticker_col_idx")
                with col2:
                    date_col_idx = st.selectbox("Колонка с датой", col_options, key="date_col_idx")
                with col3:
                    qty_col_idx = st.selectbox("Колонка с количеством", col_options, key="qty_col_idx")
                with col4:
                    price_col_idx = st.selectbox("Колонка с ценой", col_options, key="price_col_idx")
                
                # Показываем что выбрано
                st.markdown(f"""
                **Выбрано:**
                - Тикер: колонка {ticker_col_idx} ({df_import.columns[ticker_col_idx]})
                - Дата: колонка {date_col_idx} ({df_import.columns[date_col_idx]})
                - Количество: колонка {qty_col_idx} ({df_import.columns[qty_col_idx]})
                - Цена: колонка {price_col_idx} ({df_import.columns[price_col_idx]})
                """)
                
                if st.button("Применить импорт", type="primary"):
                    # ✅ НОВОЕ: работаем через iloc (по индексам), а не по именам
                    df_filtered = df_import.copy()
                    
                    # Берём данные по индексам колонок
                    tickers = df_filtered.iloc[:, ticker_col_idx].astype(str).str.strip()
                    qtys_raw = df_filtered.iloc[:, qty_col_idx]
                    prices_raw = df_filtered.iloc[:, price_col_idx]
                    
                    # ✅ Функция очистки чисел от текста
                    def clean_number(val):
                        if pd.isna(val):
                            return 0.0
                        s = str(val)
                        # Убираем пробелы (включая неразрывные)
                        s = s.replace(' ', '').replace('\u00a0', '')
                        # Убираем символы валют и ₽
                        s = s.replace('₽', '').replace('руб', '').replace('RUB', '').replace('$', '')
                        # Заменяем запятую на точку (для дробных)
                        s = s.replace(',', '.')
                        # Убираем всё кроме цифр, точки и минуса
                        s = ''.join(c for c in s if c.isdigit() or c in '.-')
                        try:
                            return float(s)
                        except:
                            return 0.0
                    
                    qtys = qtys_raw.apply(clean_number)
                    prices = prices_raw.apply(clean_number)
                    
                    # Создаём DataFrame для группировки
                    df_clean = pd.DataFrame({
                        'ticker': tickers,
                        'qty': qtys,
                        'price': prices
                    })
                    
                    # Группируем по тикеру
                    grouped = df_clean.groupby('ticker').agg({
                        'qty': 'sum',
                        'price': 'mean'
                    }).reset_index()
                    
                    updated_count = 0
                    added_count = 0
                    skipped_count = 0
                    
                    for _, row in grouped.iterrows():
                        ticker = str(row['ticker']).strip()
                        qty = int(float(row['qty']))
                        price = float(row['price'])
                        
                        # Пропускаем пустые
                        if not ticker or ticker == 'nan' or ticker == '' or qty == 0:
                            skipped_count += 1
                            continue
                        
                        found = False
                        for pos in st.session_state.positions:
                            if pos['ticker'] == ticker or ticker in pos['ticker'] or pos['ticker'] in ticker:
                                pos['qty'] = qty
                                pos['buy_price'] = price
                                found = True
                                updated_count += 1
                                break
                        
                        if not found:
                            short_name = ticker
                            match = re.search(r'26\d{3}', ticker)
                            if match:
                                short_name = f"ОФЗ {match.group()}"
                            st.session_state.positions.append({
                                'ticker': ticker,
                                'short_name': short_name,
                                'qty': qty,
                                'buy_price': price,
                                'coupon_rate': 0.10,
                                'duration': 5.0,
                                'current_price': price,
                                'maturity_years': 5
                            })
                            added_count += 1
                    
                    st.success(f"✅ Импорт завершен!")
                    st.info(f"Обновлено: {updated_count} | Добавлено: {added_count} | Пропущено: {skipped_count}")
                    st.rerun()
                    
        except Exception as e:
            st.error(f"❌ Ошибка обработки файла: {e}")
            st.info("Попробуйте конвертировать файл в CSV через Excel")
    
    st.markdown("---")
    st.subheader("Ручное обновление цен покупки")
    for i, pos in enumerate(st.session_state.positions):
        col1, col2, col3 = st.columns([3, 1, 1])
        with col1:
            st.markdown(f"**{pos['short_name']}** ({pos['ticker']})")
        with col2:
            st.markdown(f"Текущая: {pos['buy_price']}%")
        with col3:
            new_price = st.number_input("Новая цена %", value=float(pos['buy_price']), step=0.1, key=f"manual_price_{i}", label_visibility="collapsed")
        if st.button("Обновить", key=f"manual_update_{i}"):
            st.session_state.positions[i]['buy_price'] = new_price
            st.success(f"✅ Цена {pos['short_name']} обновлена!")
            st.rerun()



elif page == "Достижения":
    st.title("🎮 Ваши достижения")
    level_name, level_css, next_level, level_msg = get_investor_level(metrics['total_value'])
    stars_count, star_icon = get_star_level(metrics['annual_coupon'])
    
    st.markdown(f"## Ваш уровень: {level_name}")
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        if metrics['total_value'] < 10_000_000:
            progress_to_next = min(metrics['total_value'] / next_level, 1.0)
            st.progress(progress_to_next)
            st.caption(f"{level_msg}: {next_level - metrics['total_value']:,.0f} ₽")
        else:
            st.caption("🌟 Максимальный уровень!")
    with col2:
        st.markdown(f'<div class="{level_css}">{level_name}</div>', unsafe_allow_html=True)
    with col3:
        if stars_count > 0:
            st.markdown(f'<div class="stars-display">{star_icon} {stars_count} звезд</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="stars-display">⭐ 0 звезд</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    st.subheader(" Статистика")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Всего в портфеле", f"{metrics['total_value']:,.0f} ₽")
    with col2:
        st.metric("Общий P&L", f"{metrics['total_pnl']:+,.0f} ₽")
    with col3:
        st.metric("Облигаций", len(st.session_state.positions))
    with col4:
        achievements = get_achievements(metrics)
        unlocked = sum(1 for a in achievements if a['unlocked'])
        st.metric("Достижений", f"{unlocked}/{len(achievements)}")
    
    st.markdown("---")
    st.subheader(" Достижения")
    achievements = get_achievements(metrics)
    
    left_achievements = [a for i, a in enumerate(achievements) if i % 2 == 0]
    right_achievements = [a for i, a in enumerate(achievements) if i % 2 != 0]
    
    col1, col2 = st.columns(2)
    
    with col1:
        for achievement in left_achievements:
            if achievement['unlocked']:
                st.markdown(f"""
                <div class='achievement-card'>
                    <h3>{achievement['icon']} {achievement['name']} ✅</h3>
                    <p>{achievement['description']}</p>
                    <p><small>Статус: {achievement['condition']}</small></p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style='background-color: #e0e0e0; padding: 20px; border-radius: 15px; margin: 10px 0; opacity: 0.6;'>
                    <h3>{achievement['icon']} {achievement['name']} 🔒</h3>
                    <p>{achievement['description']}</p>
                    <p><small>Прогресс: {achievement['condition']}</small></p>
                </div>
                """, unsafe_allow_html=True)
    
    with col2:
        for achievement in right_achievements:
            if achievement['unlocked']:
                st.markdown(f"""
                <div class='achievement-card'>
                    <h3>{achievement['icon']} {achievement['name']} ✅</h3>
                    <p>{achievement['description']}</p>
                    <p><small>Статус: {achievement['condition']}</small></p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style='background-color: #e0e0e0; padding: 20px; border-radius: 15px; margin: 10px 0; opacity: 0.6;'>
                    <h3>{achievement['icon']} {achievement['name']} 🔒</h3>
                    <p>{achievement['description']}</p>
                    <p><small>Прогресс: {achievement['condition']}</small></p>
                </div>
                """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.subheader("🎯 Следующая цель")
    next_achievement = None
    for a in achievements:
        if not a['unlocked']:
            next_achievement = a
            break
    if next_achievement:
        st.info(f"**{next_achievement['icon']} {next_achievement['name']}** — {next_achievement['description']}")
        st.caption(f"Прогресс: {next_achievement['condition']}")
    else:
        st.success("🎉 Все достижения разблокированы! Вы настоящий мастер инвестиций!")
