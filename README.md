# Proyecto de Migración de Datos: SQL Server a MongoDB (GimnasioDB)

Este repositorio contiene la solución completa para la migración, estructuración y consulta del modelo de datos para la gestión del gimnasio.

---

## Estructura del Repositorio

* `01_sql/`: Scripts de creación y población masiva en SQL Server.
* `02_migracion/`: Script de Python en encargado de la extracción, transformación y carga (ETL).
* `03_consultas_mongo/`: Aggregation Pipelines y consultas desarrolladas para análisis de negocio.
* `04_modelos/`: Diagramas de arquitectura relacional y documental.
* `05_evidencias/`: Pruebas gráficas de integridad y conteo de datos.
* `06_presentacion/`: Presentación para la sustentación final.

---

## Justificación Técnica de Decisiones de Diseño

### 1. Decisiones de Embedding (Anidación)
* **Membresías y Pagos en Cliente:** Se decidió embeber las membresías dentro de cada cliente, y los pagos dentro de sus respectivas membresías, debido a que el historial financiero de un usuario casi siempre se consulta dentro del contexto del cliente. Esto elimina JOINs costosos.
* **Asistencias en Cliente:** Las asistencias se integraron como un array embebido dentro del documento del cliente para facilitar el cálculo de frecuencia y fidelidad del usuario.
* **Rutinas y Ejercicios en Planes de Entrenamiento:** Las rutinas y los ejercicios (con series, repeticiones u observaciones) se anidaron jerárquicamente dentro de los planes de entrenamiento. Esto responde a que una rutina no suele existir de manera aislada sin su plan correspondiente.

### 2. Decisiones de Referencing (Referencias)
* **Entrenadores (Colección independiente):** Se mantuvo la colección `entrenadores` separada y se referenció desde los `planes_entrenamiento` mediante el campo `id_entrenador_ref`. Esto se debe a que un entrenador administra múltiples planes y sus datos de contacto cambian o se consultan de manera independiente.

---

## Justificación de Consultas de Agregación e Impacto en el Negocio

1. **Consulta 1 (Filtrado por ciudad):** Permite focalizar campañas de marketing y promociones según la ubicación geográfica de los clientes.
2. **Consulta 2 (Desglose de membresías con `$unwind`):** Facilita la auditoría individual de estados de contrato para identificar clientes con suscripciones inactivas o por vencer.
3. **Consulta 3 (`$lookup` Entrenadores y Planes):** Permite a la gerencia conocer la carga de trabajo y asignación de planes por cada entrenador.
4. **Consulta 4 (Proyección de relaciones):** Simplifica la visualización de datos clave eliminando campos pesados o innecesarios para reportes ejecutivos.
5. **Consulta 5 (Filtro por especialidad con `$lookup`):** Ayuda a evaluar la disponibilidad de oferta de entrenamiento por áreas (ej. Musculación, CrossFit).
6. **Consulta 6 (`$sort` y `$limit` de planes):** Identifica los programas de entrenamiento más extensos para análisis de retención.
7. **Consulta 7 (`$unwind` en rutinas):** Desglosa la carga metodológica de los planes para la revisión del equipo pedagógico del gimnasio.
8. **Consulta 8 (Múltiples `$lookup`):** Permite cruzar información compleja entre entrenamiento y clientes para decisiones estratégicas globales.

---

## Verificación de Datos e Integridad

* **Total de registros en SQL Server:** > 5.000 registros distribuidos entre las 10 tablas relacionales.
* **Documentos resultantes en MongoDB:**
  * Colección `clientes`: 600 documentos (con membresías, pagos y asistencias anidadas).
  * Colección `entrenadores`: 50 documentos.
  * Colección `planes_entrenamiento`: 100 documentos (con rutinas y ejercicios anidados).