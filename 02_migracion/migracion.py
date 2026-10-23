import pyodbc
from pymongo import MongoClient

# 1. CONEXIÓN A SQL SERVER Y MONGODB
try:
    conn_sql = pyodbc.connect(
        r'DRIVER={ODBC Driver 17 for SQL Server};'
        r'SERVER=LAPTOP-ITLNG2H7\SQLEXPRESS;'
        r'DATABASE=GimnasioDB;'
        r'Trusted_Connection=yes;'
    )
    cursor = conn_sql.cursor()
    print("¡Conexión exitosa a SQL Server!")
except Exception as e:
    print(f"Error al conectar a SQL Server: {e}")
    exit()

try:
    client_mongo = MongoClient("mongodb://localhost:27017/")
    db_mongo = client_mongo["GimnasioDB_Mongo"]
    
    # Definir colecciones en MongoDB
    col_clientes = db_mongo["clientes"]
    col_entrenadores = db_mongo["entrenadores"]
    col_planes = db_mongo["planes_entrenamiento"]
    
    print("¡Conexión exitosa a MongoDB!")
except Exception as e:
    print(f"Error al conectar a MongoDB: {e}")
    conn_sql.close()
    exit()

# Limpiar colecciones anteriores para evitar duplicados en pruebas
col_clientes.delete_many({})
col_entrenadores.delete_many({})
col_planes.delete_many({})

# 2. MIGRACIÓN DE ENTRENADORES (Referencing)
try:
    cursor.execute("SELECT id, nombre_completo_entrenador, especialidad, telefono, estado FROM ENTRENADOR")
    entrenadores_sql = cursor.fetchall()

    for ent in entrenadores_sql:
        doc_entrenador = {
            "sql_id": ent.id,
            "nombre": ent.nombre_completo_entrenador,
            "especialidad": ent.especialidad,
            "telefono": ent.telefono,
            "estado": ent.estado
        }
        col_entrenadores.insert_one(doc_entrenador)

    print("-> Entrenadores migrados correctamente (Referencing).")
except Exception as e:
    print(f"Error migrando entrenadores: {e}")

# 3. MIGRACIÓN DE CLIENTES (Embedding de Membresías, Pagos y Asistencias)
try:
    cursor.execute("SELECT id, nombre_completo_cliente, telefono, correo, edad, ciudad FROM CLIENTE")
    clientes_sql = cursor.fetchall()

    for cli in clientes_sql:
        cliente_id = cli.id

        # Buscar Membresías del cliente en SQL Server
        cursor.execute("SELECT id, tipo_membresia, fecha_inicio, fecha_fin, estado_membresia FROM MEMBRESIA WHERE id_cliente = ?", cliente_id)
        membresias_sql = cursor.fetchall()
        
        membresias = []
        for m in membresias_sql:
            # Buscar Pagos asociados a esta membresía
            cursor.execute("SELECT fecha_pago, valor_pago, metodo_pago, estado_pago FROM PAGO WHERE id_membresia = ?", m.id)
            pagos_sql = cursor.fetchall()
            
            pagos = [
                {
                    "fecha": str(p.fecha_pago),
                    "valor": p.valor_pago,
                    "metodo": p.metodo_pago,
                    "estado": p.estado_pago
                } for p in pagos_sql
            ]

            membresias.append({
                "sql_id_membresia": m.id,
                "tipo": m.tipo_membresia,
                "inicio": str(m.fecha_inicio),
                "fin": str(m.fecha_fin),
                "estado": m.estado_membresia,
                "pagos": pagos  # Pagos embebidos dentro de la membresía
            })

        # Buscar Asistencias del cliente en SQL Server
        cursor.execute("SELECT fecha_ingreso FROM ASISTENCIA WHERE id_cliente = ?", cliente_id)
        asistencias = [
            {
                "fecha_ingreso": str(a.fecha_ingreso)
            } for a in cursor.fetchall()
        ]

        # Construir el documento final embebido para el cliente
        doc_cliente = {
            "sql_id": cliente_id,
            "nombre_completo": cli.nombre_completo_cliente,
            "telefono": cli.telefono,
            "correo": cli.correo,
            "edad": cli.edad,
            "ciudad": cli.ciudad,
            "membresias": membresias,       
            "asistencias": asistencias      
        }

        col_clientes.insert_one(doc_cliente)

    print("-> Clientes con membresías, pagos y asistencias embebidas migrados correctamente.")
except Exception as e:
    print(f"Error migrando clientes: {e}")

# 4. MIGRACIÓN DE PLANES, RUTINAS Y EJERCICIOS (Embedding Jerárquico)
try:
    cursor.execute("SELECT id, nombre_plan, objetivo, duracion_semanas, id_entrenador FROM PLAN_ENTRENAMIENTO")
    planes_sql = cursor.fetchall()

    for plan in planes_sql:
        plan_id = plan.id

        # Buscar Rutinas asociadas al plan
        cursor.execute("SELECT id, nombre_rutina, nivel_dificultad, descripcion FROM RUTINA WHERE id_plan = ?", plan_id)
        rutinas_sql = cursor.fetchall()

        rutinas_emb = []
        for rut in rutinas_sql:
            rutina_id = rut.id

            # Buscar Ejercicios asociados a la rutina con sus detalles (RUTINA_EJERCICIO)
            cursor.execute("""
                SELECT e.nombre_ejercicio, e.grupo_muscular, e.tipo_ejercicio, re.series, re.repeticiones, re.observaciones
                FROM RUTINA_EJERCICIO re
                JOIN EJERCICIO e ON re.id_ejercicio = e.id
                WHERE re.id_rutina = ?
            """, rutina_id)
            ejercicios_sql = cursor.fetchall()

            ejercicios_emb = [
                {
                    "nombre": ej.nombre_ejercicio,
                    "grupo_muscular": ej.grupo_muscular,
                    "tipo": ej.tipo_ejercicio,
                    "series": ej.series,
                    "repeticiones": ej.repeticiones,
                    "observaciones": ej.observaciones
                } for ej in ejercicios_sql
            ]

            rutinas_emb.append({
                "sql_id": rutina_id,
                "nombre_rutina": rut.nombre_rutina,
                "nivel": rut.nivel_dificultad,
                "descripcion": rut.descripcion,
                "ejercicios": ejercicios_emb  # Array embebido de ejercicios
            })

        # Construir documento del Plan (Referencia al entrenador + Rutinas embebidas)
        doc_plan = {
            "sql_id": plan_id,
            "nombre_plan": plan.nombre_plan,
            "objetivo": plan.objetivo,
            "duracion_semanas": plan.duracion_semanas,
            "id_entrenador_ref": plan.id_entrenador,  # Referencia al entrenador
            "rutinas": rutinas_emb                    # Array embebido de rutinas
        }

        col_planes.insert_one(doc_plan)

    print("-> Planes de entrenamiento, rutinas y ejercicios migrados correctamente.")
except Exception as e:
    print(f"Error migrando planes y rutinas: {e}")

# 5. CIERRE DE CONEXIONES Y VERIFICACIÓN
cursor.close()
conn_sql.close()

print("  RESUMEN DE VERIFICACIÓN EN MONGODB")
print(f"Documentos en 'clientes': {col_clientes.count_documents({})}")
print(f"Documentos en 'entrenadores': {col_entrenadores.count_documents({})}")
print(f"Documentos en 'planes_entrenamiento': {col_planes.count_documents({})}")
print("¡Proceso de migración finalizado con éxito!")