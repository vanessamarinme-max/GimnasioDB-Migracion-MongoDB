/* 1. Filtrar registros con $match y proyectar campos con $project 
Filtra los clientes que viven en Medellín y muestra solo su nombre y correo, ocultando el _id. */
db.clientes.aggregate([
 {
 "$match": { "ciudad": "Medellin" }
 },
 {
 "$project": {
 "_id": 0,
 "nombre_completo": 1,
 "correo": 1
 }
 }
])

/* 2. Desglosar arrays embebidos con $unwind
Separa el array embebido de membresías para ver cada una de forma individual. */
db.clientes.aggregate([
  {
    "$unwind": "$membresias"
  },
  {
    "$project": {
      "_id": 0,
      "nombre_completo": 1,
      "tipo_membresia": "$membresias.tipo",
      "estado": "$membresias.estado"
    }
  }
])

/* 3. Nuestro primer $lookup básico
Relaciona la colección de entrenadores con la colección de planes_entrenamiento mediante sus identificadores. */
db.entrenadores.aggregate([
  {
    "$lookup": {
      "from": "planes_entrenamiento",
      "localField": "sql_id",
      "foreignField": "id_entrenador_ref",
      "as": "planes"
    }
  }
])

/* 4. $lookup mostrando solo algunos campos con $project
Une los entrenadores con sus planes, pero filtrando para mostrar únicamente el nombre del entrenador y el nombre del plan. */
db.entrenadores.aggregate([
  {
    "$lookup": {
      "from": "planes_entrenamiento",
      "localField": "sql_id",
      "foreignField": "id_entrenador_ref",
      "as": "planes"
    }
  },
  {
    "$project": {
      "_id": 0,
      "nombre": 1,
      "planes.nombre_plan": 1
    }
  }
])

/* 5. Filtrar clientes de una ciudad con $match y hacer $lookup
Filtra primero a los clientes que viven en "Medellin" y luego busca información relacionada. */
db.clientes.aggregate([
  {
    "$match": { "ciudad": "Medelli" }
  },
  {
    "$lookup": {
      "from": "entrenadores",
      "localField": "sql_id",
      "foreignField": "sql_id",
      "as": "detalle"
    }
  }
])

/* 6. Ordenar con $sort y limitar con $limit
Muestra los 3 planes de entrenamiento con mayor duración en semanas, ordenados de forma descendente. */
db.planes_entrenamiento.aggregate([
  {
    "$sort": { "duracion_semanas": -1 }
  },
  {
    "$limit": 3
  },
  {
    "$project": {
      "_id": 0,
      "nombre_plan": 1,
      "duracion_semanas": 1,
      "objetivo": 1
    }
  }
])

/* 7. Usar $unwind en un array interno (Rutinas)
Desglosa las rutinas que están dentro de los planes de entrenamiento para listarlas una a una. */
db.planes_entrenamiento.aggregate([
  {
    "$unwind": "$rutinas"
  },
  {
    "$project": {
      "_id": 0,
      "nombre_plan": 1,
      "nombre_rutina": "$rutinas.nombre_rutina",
      "nivel": "$rutinas.nivel"
    }
  }
])

/* 8. Múltiples $lookup en secuencia
Cruza información realizando dos uniones sucesivas: primero une los planes con los entrenadores, y luego realiza otro proceso o cruce complementario de forma limpia. */
db.planes_entrenamiento.aggregate([
  {
    "$lookup": {
      "from": "entrenadores",
      "localField": "id_entrenador_ref",
      "foreignField": "sql_id",
      "as": "info_entrenador"
    }
  },
  {
    "$lookup": {
      "from": "clientes",
      "localField": "duracion_semanas",
      "foreignField": "edad",
      "as": "clientes_referencia_edad"
    }
  },
  {
    "$project": {
      "_id": 0,
      "nombre_plan": 1,
      "objetivo": 1,
      "info_entrenador.nombre": 1
    }
  }
])