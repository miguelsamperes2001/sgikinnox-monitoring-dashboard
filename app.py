import streamlit as st
import plotly.graph_objects as go
import time
from datetime import datetime
import sys
from pathlib import Path

# Add modules to path
sys.path.append(str(Path(__file__).parent))

from modules.data_store import DataStore
from modules.modbus_client import ModbusClient
from modules.control_logic import ControlLogic
import config as cfg

# PAGE CONFIG
st.set_page_config(
    page_title="Cerebro SGI - KINNOX",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# INICIALIZACION DE SESSION STATE
def init_session_state():
    if 'data_store' not in st.session_state:
        st.session_state.data_store = DataStore()
    
    if 'modbus_client' not in st.session_state:
        st.session_state.modbus_client = ModbusClient(
            host=cfg.PLC_IP,
            port=cfg.PLC_PORT,
            slave_id=cfg.SLAVE_ID
        )
    
    if 'control_logic' not in st.session_state:
        st.session_state.control_logic = ControlLogic()
    
    if 'demo_mode' not in st.session_state:
        st.session_state.demo_mode = True
    
    if 'last_update' not in st.session_state:
        st.session_state.last_update = datetime.now()
    
    if 'failsafe_active' not in st.session_state:
        st.session_state.failsafe_active = False

init_session_state()

# CUSTOM CSS
st.markdown("""
<style>
    .stApp {
        background-color: #07090f;
        color: #cdd9ee;
    }
    h1, h2, h3 {
        color: #00e5ff !important;
        font-family: 'IBM Plex Mono', monospace;
    }
    [data-testid="stMetricValue"] {
        font-size: 2.5rem;
        color: #00e5ff;
    }
    .mode-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 4px;
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.75rem;
        font-weight: 700;
        border: 1px solid;
    }
    .mode-auto { color: #00e676; border-color: #00e676; background: rgba(0,230,118,0.08); }
    .mode-failsafe { color: #ff1744; border-color: #ff1744; background: rgba(255,23,68,0.12); }
</style>
""", unsafe_allow_html=True)

# SIDEBAR
ds = st.session_state.data_store

with st.sidebar:
    st.markdown("### 🏭 SGI COLOMBIA")
    st.caption("Sistema Cerebro v2")
    
    st.markdown("---")
    st.subheader("🔌 Conexion")
    
    if st.session_state.demo_mode:
        st.warning("🎮 MODO DEMO")
    else:
        if st.session_state.modbus_client.is_connected():
            st.success(f"✅ PLC: {cfg.PLC_IP}")
        else:
            st.error("❌ Desconectado")
    
    st.markdown("---")
    st.subheader("🎛 Control N₂")
    
    mode = ds.get_control_mode()
    mode_class = 'mode-auto' if mode == 'AUTO' else 'mode-failsafe'
    st.markdown(f'<div class="mode-badge {mode_class}">{mode}</div>', unsafe_allow_html=True)
    
    apertura = ds.get_valve_aperture()
    st.metric("Valvula N₂", f"{apertura:.1f}%")
    
    st.markdown("---")
    st.subheader("💰 Ahorro")
    ahorro = ds.get_total_savings()
    st.metric("Sesion", f"${ahorro:.2f}")
    
    n2_total = ds.get_n2_consumed()
    st.metric("N₂", f"{n2_total:.2f} m³")
    
    st.markdown("---")
    st.caption(f"⏱ {st.session_state.last_update.strftime('%H:%M:%S')}")
    st.caption(f"🔄 {ds.tick_count} ciclos")

# MAIN PAGE
st.title("⚙️ CEREBRO SGI v2")
st.markdown("**KINNOX - Linea de Galvanizado Druids**")
st.markdown("_Republica Dominicana_")
st.markdown("---")

# KPIs PRINCIPALES
col1, col2, col3, col4 = st.columns(4)

vel = ds.get_velocity()
with col1:
    st.metric(
        "Velocidad Linea",
        f"{vel:.1f} m/min", 
        delta="Normal" if vel > cfg.VEL_MIN_PRODUCCION else "Detenida"
    )

tz = ds.get_temp_zinc()
tz_ok = cfg.TEMP_ZINC_MIN <= tz <= cfg.TEMP_ZINC_MAX
with col2:
    st.metric(
        "Temperatura Zinc",
        f"{tz:.1f} °C",
        delta="OK" if tz_ok else "Fuera rango",
        delta_color="normal" if tz_ok else "inverse"
    )

with col3:
    st.metric(
        "Valvula N₂",
        f"{apertura:.0f}%",
        delta=mode
    )

with col4:
    st.metric(
        "Ahorro Acumulado",
        f"${ahorro:.2f}",
        delta="Sesion actual"
    )

st.markdown("---")

# ALERTAS
alerts = ds.get_active_alerts()
if alerts:
    st.subheader("🔔 Alertas Activas")
    for alert in alerts:
        level = alert.get('level', 'warning')
        msg = alert.get('message', '')
        if level == 'critical':
            st.error(f"🔴 {msg}")
        else:
            st.warning(f"⚠️ {msg}")
    st.markdown("---")

# GRAFICA
st.subheader("📈 Tendencia (Ultimos 5 min)")

history = ds.get_history(limit=100)

if history:
    timestamps = [h['timestamp'] for h in history]
    velocities = [h.get('velocity', 0) for h in history]
    temps = [h.get('temp_zinc', 0) / 10 for h in history]
    valves = [h.get('valve_aperture', 0) for h in history]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=timestamps, y=velocities,
        name='Velocidad (m/min)',
        line=dict(color='#00e5ff', width=2)
    ))
    fig.add_trace(go.Scatter(
        x=timestamps, y=temps,
        name='Temp Zinc (°C / 10)',
        line=dict(color='#ff6b35', width=2)
    ))
    fig.add_trace(go.Scatter(
        x=timestamps, y=valves,
        name='Valvula N₂ (%)',
        line=dict(color='#00e676', width=2)
    ))
    
    fig.update_layout(
        template='plotly_dark',
        paper_bgcolor='#07090f',
        plot_bgcolor='#0d1117',
        font=dict(family='monospace', color='#4a6080'),
        xaxis=dict(showgrid=True, gridcolor='#1e2d47'),
        yaxis=dict(showgrid=True, gridcolor='#1e2d47'),
        height=350,
        margin=dict(l=20, r=20, t=20, b=20),
        hovermode='x unified',
    )
    
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("📊 Esperando datos historicos...")

# NAVEGACION
st.markdown("---")
st.subheader("🧭 Navegar a:")

nav_cols = st.columns(8)

with nav_cols[0]:
    if st.button("📊 Operativo", use_container_width=True):
        st.switch_page("pages/01_📊_Operativo.py")

with nav_cols[1]:
    if st.button("🎛 Control", use_container_width=True):
        st.switch_page("pages/02_🎛_Control_N2.py")

with nav_cols[2]:
    if st.button("💰 Financiero", use_container_width=True):
        st.switch_page("pages/03_💰_Financiero.py")

with nav_cols[3]:
    if st.button("📡 Modbus", use_container_width=True):
        st.switch_page("pages/04_📡_Modbus.py")

with nav_cols[4]:
    if st.button("🔔 Alertas", use_container_width=True):
        st.switch_page("pages/05_🔔_Alertas.py")

with nav_cols[5]:
    if st.button("🔬 Zinc", use_container_width=True):
        st.switch_page("pages/06_Zinc.py")

with nav_cols[6]:
    if st.button("📊 Resumen", use_container_width=True):
        st.switch_page("pages/07_Resumen_Ejecutivo.py")

with nav_cols[7]:
    if st.button("⚗️ PSA", use_container_width=True):
        st.switch_page("pages/08_PSA_NGP300.py")

# RESUMEN FINANCIERO
st.markdown("---")
st.subheader("💰 Resumen Financiero")

col1, col2, col3 = st.columns(3)

# N2
ahorro_n2_ano = 583904
with col1:
    st.markdown("**Control N₂ (PSA)**")
    st.metric("Ahorro Anual", f"${ahorro_n2_ano:,}")
    st.caption("Proyeccion NGP+300")

# Zinc
ahorro_zinc_ano = 89267
with col2:
    st.markdown("**Optimizacion Zinc**")
    st.metric("Ahorro Anual", f"${ahorro_zinc_ano:,}")
    st.caption("vs mejor historico")

# Total
with col3:
    st.markdown("**TOTAL COMBINADO**")
    total = ahorro_n2_ano + ahorro_zinc_ano
    st.metric("Ahorro Anual", f"${total:,}")
    st.caption(f"${total/12:,.0f}/mes")

st.success(f"🎯 **Potencial de ahorro total: ${total:,} USD/año**")

st.markdown("---")

# AUTO-REFRESH (al final)
auto_refresh = st.checkbox("🔄 Auto-actualizacion (3s)", value=False)

if auto_refresh:
    # Simular datos si esta en demo
    if st.session_state.demo_mode:
        ds.simulate_demo_data(dt=3.0)
        
        # Ejecutar control si esta en AUTO
        if ds.get_control_mode() == 'AUTO' and not ds.is_failsafe_active():
            ctrl = st.session_state.control_logic
            data = ds.get_all_process_data()
            
            apertura_tgt, razon, do_fail = ctrl.calculate_setpoint(
                velocity=data['velocity'],
                pureza=data['pureza_n2'],
                presion=data['presion_n2'],
                temp_zinc=data['temp_zinc'],
                estado_linea=data['estado_linea'],
                alarma_horno=data['alarma_horno'],
                alarma_zinc=data['alarma_zinc']
            )
            
            if do_fail:
                ds.set_failsafe(razon)
            else:
                apertura_final = ctrl.apply_ramp(apertura_tgt, ds.valve_aperture)
                ds.set_valve_aperture(apertura_final)
                ds.valve_aperture_target = apertura_tgt
                ds.control_reason = razon
                
                # Calcular finanzas
                flujo = (apertura_final / 100) * cfg.FLUJO_N2_NOMINAL
                dt_h = 3 / 3600
                with ds._lock:
                    ds.n2_consumed += flujo * dt_h
                    ds.savings_accumulated += flujo * dt_h * (cfg.COSTO_LIN_USD_M3 - cfg.COSTO_PSA_USD_M3)
        
        ds.add_history_point()
    
    time.sleep(3)
    st.rerun()

st.markdown("---")
st.caption("**SGI Colombia S.A.S.** · Cerebro SGI v2 · Proyecto KINNOX")

