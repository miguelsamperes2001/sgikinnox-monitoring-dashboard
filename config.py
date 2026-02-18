# CONEXION MODBUS
PLC_IP = "192.168.1.10"  # Cambiar por IP real del PLC Druids
PLC_PORT = 502
SLAVE_ID = 1

# INTERVALOS DE ACTUALIZACION
POLL_INTERVAL_S = 5
RECONNECT_WAIT_S = 15
CLOUD_EXPORT_INTERVAL = 60

# UMBRALES DE PROCESO
VEL_MIN_PRODUCCION = 30.0   # m/min - por debajo: linea detenida
VEL_MIN_N2_REDUCIDO = 80.0  # m/min - por debajo: reducir N2
VEL_MAX = 220.0             # m/min - alerta si se excede

TEMP_ZINC_MIN = 430.0       # °C
TEMP_ZINC_MAX = 470.0       # °C

TEMP_HORNO_REF_MIN = 600.0  # °C (referencial)
TEMP_HORNO_REF_MAX = 750.0  # °C (referencial)

# PARAMETROS N2 / PSA
PUREZA_NOMINAL = 99.0       # % objetivo
PUREZA_MIN_OPERATIVA = 98.0 # % - por debajo: reducir apertura
PUREZA_CRITICA = 95.0       # % - por debajo: FAILSAFE

PRESION_MIN_SEGURA = 0.5    # bar
PRESION_MAX_SEGURA = 8.0    # bar

# FORMING GAS (Mezclador N2-H2) - PRINCIPAL USO EN KINNOX
FORMING_GAS_ENABLED = True               # Sistema forming gas habilitado
FORMING_GAS_N2_PERCENT = 95.0           # % N2 en mezcla (95%)
FORMING_GAS_H2_PERCENT = 5.0            # % H2 en mezcla (5%)
FORMING_GAS_FLUJO_NOMINAL = 80.0        # Nm³/h flujo total forming gas
FORMING_GAS_N2_FLUJO = 76.0             # Nm³/h N2 en forming gas (95% de 80)
FORMING_GAS_H2_FLUJO = 4.0              # Nm³/h H2 en forming gas (5% de 80)

# Limites de seguridad forming gas
FORMING_GAS_H2_MIN = 3.0    # % minimo H2 (proteccion insuficiente)
FORMING_GAS_H2_MAX = 10.0   # % maximo H2 (riesgo explosion - LEL H2 = 4%)
FORMING_GAS_PRESION_MIN = 0.3  # bar
FORMING_GAS_PRESION_MAX = 2.0  # bar
FORMING_GAS_TEMP_MAX = 50.0    # °C temperatura mezclador

# Jet Wipe (proteccion N2 puro - uso secundario)
JET_WIPE_FLUJO_NOMINAL = 20.0   # Nm³/h N2 puro para jet wipe

# Total N2 consumido
N2_TOTAL_NOMINAL = FORMING_GAS_N2_FLUJO + JET_WIPE_FLUJO_NOMINAL  # 96 Nm³/h

# CONTROL DE VALVULA
APERTURA_LINEA_DETENIDA = 0.0   # %
APERTURA_ARRANQUE = 20.0        # %
APERTURA_VELOCIDAD_BAJA = 40.0  # %
APERTURA_NOMINAL = 75.0         # %
APERTURA_MAXIMA = 95.0          # %
APERTURA_FAILSAFE = 0.0         # %

MAX_CAMBIO_PCT_POR_CICLO = 10.0 # % - rampa anti-golpe

# HEARTBEAT
HEARTBEAT_INTERVALO_S = 10.0
HEARTBEAT_TIMEOUT_S = 60.0

# COSTOS FINANCIEROS
COSTO_LIN_USD_M3 = 2.28        # USD/m³ nitrogeno comprado (LIN)
COSTO_PSA_USD_M3 = 0.21        # USD/m³ estimado con PSA
COSTO_H2_USD_M3 = 8.50         # USD/m³ hidrogeno (forming gas)
FLUJO_N2_NOMINAL = N2_TOTAL_NOMINAL  # Nm³/h total (forming gas + jet wipe)

# DIRECCIONES MODBUS
# VERIFICAR ESTAS DIRECCIONES CON DOCUMENTACION DEL PLC DRUIDS
ADDR_VELOCIDAD_REAL = 40001
ADDR_VELOCIDAD_SETPOINT = 40002
ADDR_TEMP_ZINC = 40003
ADDR_TEMP_HORNO = 40004
ADDR_PRESION_JET_WIPE = 40005
ADDR_FLUJO_JET_WIPE = 40006
ADDR_NIVEL_ZINC = 40007
ADDR_TOTALIZADOR_METROS = 40008
ADDR_TIPO_PRODUCTO = 40009

# Variables PSA
ADDR_FLUJO_N2 = 40010
ADDR_PRESION_N2 = 40011
ADDR_PUREZA_N2 = 40012
ADDR_DEW_POINT_N2 = 40013

# Variables FORMING GAS (Mezclador N2-H2)
ADDR_FG_FLUJO_TOTAL = 40014      # Flujo total forming gas (Nm³/h)
ADDR_FG_PERCENT_N2 = 40015       # % N2 en mezcla
ADDR_FG_PERCENT_H2 = 40016       # % H2 en mezcla
ADDR_FG_PRESION = 40017          # Presion forming gas (bar)
ADDR_FG_TEMP_MEZCLADOR = 40018   # Temperatura mezclador (°C)
ADDR_FG_FLUJO_N2 = 40019         # Flujo N2 al mezclador (Nm³/h)
ADDR_FG_FLUJO_H2 = 40020         # Flujo H2 al mezclador (Nm³/h)

# Coils (estados booleanos)
ADDR_ESTADO_LINEA = 1
ADDR_ALARMA_HORNO = 2
ADDR_ALARMA_ZINC = 3
ADDR_ALARMA_PSA = 4
ADDR_ALARMA_FG_H2_HIGH = 5       # Alarma H2 > 10%
ADDR_ALARMA_FG_H2_LOW = 6        # Alarma H2 < 3%
ADDR_ALARMA_FG_PRESION = 7       # Alarma presion forming gas

# Escritura (control activo)
ADDR_VALVULA_N2_PSA = 40030      # Valvula principal N2 desde PSA
ADDR_VALVULA_N2_FG = 40031       # Valvula N2 hacia forming gas
ADDR_VALVULA_H2_FG = 40032       # Valvula H2 hacia forming gas
ADDR_HEARTBEAT = 40033
ADDR_MODO_CONTROL = 40034

# ESCALAS (raw -> valor real)
ESCALA_VELOCIDAD = 0.1
ESCALA_TEMP = 0.1
ESCALA_PRESION = 0.01
ESCALA_FLUJO = 0.1
ESCALA_PUREZA = 0.01
ESCALA_PERCENT = 0.01
ESCALA_VALVULA = 1.0

# CONTROL ACTIVO - HABILITACION
# CAMBIAR A True SOLO DESPUES DE CONFIRMAR:
#    1. PLC acepta escritura Modbus
#    2. Valvula tiene fail-closed mecanico
#    3. PLC tiene watchdog configurado
CONTROL_ACTIVO_HABILITADO = False

# CLOUD / EXPORT
CLOUD_ENABLED = False
CLOUD_PLATFORM = "ubidots"
UBIDOTS_TOKEN = "BBFF-xxxx"
UBIDOTS_DEVICE = "kinnox-line"
THINGSBOARD_URL = "http://demo.thingsboard.io"
THINGSBOARD_TOKEN = "ACCESS_TOKEN"

# ARCHIVOS DE SALIDA
CSV_PATH = "data/datos_kinnox.csv"
SQLITE_PATH = "data/datos_kinnox.db"
LOG_PATH = "logs/cerebro_sgi.log"

# STREAMLIT ESPECIFICO
MAX_HISTORY_POINTS = 500
AUTO_REFRESH_INTERVAL = 3
