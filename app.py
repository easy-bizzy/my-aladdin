import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import requests
from datetime import datetime, timedelta

# ==================== НАСТРОЙКА СТРАНИЦЫ ====================

st.set_page_config(
    page_title="Mini-Aladdin | Портфель ОФЗ",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== CSS СТИЛИ ====================

st.markdown("""
<style>
    /* Принудительный светлый фон */
    .main { background-color: #ffffff !important; }
    .block-container { padding-top: 2rem !important; }
    
    /* Карточки метрик */
    div[data-testid="stMetric"] { 
        background-color: #f8f9fa !important;
        border: 1px solid #e0e0e0 !important;
        border-radius: 10px !important;
        padding: 15px !important;
    }
    div[data-testid="stMetric"] p { color: #000000 !important; font-weight: bold; }
    div[data-testid="stMetric"] label { color: #333333 !important; }
    
    /* Заголовки */
    h1, h2, h3 { color: #000000 !important; }
    p, span, div, label { color: #000000 !important; }
    
    /* Сайдбар */
    section[data-testid="stSidebar"] { background-color: #1e3a5f !important; }
    section[data-testid="stSidebar"] * { color: #ffffff !important; }
    
    /* Кнопки */
    .stButton button {
        background-color: #4a90e2 !important;
        color: #ffffff !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
    }
    
    /* Успех/ошибка */
    .stSuccess { background-color: #d4edda !important; color: #155724 !important; }
    .stError { background-color: #f8d7da !important; color: #721c24 !important; }
    
    /* Скрыть футер */
    footer { visibility: hidden; }
    
    /* Мобильная адаптация */
    @media (max-width: 768px) {
        div[data-testid="stMetric"] p { font-size: 20px !important; }
    }
</style>
""", unsafe_allow_html=True)

# ==================== ИНИЦИАЛИЗАЦИЯ ДАННЫХ ====================

if 'positions' not in st.session_state:
    st.session_state.positions = [
        {'ticker': 'SU26238RMFS4', 'short_name': 'ОФЗ 26238', 'qty': 41, 'buy_price': 59.2, 'coupon_rate': 0.071, 'duration': 7.2},
        {'ticker': 'SU26246RMFS5', 'short_name': 'ОФЗ 26246', 'qty': 65, 'buy_price': 88.4, 'coupon_rate': 0.12, 'duration': 5.6},
        {'ticker': 'SU26247RMFS1', 'short_name': 'ОФЗ 26247', 'qty': 149, 'buy_price': 89.0, 'coupon_rate': 0.1225, 'duration': 6.08},
        {'ticker': 'SU26248RMFS9', 'short_name': 'ОФЗ 26248', 'qty': 174, 'buy_price': 88.1, 'coupon_rate': 0.1225, 'duration': 6.2},
        {'ticker': 'SU26254RMFS6', 'short_name': 'ОФЗ 26254', 'qty': 250, 'buy_price': 93.0, 'coupon_rate': 0.13, 'duration': 6.06}
    ]

# ==================== ПОЛУЧЕНИЕ ЦЕН С MOEX ====================

@st.cache_data(ttl=300)
def get_moex_prices(positions):
    """Получить актуальные цены с Московской биржи"""
    prices = {}
    base_url = "https://iss.moex.com/iss/engines/stock/markets/bonds/boards/TQOB/securities"
    
    for pos in positions:
        try:
            url = f"{base_url}/{pos['ticker']}.json"
            response = requests.get(url, timeout=5)
            data = response.json()
            market_data = data.get('marketdata', {}).get('data', [])
            if market_data and len(market_data[0]) > 12:
                price = market_data[0][12]
                prices[pos['ticker']] = price if price else pos['buy_price']
            else:
                prices[pos['ticker']] = pos['buy_price']
        except:
            prices[pos['ticker']] = pos['buy_price']
    
    return prices

# Обновляем текущие цены
for pos in st.session_state.positions:
    pos['current_price'] = get_moex_prices(st.session_state.positions).get(pos['ticker'], pos['buy_price'])

# ==================== РАСЧЁТ МЕТРИК ====================

df = pd.DataFrame(st.session_state.positions)
df['market_value'] = df['qty'] * df['current_price'] * 10
df['cost_basis'] = df['qty'] * df['buy_price'] * 10
df['pnl'] = df['market_value'] - df['cost_basis']
df['pnl_pct'] = (df['pnl'] / df['cost_basis']) * 100

total_value = df['market_value'].sum()
df['weight'] = df['market_value'] / total_value
weighted_duration = (df['weight'] * df['duration']).sum()
dv01 = total_value * weighted_duration * 0.0001
annual_coupon = (df['qty'] * 1000 * df['coupon_rate']).sum()

metrics = {
    'total_value': total_value,
    'cost_basis': df['cost_basis'].sum(),
    'total_pnl': df['pnl'].sum(),
    'total_pnl_pct': (df['pnl'].sum() / df['cost_basis'].sum()) * 100,
    'weighted_duration': weighted_duration,
    'dv01': dv01,
    'annual_coupon': annual_coupon,
    'details': df
}

# ==================== САЙДБАР ====================

with st.sidebar:
    st.title("📊 Mini-Aladdin")
    st.markdown("---")
    
    page = st.radio(
        "Навигация",
        ["🏠 Главная", "📊 Позиции", "🔥 Стресс-тесты", 
         "🎯 Прогноз цели", "📈 Симуляция RGBI"],
        index=0
    )
    
    st.markdown("---")
    st.caption(f"🔄 Обновлено: {datetime.now().strftime('%H:%M')}")
    
    if st.button("🔄 Обновить цены"):
        st.cache_data.clear()
        st.rerun()

# ==================== ГЛАВНАЯ СТРАНИЦА ====================

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
        fig_pie = px.pie(metrics['details'], values='market_value', 
                        names='short_name', hole=0.4,
                        color_discrete_sequence=px.colors.qualitative.Set3)
        fig_pie.update_layout(height=400)
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        st.subheader("💹 P&L по позициям")
        colors = ['rgb(46, 204, 113)' if x > 0 else 'rgb(231, 76, 60)' 
                  for x in metrics['details']['pnl']]
        fig_bar = go.Figure(go.Bar(
            x=metrics['details']['short_name'],
            y=metrics['details']['pnl'],
            marker_color=colors,
            text=metrics['details']['pnl'].apply(lambda x: f"{x:+,.0f} ₽"),
            textposition='auto'
        ))
        fig_bar.update_layout(height=400, showlegend=False,
                             yaxis_title="Прибыль/Убыток (₽)")
        fig_bar.add_hline(y=0, line_dash="dash")
        st.plotly_chart(fig_bar, use_container_width=True)
    
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

elif page == " Позиции":
    st.title("💼 Управление позициями")
    
    st.subheader(" Текущие позиции")
    display_df = metrics['details'][['short_name', 'qty', 'buy_price', 
                                     'current_price', 'market_value', 'pnl', 'pnl_pct']].copy()
    display_df.columns = ['Облигация', 'Кол-во', 'Покупка %', 'Сейчас %', 
                          'Стоимость ₽', 'P&L ₽', 'P&L %']
    st.dataframe(display_df, use_container_width=True)
    
    st.markdown("---")
    st.subheader("➕ Добавить новую позицию")
    
    col1, col2 = st.columns(2)
    with col1:
        new_ticker = st.text_input("Тикер (например, SU26230RMFS5)", "SU26230RMFS5")
        new_name = st.text_input("Название (например, ОФЗ 26230)", "ОФЗ 26230")
        new_qty = st.number_input("Количество (шт)", min_value=1, value=10)
    
    with col2:
        new_price = st.number_input("Цена покупки (%)", value=90.0, step=0.1)
        new_coupon = st.number_input("Купонная ставка (%)", value=10.0, step=0.1)
        new_duration = st.number_input("Дюрация (лет)", value=5.0, step=0.1)
    
    if st.button("✅ Добавить позицию"):
        st.session_state.positions.append({
            'ticker': new_ticker,
            'short_name': new_name,
            'qty': int(new_qty),
            'buy_price': float(new_price),
            'coupon_rate': float(new_coupon)/100,
            'duration': float(new_duration),
            'current_price': float(new_price)
        })
        st.cache_data.clear()
        st.success(f"✅ Добавлена: {new_name}")
        st.rerun()
    
    st.markdown("---")
    st.subheader("🗑️ Удалить позицию")
    
    options = [f"{pos['short_name']} ({pos['qty']} шт)" 
               for pos in st.session_state.positions]
    position_to_delete = st.selectbox("Выберите позицию", options)
    
    if st.button("❌ Удалить"):
        index = options.index(position_to_delete)
        st.session_state.positions.pop(index)
        st.cache_data.clear()
        st.success("✅ Позиция удалена")
        st.rerun()

# ==================== СТРЕСС-ТЕСТЫ ====================

elif page == "🔥 Стресс-тесты":
    st.title("🔥 Стресс-тестирование")
    st.caption("Моделируйте реакцию портфеля на изменения рынка")
    
    col1, col2 = st.columns(2)
    with col1:
        rate_shock = st.slider("📈 Изменение ключевой ставки (%)", 
                              -5.0, 10.0, 0.0, 0.1)
    with col2:
        fx_shock = st.slider("💱 Ослабление рубля (%)", 
                            0.0, 50.0, 0.0, 1.0)
    
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
        st.metric("💰 Текущая стоимость", f"{current_value:,.0f} ₽")
    with col2:
        st.metric("📊 Изменение", f"{value_change:+,.0f} ₽", f"{change_pct:+.2f}%")
    with col3:
        st.metric("📉 Новая стоимость", f"{new_value:,.0f} ₽")
    
    st.markdown("---")
    st.subheader("📈 Чувствительность к ставке")
    
    rate_range = np.linspace(-5, 10, 100)
    losses = [current_value * (-duration * r / 100) for r in rate_range]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=rate_range, y=losses, mode='lines',
        line=dict(color='rgb(52, 152, 219)', width=3),
        fill='tozeroy',
        fillcolor='rgba(52, 152, 219, 0.1)',
        name='Изменение стоимости'
    ))
    fig.add_trace(go.Scatter(
        x=[rate_shock], y=[value_change], mode='markers',
        marker=dict(size=15, color='red', symbol='circle'),
        name='Ваш сценарий'
    ))
    fig.add_hline(y=0, line_dash="dash", line_color="black")
    fig.update_layout(
        xaxis_title="Изменение ключевой ставки (%)",
        yaxis_title="Изменение стоимости (₽)",
        height=500, template='plotly_white'
    )
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    st.subheader("📋 Готовые сценарии")
    
    scenarios = [
        (" Сильное снижение ставки", -3.0, 0),
        ("🟢 Умеренное снижение", -1.5, 0),
        ("⚪ Ставка без изменений", 0, 0),
        ("🟡 Небольшой рост", 1.0, 0),
        ("🟠 Значительный рост", 2.0, 0),
        ("🔴 Кризис", 5.0, 20),
    ]
    
    scenario_data = []
    for name, rate, fx in scenarios:
        change = current_value * (-duration * rate / 100)
        if fx > 0:
            change -= current_value * (duration * fx * 0.15 / 100)
        scenario_data.append({
            'Сценарий': name,
            'Шок ставки': f"{rate:+.1f}%",
            'Шок валюты': f"{fx:.0f}%",
            'Изменение ₽': f"{change:+,.0f}",
            'Новая стоимость ₽': f"{current_value + change:,.0f}"
        })
    
    st.dataframe(pd.DataFrame(scenario_data), 
                use_container_width=True, hide_index=True)

# ==================== ПРОГНОЗ ЦЕЛИ ====================

elif page == " Прогноз цели":
    st.title("🎯 Прогноз достижения цели")
    
    target = st.number_input("Цель (₽)", value=5_000_000, step=100_000)
    monthly = st.number_input("Ежемесячные вложения (₽)", 
                             value=100_000, step=10_000)
    
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
            'Лет до цели': months / 12,
            'Купон %': f"{coupon*100:.2f}%",
            'Реинвест. купоны ₽': f"{total_coupons:,.0f}"
        })
    
    df_forecast = pd.DataFrame(forecasts).sort_values('Лет до цели')
    
    st.markdown("---")
    st.subheader("⏱️ Время достижения цели по каждой облигации")
    
    fig = go.Figure(go.Bar(
        x=df_forecast['Облигация'],
        y=df_forecast['Лет до цели'],
        marker_color=px.colors.sequential.Viridis[:len(df_forecast)],
        text=df_forecast['Лет до цели'].apply(lambda x: f"{x:.1f} лет"),
        textposition='auto'
    ))
    fig.update_layout(height=400, template='plotly_white', 
                     yaxis_title="Лет")
    st.plotly_chart(fig, use_container_width=True)
    
    st.dataframe(df_forecast, use_container_width=True, hide_index=True)
    
    best = df_forecast.iloc[0]
    st.success(f"🏆 **Лучший выбор:** {best['Облигация']} — достигнете цели за {best['Лет до цели']:.1f} лет")

# ==================== СИМУЛЯЦИЯ RGBI ====================

elif page == "📈 Симуляция RGBI":
    st.title(" Сравнение: RGBI vs Ваш портфель")
    
    months = st.slider("Период симуляции (месяцев)", 3, 60, 12)
    
    np.random.seed(42)
    current = metrics['total_value']
    daily_values = []
    
    for day in range(months * 30):
        ret = np.random.normal(0.12/252, 0.08/np.sqrt(252))
        current *= (1 + ret)
        if day % 30 == 0 and day > 0:
            current += current * 0.10 / 12
        daily_values.append({
            'date': datetime.now() + timedelta(days=day),
            'value': current
        })
    
    rgbi_final = current
    rgbi_return = (rgbi_final - metrics['total_value']) / metrics['total_value'] * 100
    
    ofz_value = metrics['total_value']
    monthly_growth = (metrics['annual_coupon'] / metrics['total_value']) / 12
    for month in range(months):
        ofz_value *= (1 + monthly_growth)
        ofz_value += 100_000
    
    ofz_return = (ofz_value - metrics['total_value']) / metrics['total_value'] * 100
    difference = rgbi_final - ofz_value
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📈 RGBI", f"{rgbi_final:,.0f} ₽", f"{rgbi_return:+.2f}%")
    with col2:
        st.metric("💼 ОФЗ", f"{ofz_value:,.0f} ₽", f"{ofz_return:+.2f}%")
    with col3:
        label = "Перезаработок" if difference > 0 else "Недозаработок"
        st.metric("🆚 Разница", f"{difference:+,.0f} ₽", label)
    
    st.markdown("---")
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=[d['date'] for d in daily_values],
        y=[d['value'] for d in daily_values],
        mode='lines',
        name='RGBI',
        line=dict(color='rgb(52, 152, 219)', width=2)
    ))
    
    ofz_dates = [datetime.now() + timedelta(days=m*30) for m in range(months)]
    fig.add_trace(go.Scatter(
        x=ofz_dates,
        y=[metrics['total_value'] * (1 + monthly_growth)**m + 100_000 * m 
           for m in range(months)],
        mode='lines+markers',
        name='ОФЗ',
        line=dict(color='rgb(46, 204, 113)', width=2)
    ))
    
    fig.update_layout(
        height=500, template='plotly_white',
        yaxis_title="Стоимость (₽)",
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)
