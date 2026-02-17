import streamlit as st
import pandas as pd
import time

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Cerebro SGI v2 - Kinnox", layout="wide")

# --- ESTADO DE LA APP (DataStore) ---
if 'demo_mode' not in st.session_state:
    st.session_state['demo_mode'] = True

# --- BARRA LATERAL (Control de Planta) ---
st.sidebar.title("⚙️ Configuración")
modo = st.sidebar.selectbox("Modo de Operación", ["DEMO (Simulado)", "PRODUCCIÓN (PLC)"])
st.session_state['demo_mode'] = (modo == "DEMO (Simulado)")

# --- CUERPO PRINCIPAL ---
st.title("🧠 Cerebro SGI v2: Monitoreo Kinnox")
st.info(f"Sistema operando en: **{modo}**")

# Columnas con métricas clave para SGI
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Ahorro Acumulado (Leasing)", "$12,450 USD", "+5.2%")
with col2:
    st.metric("Eficiencia de Producción", "94%", "-1.5%")
with col3:
    st.metric("Estado PLC (Modbus)", "Conectado" if not st.session_state['demo_mode'] else "Simulado")

st.divider()

# Gráfico de ejemplo
st.subheader("📊 Monitoreo de Flujo de Ahorros")
datos_demo = pd.DataFrame({
    'Semana': ['S1', 'S2', 'S3', 'S4'],
    'Producción': [100, 120, 115, 130],
    'Ahorro': [20, 25, 23, 28]
})
st.line_chart(datos_demo.set_index('Semana'))

st.success("✅ Sistema de control predictivo activo.")
