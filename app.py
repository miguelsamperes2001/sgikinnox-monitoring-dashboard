cd streamlit_app/
git init
git add .
git commit -m "Initial commit - Cerebro SGI v2"
git remote add origin https://github.com/TU-USUARIO/cerebro-sgi-kinnox.git
git push -u origin main
```

### 2️⃣ Deploy en Streamlit Cloud (3 minutos)
1. https://share.streamlit.io
2. New app → selecciona tu repo
3. Main file: `app.py`
4. Deploy!

**URL resultante:** `https://tu-usuario-cerebro-sgi-kinnox.streamlit.app`

### 3️⃣ Modo demo vs producción
- **Ahora:** Modo DEMO automático (datos simulados, sin PLC)
- **En planta:** Cambiar `demo_mode = False` + configurar IP del PLC

---

## ⚙️ Arquitectura técnica
```
Streamlit Cloud / Local
    ↓ (Streamlit multi-page app)
app.py (home)
    ├─ DataStore (estado compartido en session_state)
    ├─ ModbusClient (lectura/escritura PLC)
    └─ ControlLogic (algoritmo predictivo)
         ↓
pages/
    ├─ 01_Operativo.py
    ├─ 02_Control_N2.py  ✅ COMPLETADO
    ├─ 03_Financiero.py
    ├─ 04_Modbus.py
    └─ 05_Alertas.py
