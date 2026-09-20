from flask import Flask, render_template
import sqlite3
import os

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database", "control_personal.db")


def crear_base_datos():

    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

    conexion = sqlite3.connect(DB_PATH)
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
    conexion.close()


@app.route("/")
def inicio():
    return render_template("index.html")


if __name__ == "__main__":
    crear_base_datos()

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )