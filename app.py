import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import requests
from datetime import datetime, timedelta

# ==================== НАСТРОЙКА СТРАНИЦЫ ====================

st.set_page_config(
    page_title="Mini-Aladdin",
    page_icon="📊",
    layout="wide"
)

# ==================== АДАПТИВНЫЙ CSS ====================
# Светлая тема → черный текст на белом фоне
# Темная тема → белый текст на черном фоне

st.markdown("""
<style>
    /* ============================================ */
    /* СВЕТЛАЯ ТЕМА (по умолчанию)                   */
    /* ============================================ */
    @media (prefers-color-scheme: light) {
        .main, .main *, body, html {
            background-color: #ffffff !important;
        }
        h1, h2, h3, h4, h5, h6, p, span, div, label, li, td, th {
            color: #000000 !important;
        }
        div[data-testid="stMetric"] {
            background-color: #f8f9fa !important;
            border: 2px solid #e0e0e0 !important;
        }
        div[data-testid="stMetric"] p {
            color: #000000 !important;
        }
        div[data-testid="stMetric"] label {
            color: #333333 !important;
        }
        .stDataFrame th {
            background-color: #f0f0f0 !important;
            color: #000000 !important;
        }
        .stDataFrame td {
            color: #000000 !important;
        }
        input, textarea, select {
            background-color: #ffffff !important;
            color: #000000 !important;
        }
    }
    
    /* ============================================ */
    /* ТЕМНАЯ ТЕМА                                   */
    /* ============================================ */
    @media (prefers-color-scheme: dark) {
        .main, .main *, body, html {
            background-color: #0e1117 !important;
        }
        h1, h2, h3, h4, h5, h6, p, span, div, label, li, td, th {
            color: #ffffff !important;
        }
        div[data-testid="stMetric"] {
            background-color: #1e2937 !important;
            border: 2px solid #313846 !important;
        }
        div[data-testid="stMetric"] p {
            color: #ffffff !important;
        }
        div[data-testid="stMetric"] label {
            color: #b0b0b0 !important;
        }
        .stDataFrame th {
            background-color: #1e2937 !important;
            color: #ffffff !important;
        }
        .stDataFrame td {
            color: #ffffff !important;
        }
        input, textarea, select {
            background-color: #1e2937 !important;
            color: #ffffff !important;
        }
        .stSuccess {
            background-color: #0f5132 !important;
            color: #ffffff !important;
        }
        .stError {
            background-color: #842029 !important;
            color: #ffffff !important;
        }
    }
    
    /* ============================================ */
    /* ОБЩИЕ СТИЛИ (для любой темы)                  */
    /* ============================================ */
    div[data-testid="stMetric"] {
        border-radius: 10px !important;
        padding: 15px !important;
    }
    div[data-testid="stMetric"] p {
        font-weight: bold !important;
        font-size: 24px !important;
    }
    div[data-testid="stMetric"] label {
        font-size: 14px !important;
    }
    
    /* Сайдбар - всегда темный с белым текстом */
    section[data-testid="stSidebar"] {
        background-color: #1e3a5f !important;
    }
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] div {
        color: #ffffff !important;
    }
    
    /* Кнопки */
    .stButton button {
        background-color: #4a90e2 !important;
        color: #ffffff !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        padding: 10px 20px !important;
    }
    
    /* Скрыть футер */
    footer { visibility: hidden; }
    
    /* Мобильная адаптация */
    @media (max-width: 768px) {
        div[data-testid="stMetric"] p { font-size: 18px !important; }
        h1 { font-size: 22px !important; }
    }
</style>
""", unsafe_allow_html=True)

# ==================== ФУНКЦИЯ ПОЛУЧЕНИЯ ЦЕН С MOEX ====================

@st.cache_data(ttl=300, show_spinner="🔄 Загрузка цен с Московской биржи...")
def get_moex_prices(tickers):
    """
    Получает актуальные цены с MOEX для списка тикеров.
    Работает даже ночью - использует PREVPRICE если LAST недоступна.
    """
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
            
            # Пробуем получить LAST (текущая цена)
            price = None
            if 'LAST' in columns:
                last_idx = columns.index('LAST')
                val = rows[0][last_idx]
                if val is not None:
                    price = val
            
            # Если LAST = None (биржа закрыта), берем PREVPRICE
            if price is None and 'PREVPRICE' in columns:
                prev_idx = columns.index('PREVPRICE')
                val = rows[0][prev_idx]
                if val is not None:
                    price = val
            
            # Если и этого нет - пробуем LASTTOPREVPRICE
            if price is None and 'LASTTOPREVPRICE' in columns:
                ltp_idx = columns.index('LASTTOPREVPRICE')
                val = rows[0][ltp_idx]
                if val is not None:
                    price = val
            
            prices[ticker] = price
            
        except Exception as e:
            prices[ticker] = None
    
    return prices

# ==================== ИНИЦИАЛИЗАЦИЯ ДАННЫХ ====================

# ВАЖНО: current_price берется С БИРЖИ, а не хардкодится!
if 'positions' not in st.session_state:
    st.session_state.positions = [
        {'ticker': 'SU26238RMFS4', 'short_name': 'ОФЗ 26238', 'qty': 41, 'buy_price': 59.2, 'coupon_rate': 0.071, 'duration': 7.2},
        {'ticker': 'SU26246RMFS5', 'short_name': 'ОФЗ 26246', 'qty': 65, 'buy_price': 88.4, 'coupon_rate': 0.12, 'duration': 5.6},
        {'ticker': 'SU26247RMFS1', 'short_name': 'ОФЗ 26247', 'qty': 149, 'buy_price': 89.0, 'coupon_rate': 0.1225, 'duration': 6.08},
        {'ticker': 'SU26248RMFS9', 'short_name': 'ОФЗ 26248', 'qty': 174, 'buy_price': 88.1, 'coupon_rate': 0.1225, 'duration': 6.2},
        {'ticker': 'SU26254RMFS6', 'short_name': 'ОФЗ 26254', 'qty': 250, 'buy_price': 93.0, 'coupon_rate': 0.13, 'duration': 6.06}
    ]

# ==================== АВТООБНОВЛЕНИЕ ЦЕН ПРИ ОТКРЫТИИ ====================

# Получаем список всех тикеров
tickers = [pos['ticker'] for pos in st.session_state.positions]

# Загружаем цены с биржи (с кэшем 5 минут)
live_prices = get_moex_prices(tickers)

# Обновляем current_price для каждой позиции
for pos in st.session_state.positions:
    price_from_moex = live_prices.get(pos['ticker'])
    if price_from_moex is not None:
        pos['current_price'] = price_from_moex
    elif 'current_price' not in pos or pos['current_price'] is None:
        # Первый запуск - используем цену покупки
        pos['current_price'] = pos['buy_price']

# ==================== РАСЧЁТ МЕТРИК ====================

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
    
    page = st.radio(
        "Навигация",
        ["🏠 Главная", "📊 Позиции", "🔥 Стресс-тесты", "🎯 Прогноз цели"],
        index=0
    )
    
    st.markdown("---")
    st.caption(f"🔄 Обновлено: {datetime.now().strftime('%H:%M')}")
    st.caption(f"📡 Источник: MOEX ISS API")
    
    if st.button("🔄 Обновить цены принудительно"):
        st.cache_data.clear()
        st.rerun()

# ==================== ГЛАВНАЯ ====================

if page == "🏠 Главная":
    st.title("💼 Обзор портфеля")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("💰 Стоимость", f"{metrics['total_value']:,.0f} ₽", 
                 f"{metrics['total_pnl']:+,.0f} ₽")
    
    with col2:
        st.metric("📈 Доходность", f"{metrics['total_pnl_pct']:+.2f}%", "vs покупка")
    
    with col3:
        st.metric("⏱️ Дюрация", f"{metrics['weighted_duration']:.2f} лет", "средневзвеш.")
    
    with col4:
        st.metric("🎯 DV01", f"{metrics['dv01']:,.0f} ₽", "риск на 0.01%")
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Распределение портфеля")
        try:
            fig_pie = px.pie(metrics['details'], values='market_value', 
                            names='short_name', hole=0.4,
                            color_discrete_sequence=px.colors.qualitative.Set3)
            fig_pie.update_layout(height=400, template='plotly_white')
            st.plotly_chart(fig_pie, use_container_width=True)
        except Exception as e:
            st.info("📊 График временно недоступен")
    
    with col2:
        st.subheader("💹 P&L по позициям")
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
            st.info("📊 График временно недоступен")
    
    st.markdown("---")
    st.subheader("🎯 Прогресс к цели 5 000 000 ₽")
    progress = min(metrics['total_value'] / 5_000_000, 1.0)
    st.progress(progress)
    st.caption(f"Достигнуто: {metrics['total_value']:,.0f} ₽ ({progress*100:.1f}%)")
    
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("💵 Купон в год", f"{metrics['annual_coupon']:,.0f} ₽")
    with col2:
        st.metric("💵 Купон в месяц", f"{metrics['annual_coupon']/12:,.0f} ₽")
    with col3:
        st.metric("💵 Купон в день", f"{metrics['annual_coupon']/365:,.0f} ₽")

# ==================== ПОЗИЦИИ ====================

elif page == "📊 Позиции":
    st.title("💼 Управление позициями")
    
    st.subheader("📋 Текущие позиции (цены с MOEX)")
    
    df_display = metrics['details'][['short_name', 'ticker', 'qty', 'buy_price', 
                                     'current_price', 'market_value', 'pnl', 'pnl_pct']].copy()
    df_display.columns = ['Облигация', 'Тикер', 'Кол-во', 'Покупка %', 
                          'Сейчас %', 'Стоимость ₽', 'P&L ₽', 'P&L %']
    st.dataframe(df_display, use_container_width=True)
    
    st.markdown("---")
    
    st.subheader("⚙️ Редактирование позиции")
    
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
            if st.button("💾 Сохранить", key=f"save_{idx}"):
                st.session_state.positions[idx] = {
                    'ticker': new_ticker,
                    'short_name': new_name,
                    'qty': int(new_qty),
                    'buy_price': float(new_buy_price),
                    'coupon_rate': float(new_coupon) / 100,
                    'duration': float(new_duration),
                    'current_price': pos['current_price']
                }
                st.success(f"✅ Позиция '{new_name}' обновлена!")
                st.rerun()
        
        with col_btn2:
            if st.button("🗑️ Удалить", key=f"delete_{idx}"):
                name = pos['short_name']
                st.session_state.positions.pop(idx)
                st.success(f"✅ Позиция '{name}' удалена!")
                st.rerun()
    
    st.markdown("---")
    
    st.subheader("➕ Добавить новую позицию")
    
    col1, col2 = st.columns(2)
    
    with col1:
        add_ticker = st.text_input("Тикер (SU...)", "", key="add_ticker")
        add_name = st.text_input("Название", "", key="add_name")
        add_qty = st.number_input("Количество", min_value=1, value=10, key="add_qty")
    
    with col2:
        add_buy_price = st.number_input("Цена покупки (%)", value=90.0, step=0.1, key="add_buy_price")
        add_coupon = st.number_input("Купон (%)", value=10.0, step=0.1, key="add_coupon")
        add_duration = st.number_input("Дюрация (лет)", value=5.0, step=0.1, key="add_duration")
    
    if st.button("✅ Добавить позицию", key="add_position_btn"):
        if add_ticker and add_name:
            st.session_state.positions.append({
                'ticker': add_ticker,
                'short_name': add_name,
                'qty': int(add_qty),
                'buy_price': float(add_buy_price),
                'coupon_rate': float(add_coupon) / 100,
                'duration': float(add_duration),
                'current_price': None  # Загрузится с биржи
            })
            st.success(f"✅ Добавлена: {add_name}")
            st.cache_data.clear()
            st.rerun()
        else:
            st.error("❌ Введите тикер и название!")

# ==================== СТРЕСС-ТЕСТЫ ====================

elif page == "🔥 Стресс-тесты":
    st.title("🔥 Стресс-тестирование")
    
    col1, col2 = st.columns(2)
    with col1:
        rate_shock = st.slider("📈 Изменение ставки (%)", -5.0, 10.0, 0.0, 0.1)
    with col2:
        fx_shock = st.slider("💱 Ослабление рубля (%)", 0.0, 50.0, 0.0, 1.0)
    
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
        st.metric("💰 Текущая", f"{current_value:,.0f} ₽")
    with col2:
        st.metric("📊 Изменение", f"{value_change:+,.0f} ₽", f"{change_pct:+.2f}%")
    with col3:
        st.metric("📉 Новая", f"{new_value:,.0f} ₽")
    
    st.markdown("---")
    st.subheader("📋 Готовые сценарии")
    
    scenarios = [
        ("🟢 Сильное снижение", -3.0, 0),
        ("
