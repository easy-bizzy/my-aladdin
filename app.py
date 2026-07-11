import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# ==================== НАСТРОЙКА СТРАНИЦЫ ====================

st.set_page_config(
    page_title="Mini-Aladdin",
    page_icon="📊",
    layout="wide"
)

# ==================== CSS - АДАПТИВНЫЙ ТЕКСТ ====================

st.markdown("""
<style>
    /* Принудительно СВЕТЛЫЙ фон для всего приложения */
    .main, .main *, body, html {
        background-color: #ffffff !important;
    }
    
    /* Весь текст - ЧЕРНЫЙ на белом фоне */
    h1, h2, h3, h4, h5, h6, p, span, div, label, li, td, th {
        color: #000000 !important;
    }
    
    /* Карточки метрик */
    div[data-testid="stMetric"] { 
        background-color: #f8f9fa !important;
        border: 2px solid #e0e0e0 !important;
        border-radius: 10px !important;
        padding: 15px !important;
    }
    div[data-testid="stMetric"] p { 
        color: #000000 !important; 
        font-weight: bold !important;
        font-size: 24px !important;
    }
    div[data-testid="stMetric"] label { 
        color: #333333 !important; 
        font-size: 14px !important;
    }
    
    /* Сайдбар - темный фон, БЕЛЫЙ текст */
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
    
    /* Поля ввода */
    input, textarea, select {
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 2px solid #d0d0d0 !important;
    }
    
    /* Таблицы */
    .stDataFrame, div[data-testid="stDataFrame"] {
        background-color: #ffffff !important;
    }
    .stDataFrame table, div[data-testid="stDataFrame"] table {
        color: #000000 !important;
    }
    .stDataFrame th, div[data-testid="stDataFrame"] th {
        background-color: #f0f0f0 !important;
        color: #000000 !important;
    }
    .stDataFrame td, div[data-testid="stDataFrame"] td {
        color: #000000 !important;
    }
    
    /* Success/Error блоки */
    .stSuccess {
        background-color: #d4edda !important;
        color: #155724 !important;
        border-radius: 8px !important;
        padding: 15px !important;
    }
    .stError {
        background-color: #f8d7da !important;
        color: #721c24 !important;
        border-radius: 8px !important;
        padding: 15px !important;
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

# ==================== ИНИЦИАЛИЗАЦИЯ ДАННЫХ ====================

if 'positions' not in st.session_state:
    st.session_state.positions = [
        {'ticker': 'SU26238RMFS4', 'short_name': 'ОФЗ 26238', 'qty': 41, 'buy_price': 59.2, 'coupon_rate': 0.071, 'duration': 7.2, 'current_price': 62.5},
        {'ticker': 'SU26246RMFS5', 'short_name': 'ОФЗ 26246', 'qty': 65, 'buy_price': 88.4, 'coupon_rate': 0.12, 'duration': 5.6, 'current_price': 90.1},
        {'ticker': 'SU26247RMFS1', 'short_name': 'ОФЗ 26247', 'qty': 149, 'buy_price': 89.0, 'coupon_rate': 0.1225, 'duration': 6.08, 'current_price': 91.2},
        {'ticker': 'SU26248RMFS9', 'short_name': 'ОФЗ 26248', 'qty': 174, 'buy_price': 88.1, 'coupon_rate': 0.1225, 'duration': 6.2, 'current_price': 89.8},
        {'ticker': 'SU26254RMFS6', 'short_name': 'ОФЗ 26254', 'qty': 250, 'buy_price': 93.0, 'coupon_rate': 0.13, 'duration': 6.06, 'current_price': 94.5}
    ]

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
        ["🏠 Главная", "📊 Позиции", " Стресс-тесты", " Прогноз цели"],
        index=0
    )
    
    st.markdown("---")
    st.caption(f"🔄 Обновлено: {datetime.now().strftime('%H:%M')}")
    
    # Кнопка обновления цен (опционально)
    if st.button("🔄 Обновить цены с MOEX"):
        try:
            import requests
            base_url = "https://iss.moex.com/iss/engines/stock/markets/bonds/boards/TQOB/securities"
            for pos in st.session_state.positions:
                try:
                    url = f"{base_url}/{pos['ticker']}.json"
                    response = requests.get(url, timeout=5)
                    data = response.json()
                    market_data = data.get('marketdata', {}).get('data', [])
                    if market_data and len(market_data[0]) > 12:
                        price = market_data[0][12]
                        if price:
                            pos['current_price'] = price
                except:
                    pass
            st.success("✅ Цены обновлены!")
            st.rerun()
        except:
            st.error("❌ Ошибка обновления цен")

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
        st.metric("️ Дюрация", f"{metrics['weighted_duration']:.2f} лет", "средневзвеш.")
    
    with col4:
        st.metric("🎯 DV01", f"{metrics['dv01']:,.0f} ₽", "риск на 0.01%")
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader(" Распределение портфеля")
        try:
            fig_pie = px.pie(metrics['details'], values='market_value', 
                            names='short_name', hole=0.4)
            fig_pie.update_layout(height=400, template='plotly_white')
            st.plotly_chart(fig_pie, use_container_width=True)
        except Exception as e:
            st.info("📊 График распределения временно недоступен")
    
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
            st.info(" График P&L временно недоступен")
    
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
        st.metric(" Купон в день", f"{metrics['annual_coupon']/365:,.0f} ₽")

# ==================== ПОЗИЦИИ ====================

elif page == "📊 Позиции":
    st.title("💼 Управление позициями")
    
    st.subheader("📋 Текущие позиции")
    
    df_display = metrics['details'][['short_name', 'qty', 'buy_price', 
                                     'current_price', 'market_value', 'pnl', 'pnl_pct']].copy()
    df_display.columns = ['Облигация', 'Кол-во', 'Покупка %', 'Сейчас %', 
                          'Стоимость ₽', 'P&L ₽', 'P&L %']
    st.dataframe(df_display, use_container_width=True)
    
    st.markdown("---")
    
    st.subheader("⚙️ Управление позициями")
    
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
            if st.button("💾 Сохранить изменения", key=f"save_{idx}"):
                st.session_state.positions[idx] = {
                    'ticker': new_ticker,
                    'short_name': new_name,
                    'qty': int(new_qty),
                    'buy_price': float(new_buy_price),
                    'coupon_rate': float(new_coupon) / 100,
                    'duration': float(new_duration),
                    'current_price': float(pos['current_price'])
                }
                st.success(f"✅ Позиция '{new_name}' обновлена!")
                st.rerun()
        
        with col_btn2:
            if st.button("🗑️ Удалить позицию", key=f"delete_{idx}"):
                st.session_state.positions.pop(idx)
                st.success(f"✅ Позиция '{pos['short_name']}' удалена!")
                st.rerun()
    
    st.markdown("---")
    
    st.subheader("➕ Добавить новую позицию")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        add_ticker = st.text_input("Тикер", "", key="add_ticker")
        add_name = st.text_input("Название", "", key="add_name")
        add_qty = st.number_input("Количество", min_value=1, value=10, key="add_qty")
    
    with col2:
        add_buy_price = st.number_input("Цена покупки (%)", value=90.0, step=0.1, key="add_buy_price")
        add_coupon = st.number_input("Купон (%)", value=10.0, step=0.1, key="add_coupon")
        add_duration = st.number_input("Дюрация (лет)", value=5.0, step=0.1, key="add_duration")
    
    with col3:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("✅ Добавить позицию", key="add_position_btn"):
            if add_ticker and add_name:
                st.session_state.positions.append({
                    'ticker': add_ticker,
                    'short_name': add_name,
                    'qty': int(add_qty),
                    'buy_price': float(add_buy_price),
                    'coupon_rate': float(add_coupon) / 100,
                    'duration': float(add_duration),
                    'current_price': float(add_buy_price)
                })
                st.success(f"✅ Добавлена: {add_name}")
                st.rerun()
            else:
                st.error("❌ Введите тикер и название!")

# ==================== СТРЕСС-ТЕСТЫ ====================

elif page == " Стресс-тесты":
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
        st.metric(" Изменение", f"{value_change:+,.0f} ₽", f"{change_pct:+.2f}%")
    with col3:
        st.metric("📉 Новая", f"{new_value:,.0f} ₽")
    
    st.markdown("---")
    st.subheader("📋 Сценарии")
    
    scenarios = [
        ("🟢 Сильное снижение", -3.0, 0),
        ("🟢 Умеренное снижение", -1.5, 0),
        ("⚪ Без изменений", 0, 0),
        ("🟡 Небольшой рост", 1.0, 0),
        ("🟠 Значительный рост", 2.0, 0),
        (" Кризис", 5.0, 20),
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

elif page == "🎯 Прогноз цели":
    st.title("🎯 Прогноз достижения цели")
    
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
    st.subheader("⏱️ Время достижения цели")
    
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
        st.info("📊 График временно недоступен")
    
    st.dataframe(df_forecast, use_container_width=True, hide_index=True)
    
    if len(df_forecast) > 0:
        best = df_forecast.iloc[0]
        st.success(f"🏆 **Лучший выбор:** {best['Облигация']} — {best['Лет до цели']:.1f} лет")
