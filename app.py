import streamlit as st
import plotly.graph_objects as go
from datetime import datetime

import config as cfg
from modules.industrial.event_logger import get_event_logger
from modules.industrial.watchdog import get_watchdog
from modules.industrial.role_manager import get_role_manager
from modules.industrial.data_pipeline import get_pipeline

# PAGE CONFIG
st.set_page_config(
    page_title=f"Cerebro SGI [{cfg.MODO_OPERACION}]",
    page_icon="⚙️" if cfg.MODO_OPERACION == "SIMULACION" else "🏭",
    layout="wide",
    initial_sidebar_state="expanded",
)

# INICIALIZAR SISTEMAS
if 'initialized' not in st.session_state:
    st.session_state.event_logger = get_event_logger()
    st.session_state.watchdog = get_watchdog()
    st.session_state.role_manager = get_role_manager()
    st.session_state.pipeline = get_pipeline()
    st.session_state.initialized = True
    
    # Log inicio
    st.session_state.event_logger.log_event(
        "SYSTEM",
        "INFO",
        f"Sistema iniciado en modo {cfg.MODO_OPERACION}"
    )

# BANNER DE MODO (SIEMPRE VISIBLE)
if cfg.MODO_OPERACION == "SIMULACION":
    st.markdown("""
    <div style="background-color: #ffd740; color: #000; padding: 12px; text-align: center; 
                font-weight: bold; border-radius: 4px; margin-bottom: 20px;">
        🎮 MODO SIMULACIÓN - Datos generados automáticamente (NO REAL)
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <div style="background-color: #00e676; color: #000; padding: 12px; text-align: center; 
                font-weight: bold; border-radius: 4px; margin-bottom: 20px;">
        🏭 MODO REAL - Datos desde PLC/PSA
    </div>
    """, unsafe_allow_html=True)

# CUSTOM CSS
st.markdown("""
<style>
    .stApp { background-color: #07090f; color: #cdd9ee; }
    h1, h2, h3 { color: #00e5ff !important; font-family: 'IBM Plex Mono', monospace; }
    [data-testid="stMetricValue"] { font-size: 2.5rem; color: #00e5ff; }
    
    .estimated-badge {
        display: inline-block;
        padding: 2px 8px;
        border-radius: 3px;
        font-size: 0.7rem;
        font-weight: bold;
        background-color: rgba(255, 215, 64, 0.2);
        color: #ffd740;
        border: 1px solid #ffd740;
        margin-left: 8px;
    }
    
    .measured-badge {
        display: inline-block;
        padding: 2px 8px;
        border-radius: 3px;
        font-size: 0.7rem;
        font-weight: bold;
        background-color: rgba(0, 230, 118, 0.2);
        color: #00e676;
        border: 1px solid #00e676;
        margin-left: 8px;
    }
    
    .pending-badge {
        display: inline-block;
        padding: 2px 8px;
        border-radius: 3px;
        font-size: 0.7rem;
        font-weight: bold;
        background-color: rgba(255, 23, 68, 0.2);
        color: #ff1744;
        border: 1px solid #ff1744;
        margin-left: 8px;
    }
</style>
""", unsafe_allow_html=True)

# SIDEBAR
rm = st.session_state.role_manager
session_info = rm.get_session_info()

with st.sidebar:
    st.markdown("### 🏭 CEREBRO SGI v2")
    
    # Modo operación
    modo_icon = "🎮" if cfg.MODO_OPERACION == "SIMULACION" else "🏭"
    st.markdown(f"**Modo:** {modo_icon} {cfg.MODO_OPERACION}")
    
    # Fase del proyecto
    st.markdown(f"**Fase:** {cfg.FASE_PROYECTO}")
    st.caption(f"Algorithm: v{cfg.ALGORITHM_VERSION}")
    
    st.markdown("---")
    
    # Usuario y rol
    st.markdown("**👤 Usuario**")
    st.write(f"{session_info['name']}")
    st.caption(f"Rol: {session_info['role']}")
    
    # Permisos
    with st.expander("Ver permisos"):
        perms = session_info['permissions']
        for perm, allowed in perms.items():
            icon = "✅" if allowed else "❌"
            st.caption(f"{icon} {perm}")
    
    st.markdown("---")
    
    # Estado watchdog
    watchdog = st.session_state.watchdog
    wd_status = watchdog.get_status()
    
    if wd_status['failsafe_active']:
        st.error("⛔ FAILSAFE ACTIVO")
        st.caption(wd_status['failsafe_reason'])
    else:
        st.success("✅ Sistema OK")
    
    st.caption(f"Última lectura: {wd_status['seconds_since_read']:.0f}s")

# HEADER
st.title("⚙️ CEREBRO SGI v2")
st.markdown("**KINNOX - Línea de Galvanizado Druids**")
st.markdown("_República Dominicana_")

# Estado instrumentación
with st.expander("📊 Estado de Instrumentación"):
    cols = st.columns(3)
    
    col_idx = 0
    for sensor, instalado in cfg.INSTRUMENTACION.items():
        with cols[col_idx % 3]:
            if instalado:
                st.markdown(f"✅ **{sensor}**")
            else:
                st.markdown(f"⚠️ **{sensor}** <span class='pending-badge'>PENDIENTE</span>", 
                           unsafe_allow_html=True)
        col_idx += 1

st.markdown("---")

# KPIs PRINCIPALES (con marcadores MEDIDO/ESTIMADO)
col1, col2, col3, col4 = st.columns(4)

# Ejemplo de datos (en producción: desde DataStore)
velocidad = 165.0
temp_zinc = 452.0
n2_flujo = 96.0
ahorro = 1250.0

with col1:
    st.metric("Velocidad Línea", f"{velocidad:.1f} m/min")
    if cfg.INSTRUMENTACION["velocidad_real"]:
        st.markdown('<span class="measured-badge">MEDIDO</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="estimated-badge">ESTIMADO</span>', unsafe_allow_html=True)

with col2:
    st.metric("Temp. Zinc", f"{temp_zinc:.1f} °C")
    if cfg.INSTRUMENTACION["temp_zinc"]:
        st.markdown('<span class="measured-badge">MEDIDO</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="estimated-badge">ESTIMADO</span>', unsafe_allow_html=True)

with col3:
    st.metric("Flujo N₂", f"{n2_flujo:.1f} Nm³/h")
    if cfg.INSTRUMENTACION["caudalimetro_n2"]:
        st.markdown('<span class="measured-badge">MEDIDO</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="estimated-badge">ESTIMADO</span>', unsafe_allow_html=True)

with col4:
    st.metric("Ahorro Sesión", f"${ahorro:.2f}")
    if cfg.INSTRUMENTACION["caudalimetro_n2"]:
        st.markdown('<span class="measured-badge">MEDIDO</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="estimated-badge">ESTIMADO</span>', unsafe_allow_html=True)

st.markdown("---")

# ESTADO DEL CONTROL
st.subheader("🎛 Estado del Control N₂")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("**Modo Actual:** MANUAL")
    st.caption("Operador controlando manualmente")

with col2:
    st.metric("Apertura Válvula", "65%")

with col3:
    can_enable, reason = rm.can_enable_auto()
    if can_enable:
        st.success("✅ AUTO disponible")
    else:
        st.warning(f"⚠️ AUTO bloqueado: {reason}")

# Roadmap de fases
with st.expander("🗺 Roadmap: Fases del Proyecto"):
    st.markdown(f"""
    **FASE A - READ-ONLY** {'✅ ACTUAL' if cfg.FASE_PROYECTO == 'A' else ''}
    - Solo lectura de PLC/PSA
    - Sin escritura de comandos
    - Dashboard de monitoreo
    - Historización de datos
    
    **FASE B - ADVISORY** {'✅ ACTUAL' if cfg.FASE_PROYECTO == 'B' else ''}
    - Algoritmo genera recomendaciones
    - Operador decide si aplicar
    - Tracking de recomendaciones vs acciones
    
    **FASE C - CLOSED-LOOP** {'✅ ACTUAL' if cfg.FASE_PROYECTO == 'C' else ''}
    - Control automático habilitado
    - Watchdog + fail-safe activos
    - Requiere doble confirmación
    - Auditoría completa
    """)

st.markdown("---")

# NAVEGACIÓN
st.subheader("🧭 Páginas")

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

st.markdown("---")

# EVENTOS RECIENTES
st.subheader("📋 Eventos Recientes")

logger = st.session_state.event_logger
recent = logger.get_recent_events(limit=10)

if recent:
    import pandas as pd
    df = pd.DataFrame(recent)
    df = df[['timestamp', 'severity', 'event_type', 'description', 'user']]
    st.dataframe(df, use_container_width=True, hide_index=True)
else:
    st.info("Sin eventos registrados")

st.markdown("---")
st.caption(f"""
**SGI Colombia S.A.S.** · Cerebro SGI v2 · Modo {cfg.MODO_OPERACION} · 
Fase {cfg.FASE_PROYECTO} · Usuario: {session_info['name']} ({session_info['role']})
""")


