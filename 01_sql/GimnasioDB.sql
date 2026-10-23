CREATE DATABASE GimnasioDB;
GO

USE GimnasioDB;
GO

-- 1. Tabla CLIENTE
CREATE TABLE CLIENTE(
	id INT PRIMARY KEY IDENTITY (1,1),
	nombre_completo_cliente VARCHAR (50) NOT NULL,
	telefono VARCHAR (20),
	correo VARCHAR (50),
	edad INT,
	ciudad VARCHAR (50)
);

-- 2. Tabla ENTRENADOR
CREATE TABLE ENTRENADOR(
	id INT PRIMARY KEY IDENTITY (1,1),
	nombre_completo_entrenador VARCHAR (50) NOT NULL,
	especialidad VARCHAR (50),
	telefono VARCHAR (20),
	estado VARCHAR (20)
);

-- 3. Tabla PLAN_ENTRENAMIENTO
CREATE TABLE PLAN_ENTRENAMIENTO(
	id INT PRIMARY KEY IDENTITY(1,1),
	nombre_plan VARCHAR(50),
	objetivo VARCHAR(100),
	duracion_semanas INT,
	id_entrenador INT,
	FOREIGN KEY (id_entrenador) REFERENCES ENTRENADOR(id)
);

-- 4. Tabla RUTINA
CREATE TABLE RUTINA(
	id INT PRIMARY KEY IDENTITY(1,1),
	nombre_rutina VARCHAR(50),
	nivel_dificultad VARCHAR(20),
	descripcion VARCHAR(100),
	id_plan INT,
	FOREIGN KEY (id_plan) REFERENCES PLAN_ENTRENAMIENTO(id)
);

-- 5. Tabla EJERCICIO
CREATE TABLE EJERCICIO(
	id INT PRIMARY KEY IDENTITY(1,1),
	nombre_ejercicio VARCHAR(50),
	grupo_muscular VARCHAR(50),
	tipo_ejercicio VARCHAR(50),
	estado VARCHAR(20)
);

-- 6. Tabla CLIENTE_RUTINA (Relación N:M)
CREATE TABLE CLIENTE_RUTINA (
    id_cliente_rutina INT PRIMARY KEY IDENTITY(1,1),
    id_cliente INT,
    id_rutina INT,
    FOREIGN KEY (id_cliente) REFERENCES CLIENTE(id),
    FOREIGN KEY (id_rutina) REFERENCES RUTINA(id)
);

-- 7. Tabla RUTINA_EJERCICIO (Detalle N:M con atributos)
CREATE TABLE RUTINA_EJERCICIO(
	id INT PRIMARY KEY IDENTITY(1,1),
	series INT,
	repeticiones INT,
	observaciones VARCHAR(100),
	id_rutina INT,
	id_ejercicio INT,
	FOREIGN KEY (id_rutina) REFERENCES RUTINA(id),
	FOREIGN KEY (id_ejercicio) REFERENCES EJERCICIO(id)
);

-- 8. Tabla MEMBRESIA
CREATE TABLE MEMBRESIA(
	id INT PRIMARY KEY IDENTITY(1,1),
	tipo_membresia VARCHAR(50),
	fecha_inicio DATE,
	fecha_fin DATE,
	estado_membresia VARCHAR(20),
	id_cliente INT,
	FOREIGN KEY (id_cliente) REFERENCES CLIENTE(id)
);

-- 9. Tabla PAGO
CREATE TABLE PAGO(
	id INT PRIMARY KEY IDENTITY(1,1),
	fecha_pago DATE,
	valor_pago INT,
	metodo_pago VARCHAR(50),
	estado_pago VARCHAR(20),
	id_membresia INT,
	FOREIGN KEY (id_membresia) REFERENCES MEMBRESIA(id)
);

-- 10. Tabla ASISTENCIA
CREATE TABLE ASISTENCIA (
    id INT PRIMARY KEY IDENTITY(1,1),
    fecha_ingreso DATE,
    id_cliente INT,
    FOREIGN KEY (id_cliente) REFERENCES CLIENTE(id)
);