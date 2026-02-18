import sqlite3
from datetime import datetime, date

# Configuracion
DB_PATH = "data/consumo_n2_diario.db"

def init_database():
    """Crea la base de datos si no existe."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS psa_installation (
            id INTEGER PRIMARY KEY,
            installation_date TEXT NOT NULL,
            capex REAL NOT NULL,
            costo_lin REAL NOT NULL,
            costo_psa REAL NOT NULL
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS consumo_diario (
            fecha TEXT PRIMARY KEY,
            produccion_tm REAL NOT NULL,
            metros_producidos REAL NOT NULL,
            n2_consumido_m3 REAL NOT NULL,
            velocidad_promedio REAL,
            horas_operacion REAL,
            tipo_producto TEXT,
            observaciones TEXT
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS zinc_diario (
            fecha TEXT PRIMARY KEY,
            zinc_consumido_kg REAL NOT NULL,
            dross_generado_kg REAL,
            ratio_kg_tm REAL,
            temp_zinc_promedio REAL,
            observaciones TEXT
        )
    """)
    
    conn.commit()
    conn.close()
    print("✅ Base de datos inicializada")

def register_psa_installation(installation_date=None, capex=580000, costo_lin=2.28, costo_psa=0.778189):
    """Registra la fecha de instalacion de la PSA."""
    if installation_date is None:
        installation_date = datetime.now().strftime('%Y-%m-%d')
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Verificar si ya existe
    cursor.execute("SELECT COUNT(*) FROM psa_installation")
    if cursor.fetchone()[0] > 0:
        print("⚠️ PSA ya registrada. Actualizando datos...")
        cursor.execute("""
            UPDATE psa_installation 
            SET installation_date=?, capex=?, costo_lin=?, costo_psa=?
            WHERE id=1
        """, (installation_date, capex, costo_lin, costo_psa))
    else:
        cursor.execute("""
            INSERT INTO psa_installation (id, installation_date, capex, costo_lin, costo_psa)
            VALUES (1, ?, ?, ?, ?)
        """, (installation_date, capex, costo_lin, costo_psa))
    
    conn.commit()
    conn.close()
    print(f"✅ PSA registrada con fecha: {installation_date}")

def add_daily_consumption(
    fecha,
    produccion_tm,
    metros_producidos,
    n2_consumido_m3,
    velocidad_promedio=None,
    horas_operacion=None,
    tipo_producto=None,
    observaciones=None
):
    """Registra el consumo diario de N2."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT OR REPLACE INTO consumo_diario 
        (fecha, produccion_tm, metros_producidos, n2_consumido_m3, velocidad_promedio, 
         horas_operacion, tipo_producto, observaciones)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (fecha, produccion_tm, metros_producidos, n2_consumido_m3, velocidad_promedio,
          horas_operacion, tipo_producto, observaciones))
    
    conn.commit()
    conn.close()
    print(f"✅ Consumo registrado para {fecha}: {n2_consumido_m3:.2f} m³")

def add_daily_zinc(
    fecha,
    zinc_consumido_kg,
    dross_generado_kg=None,
    ratio_kg_tm=None,
    temp_zinc_promedio=None,
    observaciones=None
):
    """Registra el consumo diario de zinc."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT OR REPLACE INTO zinc_diario
        (fecha, zinc_consumido_kg, dross_generado_kg, ratio_kg_tm, temp_zinc_promedio, observaciones)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (fecha, zinc_consumido_kg, dross_generado_kg, ratio_kg_tm, temp_zinc_promedio, observaciones))
    
    conn.commit()
    conn.close()
    print(f"✅ Zinc registrado para {fecha}: {zinc_consumido_kg:.2f} kg")

def get_roi_metrics():
    """Calcula ROI y Payback basados en datos reales."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Verificar instalacion PSA
    cursor.execute("SELECT installation_date, capex, costo_lin, costo_psa FROM psa_installation WHERE id=1")
    psa_data = cursor.fetchone()
    
    if not psa_data:
        print("❌ PSA no registrada. Ejecutar register_psa_installation() primero.")
        conn.close()
        return None
    
    installation_date = datetime.strptime(psa_data[0], '%Y-%m-%d')
    capex = psa_data[1]
    costo_lin = psa_data[2]
    costo_psa = psa_data[3]
    
    # Consumo total
    cursor.execute("SELECT SUM(n2_consumido_m3) FROM consumo_diario WHERE fecha >= ?", (psa_data[0],))
    n2_total = cursor.fetchone()[0] or 0
    
    # Dias de operacion
    dias_operacion = (datetime.now() - installation_date).days
    if dias_operacion == 0:
        dias_operacion = 1
    
    # Calculos
    ahorro_por_m3 = costo_lin - costo_psa
    ahorro_acumulado = n2_total * ahorro_por_m3
    consumo_diario_promedio = n2_total / dias_operacion
    consumo_mensual_proyectado = consumo_diario_promedio * 30
    ahorro_mensual_proyectado = consumo_mensual_proyectado * ahorro_por_m3
    ahorro_anual_proyectado = consumo_mensual_proyectado * 12 * ahorro_por_m3
    
    roi_actual = ahorro_acumulado / capex if capex > 0 else 0
    roi_anual_proyectado = ahorro_anual_proyectado / capex if capex > 0 else 0
    
    if ahorro_mensual_proyectado > 0:
        payback_meses = (capex - ahorro_acumulado) / ahorro_mensual_proyectado
        payback_meses = max(0, payback_meses)
    else:
        payback_meses = 999
    
    porcentaje_recuperado = (ahorro_acumulado / capex) * 100
    
    conn.close()
    
    return {
        'fecha_instalacion': installation_date.strftime('%Y-%m-%d'),
        'dias_operacion': dias_operacion,
        'n2_consumido_total': n2_total,
        'consumo_diario_promedio': consumo_diario_promedio,
        'consumo_mensual_proyectado': consumo_mensual_proyectado,
        'ahorro_acumulado': ahorro_acumulado,
        'ahorro_mensual_proyectado': ahorro_mensual_proyectado,
        'ahorro_anual_proyectado': ahorro_anual_proyectado,
        'roi_actual': roi_actual,
        'roi_anual_proyectado': roi_anual_proyectado,
        'payback_meses': payback_meses,
        'porcentaje_recuperado': porcentaje_recuperado
    }

def print_summary():
    """Imprime resumen de metricas actuales."""
    metrics = get_roi_metrics()
    if not metrics:
        return
    
    print("\n" + "="*60)
    print("RESUMEN ROI/PAYBACK - DATOS REALES")
    print("="*60)
    print(f"Fecha instalacion PSA: {metrics['fecha_instalacion']}")
    print(f"Dias de operacion: {metrics['dias_operacion']}")
    print(f"\nCONSUMO:")
    print(f"  N2 consumido total: {metrics['n2_consumido_total']:,.2f} m³")
    print(f"  Promedio diario: {metrics['consumo_diario_promedio']:,.2f} m³/dia")
    print(f"  Proyeccion mensual: {metrics['consumo_mensual_proyectado']:,.2f} m³/mes")
    print(f"\nAHORRO:")
    print(f"  Acumulado real: ${metrics['ahorro_acumulado']:,.2f}")
    print(f"  Proyeccion mensual: ${metrics['ahorro_mensual_proyectado']:,.2f}/mes")
    print(f"  Proyeccion anual: ${metrics['ahorro_anual_proyectado']:,.2f}/año")
    print(f"\nROI:")
    print(f"  ROI actual: {metrics['roi_actual']:.4f}x ({metrics['porcentaje_recuperado']:.2f}%)")
    print(f"  ROI anual proyectado: {metrics['roi_anual_proyectado']:.2f}x")
    print(f"\nPAYBACK:")
    if metrics['payback_meses'] > 0:
        print(f"  Meses restantes: {metrics['payback_meses']:.1f}")
    else:
        print(f"  ✅ COMPLETADO - Inversion recuperada")
    print("="*60 + "\n")

# EJEMPLO DE USO
if __name__ == "__main__":
    print("Inicializando sistema de tracking...")
    init_database()
    
    # Ejemplo: Registrar instalacion PSA
    # register_psa_installation(installation_date='2025-02-01')
    
    # Ejemplo: Registrar consumo de hoy
    # add_daily_consumption(
    #     fecha=date.today().strftime('%Y-%m-%d'),
    #     produccion_tm=19.5,
    #     metros_producidos=28500,
    #     n2_consumido_m3=1080,
    #     velocidad_promedio=165,
    #     horas_operacion=20,
    #     tipo_producto='Alambre 2.5mm',
    #     observaciones='Produccion normal'
    # )
    
    # Ejemplo: Registrar zinc de hoy
    # add_daily_zinc(
    #     fecha=date.today().strftime('%Y-%m-%d'),
    #     zinc_consumido_kg=245,
    #     dross_generado_kg=82,
    #     ratio_kg_tm=12.56,
    #     temp_zinc_promedio=451.5,
    #     observaciones='Temperatura estable'
    # )
    
    # Ver resumen
    # print_summary()
    
    print("\nEjecuta las funciones segun necesites:")
    print("  - register_psa_installation()  -> Marcar fecha de instalacion")
    print("  - add_daily_consumption()      -> Registrar consumo diario")
    print("  - add_daily_zinc()             -> Registrar zinc diario")
    print("  - get_roi_metrics()            -> Obtener metricas")
    print("  - print_summary()              -> Ver resumen")
