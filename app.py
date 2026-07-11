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
    
    .achievement-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 15px;
        margin: 10px 0;
        color: white !important;
    }
    
    .achievement-card p, .achievement-card h3, .achievement-card span {
        color: white !important;
    }
    
    .level-badge {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 15px 30px;
        border-radius: 50px;
        display: inline-block;
        font-size: 24px;
        font-weight: bold;
        color: white !important;
        margin: 20px 0;
    }
    
    .level-badge p, .level-badge span {
        color: white !important;
    }
    
    .streak-fire {
        font-size: 48px;
        text-align: center;
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.1); }
    }
</style>
""", unsafe_allow_html=True)


def get_moex_prices(tickers):
    """Получает цены с MOEX"""
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
            
            if price is None and 'WAPRICE' in columns:
                wap_idx = columns.index('WAPRICE')
                val = rows[0][wap_idx]
                if val is not None:
                    price = val
            
            prices[ticker] = price
            
        except Exception as e:
            prices[ticker] = None
    
    return prices


if 'positions' not in st.session_state:
    st.session_state.positions = [
        {'ticker': 'SU26238RMFS4', 'short_name': 'ОФЗ 26238', 'qty': 41, 'buy_price': 59.2, 'coupon_rate': 0.071, 'duration': 7.2},
        {'ticker': 'SU26246RMFS7', 'short_name': 'ОФЗ 26246', 'qty': 65, 'buy_price': 88.4, 'coupon_rate': 0.12, 'duration': 5.6},
        {'ticker': 'SU26247RMFS5', 'short_name': 'ОФЗ 26247', 'qty': 149, 'buy_price': 89.0, 'coupon_rate': 0.1225, 'duration': 6.08},
        {'ticker': 'SU26248RMFS3', 'short_name': 'ОФЗ 26248', 'qty': 174, 'buy_price': 88.1, 'coupon_rate': 0.1225, 'duration': 6.2},
        {'ticker': 'SU26254RMFS1', 'short_name': 'ОФЗ 26254', 'qty': 250, 'buy_price': 93.0, 'coupon_rate': 0.13, 'duration': 6.06}
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


# ==================== ГЕЙМИФИКАЦИЯ ====================

def get_investor_level(total_value):
    """Определяет уровень инвестора"""
    if total_value >= 5_000_000:
        return "🏆 Легенда", 5_000_000, "Достигнута цель!"
    elif total_value >= 3_000_000:
        return "💎 Мастер", 5_000_000, "До легенды осталось"
    elif total_value >= 2_000_000:
        return "🥇 Эксперт", 3_000_000, "До мастера осталось"
    elif total_value >= 1_000_000:
        return "🥈 Профи", 2_000_000, "До эксперта осталось"
    elif total_value >= 500_000:
        return "🥉 Опытный", 1_000_000, "До профи осталось"
    else:
        return "🌱 Новичок", 500_000, "До опытного осталось"

def get_achievements(metrics):
    """Возвращает список достижений"""
    achievements = []
    
    # Первое достижение
    achievements.append({
        'name': 'Первые шаги',
        'icon': '👶',
        'description': 'Создать первый портфель',
        'unlocked': True,
        'condition': 'Всегда открыто'
    })
    
    # 100к в портфеле
    achievements.append({
        'name': 'Сотня',
        'icon': '💰',
        'description': 'Накопить 100 000 ₽',
        'unlocked': metrics['total_value'] >= 100_000,
        'condition': f"{metrics['total_value']:,.0f} / 100 000 ₽"
    })
    
    # 500к в портфеле
    achievements.append({
        'name': 'Полмиллиона',
        'icon': '💎',
        'description': 'Накопить 500 000 ₽',
        'unlocked': metrics['total_value'] >= 500_000,
        'condition': f"{metrics['total_value']:,.0f} / 500 000 ₽"
    })
    
    # 1 млн
    achievements.append({
        'name': 'Миллионер',
        'icon': '🤑',
        'description': 'Накопить 1 000 000 ₽',
        'unlocked': metrics['total_value'] >= 1_000_000,
        'condition': f"{metrics['total_value']:,.0f} / 1 000 000 ₽"
    })
    
    # 5 облигаций
    achievements.append({
        'name': 'Диверсификация',
        'icon': '📊',
        'description': 'Иметь 5 разных облигаций',
        'unlocked': len(st.session_state.positions) >= 5,
        'condition': f"{len(st.session_state.positions)} / 5 облигаций"
    })
    
    # Положительный P&L
    achievements.append({
        'name': 'В плюсе',
        'icon': '📈',
        'description': 'Портфель в прибыли',
        'unlocked': metrics['total_pnl'] > 0,
        'condition': f"P&L: {metrics['total_pnl']:+,.0f} ₽"
    })
    
    # Купонный доход > 100к
    achievements.append({
        'name': 'Рентьер',
        'icon': '💵',
        'description': 'Годовой купон > 100 000 ₽',
        'unlocked': metrics['annual_coupon'] >= 100_000,
        'condition': f"{metrics['annual_coupon']:,.0f} / 100 000 ₽"
    })
    
    # Низкий DV01
    achievements.append({
        'name': 'Осторожный',
        'icon': '🛡️',
        'description': 'DV01 < 5000 ₽',
        'unlocked': metrics['dv01'] < 5000,
        'condition': f"DV01: {metrics['dv01']:,.0f} ₽"
    })
    
    # Цель достигнута
    achievements.append({
        'name': 'Цель достигнута!',
        'icon': '🎯',
        'description': 'Накопить 5 000 000 ₽',
        'unlocked': metrics['total_value'] >= 5_000_000,
        'condition': f"{metrics['total_value']:,.0f} / 5 000 000 ₽"
    })
    
    return achievements

def get_motivation_message(metrics):
    """Возвращает мотивационное сообщение"""
    pnl_pct = metrics['total_pnl_pct']
    
    if pnl_pct > 10:
        return "🚀 Отличная работа! Ваш портфель показывает выдающиеся результаты!"
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


# ==================== САЙДБАР ====================

with st.sidebar:
    st.title("Mini-Aladdin")
    st.markdown("---")
    
    page = st.radio(
        "Навигация",
        ["Главная", "Позиции", "Стресс-тесты", "Прогноз цели", "🎮 Достижения"],
        index=0
    )
    
    st.markdown("---")
    st.caption(f"Цены обновлены: {price_update_time.strftime('%H:%M:%S')}")
    st.caption(f"Источник: MOEX ISS API")
    
    # Показываем уровень в сайдбаре
    level_name, next_level, _ = get_investor_level(metrics['total_value'])
    st.caption(f"Ваш уровень: {level_name}")
    
    if st.button("Обновить цены"):
        st.rerun()


# ==================== ГЛАВНАЯ ====================

if page == "Главная":
    st.title("Обзор портфеля")
    
    # Мотивационное сообщение
    motivation = get_motivation_message(metrics)
    st.info(motivation)
    
    # Уровень инвестора
    level_name, next_level, level_msg = get_investor_level(metrics['total_value'])
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown(f"### Ваш уровень: {level_name}")
        progress_to_next = min(metrics['total_value'] / next_level, 1.0)
        st.progress(progress_to_next)
        st.caption(f"{level_msg}: {next_level - metrics['total_value']:,.0f} ₽")
    
    with col2:
        st.markdown(f"<div class='level-badge'>{level_name}</div>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Стоимость", f"{metrics['total_value']:,.0f} ₽", 
                 f"{metrics['total_pnl']:+,.0f} ₽")
    
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
            fig_pie = px.pie(metrics['details'], values='market_value', 
                            names='short_name', hole=0.4,
                            color_discrete_sequence=px.colors.qualitative.Set3)
            fig_pie.update_layout(height=400, template='plotly_white')
            st.plotly_chart(fig_pie, use_container_width=True)
        except Exception as e:
            st.info("График временно недоступен")
    
    with col2:
        st.subheader("P&L по позициям (в рублях)")
        try:
            colors = ['rgb(46, 204, 113)' if x > 0 else 'rgb(231, 76, 60)' 
                      for x in metrics['details']['pnl']]
            fig_bar = go.Figure(go.Bar(
                y=metrics['details']['short_name'],
                x=metrics['details']['pnl'],
                marker_color=colors,
                text=metrics['details']['pnl'].apply(lambda x: f"{x:+,.0f} ₽"),
                textposition='outside',
                orientation='h'
            ))
            fig_bar.update_layout(
                height=400, 
                showlegend=False, 
                template='plotly_white',
                xaxis_title="Прибыль/Убыток (₽)",
                yaxis_title=""
            )
            st.plotly_chart(fig_bar, use_container_width=True)
        except Exception as e:
            st.info("График временно недоступен")
    
    st.markdown("---")
    st.subheader("Прогресс к цели 5 000 000 ₽")
    progress = min(metrics['total_value'] / 5_000_000, 1.0)
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


# ==================== ПОЗИЦИИ ====================

elif page == "Позиции":
    st.title("Управление позициями")
    
    st.subheader("Текущие позиции (цены с MOEX)")
    
    df_display = metrics['details'][['short_name', 'ticker', 'qty', 'buy_price', 
                                     'current_price', 'market_value', 'pnl', 'pnl_pct']].copy()
    df_display.columns = ['Облигация', 'Тикер', 'Кол-во', 'Покупка %', 
                          'Сейчас %', 'Стоимость ₽', 'P&L ₽', 'P&L %']
    st.dataframe(df_display, use_container_width=True)
    
    st.markdown("---")
    
    st.subheader("Редактирование позиции")
    
    position_options = [f"{pos['short_name']} ({pos['qty']} шт)" 
                        for pos in st.session_state.positions]
    
    selected_position = st.selectbox(
        "Выберите облигацию:",
        position_options,
        key="select_position"
    )
    
    if selected_position:
        idx = position_options.index(selected_position)
        pos = st.session_state.positions[idx]
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            new_qty = st.number_input(
                "Количество (шт)",
                min_value=0,
                value=int(pos['qty']),
                step=1,
                key=f"qty_{idx}"
            )
        
        with col2:
            new_ticker = st.text_input(
                "Тикер",
                value=pos['ticker'],
                key=f"ticker_{idx}"
            )
        
        with col3:
            new_name = st.text_input(
                "Название",
                value=pos['short_name'],
                key=f"name_{idx}"
            )
        
        col4, col5, col6 = st.columns(3)
        
        with col4:
            new_buy_price = st.number_input(
                "Цена покупки (%)",
                value=float(pos['buy_price']),
                step=0.1,
                key=f"buy_price_{idx}"
            )
        
        with col5:
            new_coupon = st.number_input(
                "Купон (%)",
                value=float(pos['coupon_rate'] * 100),
                step=0.1,
                key=f"coupon_{idx}"
            )
        
        with col6:
            new_duration = st.number_input(
                "Дюрация (лет)",
                value=float(pos['duration']),
                step=0.1,
                key=f"duration_{idx}"
            )
        
        col_btn1, col_btn2 = st.columns(2)
        
        with col_btn1:
            if st.button("Сохранить", key=f"save_{idx}"):
                st.session_state.positions[idx] = {
                    'ticker': new_ticker,
                    'short_name': new_name,
                    'qty': int(new_qty),
                    'buy_price': float(new_buy_price),
                    'coupon_rate': float(new_coupon) / 100,
                    'duration': float(new_duration),
                    'current_price': pos['current_price']
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
    
    if st.button("Добавить позицию", key="add_position_btn"):
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
            st.success(f"Добавлена: {add_name}")
            st.rerun()
        else:
            st.error("Введите тикер и название!")


# ==================== СТРЕСС-ТЕСТЫ ====================

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
            'Сценарий': name,
            'Шок ставки': f"{rate:+.1f}%",
            'Изменение ₽': f"{change:+,.0f}",
            'Новая стоимость ₽': f"{current_value + change:,.0f}"
        })
    
    st.dataframe(pd.DataFrame(scenario_data), use_container_width=True, hide_index=True)


# ==================== ПРОГНОЗ ЦЕЛИ ====================

elif page == "Прогноз цели":
    st.title("Прогноз достижения цели")
    
    target = st.number_input("Цель (₽)", value=5_000_000, step=100_000)
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
            x=df_forecast['Облигация'],
            y=df_forecast['Лет до цели'],
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


# ==================== ДОСТИЖЕНИЯ ====================

elif page == "🎮 Достижения":
    st.title("🎮 Ваши достижения")
    
    # Уровень инвестора
    level_name, next_level, level_msg = get_investor_level(metrics['total_value'])
    
    st.markdown(f"## Ваш уровень: {level_name}")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        progress_to_next = min(metrics['total_value'] / next_level, 1.0)
        st.progress(progress_to_next)
        st.caption(f"{level_msg}: {next_level - metrics['total_value']:,.0f} ₽")
    
    with col2:
        st.markdown(f"<div class='level-badge'>{level_name}</div>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Статистика
    st.subheader("📊 Статистика")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Всего в портфеле", f"{metrics['total_value']:,.0f} ₽")
    
    with col2:
        st.metric("Общий P&L", f"{metrics['total_pnl']:+,.0f} ₽")
    
    with col3:
        st.metric("Количество облигаций", len(st.session_state.positions))
    
    with col4:
        achievements = get_achievements(metrics)
        unlocked = sum(1 for a in achievements if a['unlocked'])
        st.metric("Достижений", f"{unlocked}/{len(achievements)}")
    
    st.markdown("---")
    
    # Достижения
    st.subheader(" Достижения")
    
    achievements = get_achievements(metrics)
    
    col1, col2 = st.columns(2)
    
    for i, achievement in enumerate(achievements):
        with (col1 if i % 2 == 0 else col2):
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
    
    # Следующая цель
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
        st.success(" Все достижения разблокированы! Вы настоящий мастер инвестиций!")
