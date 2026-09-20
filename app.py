from flask import Flask, render_template, jsonify
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database", "control_personal.db")


def conectar():
    conexion = sqlite3.connect(DB_PATH)
    conexion.row_factory = sqlite3.Row
    return conexion


def crear_base_datos():

    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS actividades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            categoria TEXT,
            icono TEXT,
            hora_inicio TEXT,
            hora_fin TEXT,
            dia_semana INTEGER,
            activo INTEGER DEFAULT 1
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sesiones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            actividad_id INTEGER NOT NULL,
            fecha TEXT NOT NULL,
            hora_inicio TEXT,
            hora_fin TEXT,
            segundos_reales INTEGER DEFAULT 0,
            estado TEXT DEFAULT 'pendiente',
            FOREIGN KEY (actividad_id)
                REFERENCES actividades(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS habitos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            icono TEXT,
            objetivo INTEGER DEFAULT 1,
            activo INTEGER DEFAULT 1
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS progreso_habitos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            habito_id INTEGER NOT NULL,
            fecha TEXT NOT NULL,
            cantidad INTEGER DEFAULT 0,
            completado INTEGER DEFAULT 0,
            FOREIGN KEY (habito_id)
                REFERENCES habitos(id)
        )
    """)

    conexion.commit()

    # Solo insertamos el horario si todavía no existe.
    cantidad = cursor.execute(
        "SELECT COUNT(*) FROM actividades"
    ).fetchone()[0]

    if cantidad == 0:
        insertar_horario(cursor)
        conexion.commit()

    conexion.close()


def agregar(cursor, nombre, categoria, icono, inicio, fin, dias):

    for dia in dias:

        cursor.execute("""
            INSERT INTO actividades
            (
                nombre,
                categoria,
                icono,
                hora_inicio,
                hora_fin,
                dia_semana
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            nombre,
            categoria,
            icono,
            inicio,
            fin,
            dia
        ))


def insertar_horario(cursor):

    # Python:
    # lunes = 0
    # martes = 1
    # miércoles = 2
    # jueves = 3
    # viernes = 4
    # sábado = 5
    # domingo = 6

    semana = [0, 1, 2, 3, 4]

    agregar(
        cursor,
        "Levantarse y aseo",
        "rutina",
        "🌅",
        "07:00",
        "07:20",
        semana
    )

    agregar(
        cursor,
        "Meditación y Biblia",
        "espiritual",
        "📖",
        "07:20",
        "07:50",
        semana
    )

    agregar(
        cursor,
        "Desayuno",
        "comida",
        "🍳",
        "07:50",
        "08:20",
        semana
    )

    agregar(
        cursor,
        "Inglés",
        "ingles",
        "🇬🇧",
        "08:20",
        "09:00",
        semana
    )

    agregar(
        cursor,
        "Oficio",
        "hogar",
        "🧹",
        "09:00",
        "10:00",
        semana
    )

    agregar(
        cursor,
        "Buscar trabajo",
        "trabajo",
        "💼",
        "10:00",
        "11:30",
        semana
    )

    agregar(
        cursor,
        "Certificaciones",
        "carrera",
        "🎓",
        "11:30",
        "12:30",
        semana
    )

    agregar(
        cursor,
        "Proyecto personal",
        "proyecto",
        "💻",
        "12:30",
        "13:30",
        semana
    )

    agregar(
        cursor,
        "Descanso",
        "descanso",
        "☕",
        "13:30",
        "14:00",
        semana
    )

    agregar(
        cursor,
        "Almuerzo",
        "comida",
        "🍛",
        "14:00",
        "14:40",
        semana
    )

    # Lunes, martes y jueves
    agregar(
        cursor,
        "Universidad / tareas",
        "universidad",
        "📚",
        "14:40",
        "16:40",
        [0, 1, 3]
    )

    agregar(
        cursor,
        "Ejercicio",
        "ejercicio",
        "🏃",
        "16:40",
        "17:00",
        [0, 1, 3]
    )

    agregar(
        cursor,
        "Proyecto personal",
        "proyecto",
        "💻",
        "17:00",
        "18:30",
        [0, 1, 3]
    )

    agregar(
        cursor,
        "Certificaciones",
        "carrera",
        "🎓",
        "18:30",
        "19:20",
        [0, 1, 3]
    )

    agregar(
        cursor,
        "Tiempo libre / pendientes",
        "libre",
        "🕒",
        "19:20",
        "20:00",
        [0, 1, 3]
    )

    agregar(
        cursor,
        "Cena",
        "comida",
        "🍽️",
        "20:00",
        "20:40",
        [0, 1, 3]
    )

    agregar(
        cursor,
        "Inglés ligero",
        "ingles",
        "🇬🇧",
        "20:40",
        "21:20",
        [0, 1, 3]
    )

    agregar(
        cursor,
        "Biblia / reflexión",
        "espiritual",
        "📖",
        "21:20",
        "21:40",
        [0, 1, 3]
    )

    agregar(
        cursor,
        "Prepararse para dormir",
        "rutina",
        "🌙",
        "21:40",
        "22:00",
        [0, 1, 3]
    )

    # Miércoles y viernes
    agregar(
        cursor,
        "Universidad / pendientes",
        "universidad",
        "📚",
        "14:40",
        "16:20",
        [2, 4]
    )

    agregar(
        cursor,
        "Ejercicio",
        "ejercicio",
        "🏃",
        "16:20",
        "16:40",
        [2, 4]
    )

    agregar(
        cursor,
        "Prepararse",
        "rutina",
        "🚿",
        "16:40",
        "17:00",
        [2, 4]
    )

    agregar(
        cursor,
        "Ocupado",
        "ocupado",
        "🔒",
        "17:00",
        "22:00",
        [2, 4]
    )


@app.route("/")
def inicio():
    return render_template("index.html")


@app.route("/api/hoy")
def api_hoy():

    ahora = datetime.now()

    dia = ahora.weekday()
    hora_actual = ahora.strftime("%H:%M")

    conexion = conectar()

    actividades = conexion.execute("""
        SELECT *
        FROM actividades
        WHERE dia_semana = ?
        AND activo = 1
        ORDER BY hora_inicio
    """, (dia,)).fetchall()

    conexion.close()

    actividades = [dict(a) for a in actividades]

    actual = None
    siguiente = None

    for actividad in actividades:

        if (
            actividad["hora_inicio"]
            <= hora_actual
            < actividad["hora_fin"]
        ):
            actual = actividad

        elif actividad["hora_inicio"] > hora_actual:

            if siguiente is None:
                siguiente = actividad

    return jsonify({
        "fecha": ahora.strftime("%Y-%m-%d"),
        "hora": ahora.strftime("%H:%M:%S"),
        "dia_semana": dia,
        "actual": actual,
        "siguiente": siguiente,
        "actividades": actividades
    })


if __name__ == "__main__":

    crear_base_datos()

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )