from flask import (
    Flask,
    render_template,
    jsonify,
    request
)
import sqlite3
import os
import threading
import time
from datetime import datetime, timedelta
from detector_actividad import obtener_ventana_activa

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database", "control_personal.db")
notificaciones_pendientes = []
detecciones_pendientes = []
actividad_detectada_actual = None
tiempo_minimo_deteccion = 10
seguimiento_automatico = {
    "duolingo": None,
    "kodree": None
}


ultima_deteccion = {
    "duolingo": None,
    "kodree": None
}

def crear_notificacion(titulo, mensaje, tipo="info"):

    notificaciones_pendientes.append({
        "titulo": titulo,
        "mensaje": mensaje,
        "tipo": tipo,
        "fecha": datetime.now().isoformat()
    })

def conectar():
    conexion = sqlite3.connect(DB_PATH)
    conexion.row_factory = sqlite3.Row
    return conexion

def actualizar_base_datos():

    conexion = conectar()
    cursor = conexion.cursor()

    columnas = [
        fila["name"]
        for fila in cursor.execute(
            "PRAGMA table_info(sesiones)"
        ).fetchall()
    ]

    if "estado_timer" not in columnas:
        cursor.execute("""
            ALTER TABLE sesiones
            ADD COLUMN estado_timer TEXT DEFAULT 'detenido'
        """)

    if "ultimo_inicio" not in columnas:
        cursor.execute("""
            ALTER TABLE sesiones
            ADD COLUMN ultimo_inicio TEXT
        """)

    if "omitida" not in columnas:
        cursor.execute("""
            ALTER TABLE sesiones
            ADD COLUMN omitida INTEGER DEFAULT 0
        """)

    conexion.commit()
    conexion.close()

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

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS metas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            descripcion TEXT,
            icono TEXT DEFAULT '🎯',
            categoria TEXT,
            fecha_inicio TEXT NOT NULL,
            fecha_limite TEXT,
            progreso INTEGER DEFAULT 0,
            completada INTEGER DEFAULT 0,
            activa INTEGER DEFAULT 1,
            fecha_completada TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS configuracion (
            clave TEXT PRIMARY KEY,
            valor TEXT NOT NULL
        )
    """)

    configuracion_inicial = {
        "notificar_inicio": "1",
        "notificar_fin": "1",
        "confirmar_cambio_actividad": "1",
        "deteccion_automatica": "0",
        "detectar_duolingo": "1",
        "detectar_kodree": "1",
        "tema": "oscuro",
        "camara_habilitada": "0"
    }

    for clave, valor in configuracion_inicial.items():

        cursor.execute("""
            INSERT OR IGNORE INTO configuracion (
                clave,
                valor
            )
            VALUES (?, ?)
        """, (
            clave,
            valor
        ))

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


#otras rutas:

@app.route("/api/detecciones")
def obtener_detecciones():

    global detecciones_pendientes


    detecciones = (
        detecciones_pendientes.copy()
    )


    detecciones_pendientes.clear()


    return jsonify({
        "detecciones": detecciones
    })

@app.route(
    "/api/actividad/categoria/<categoria>"
)
def actividad_por_categoria(
    categoria
):

    ahora = datetime.now()

    dia = ahora.weekday()


    conexion = conectar()


    actividad = conexion.execute("""
        SELECT
            id,
            nombre,
            icono,
            categoria,
            hora_inicio,
            hora_fin

        FROM actividades

        WHERE
            dia_semana = ?
            AND categoria = ?
            AND activo = 1

        ORDER BY
            CASE
                WHEN hora_inicio <= ?
                AND hora_fin > ?
                THEN 0
                ELSE 1
            END,
            ABS(
                CAST(
                    REPLACE(
                        hora_inicio,
                        ':',
                        ''
                    )
                    AS INTEGER
                )
                -
                CAST(
                    REPLACE(
                        ?,
                        ':',
                        ''
                    )
                    AS INTEGER
                )
            )

        LIMIT 1
    """, (
        dia,
        categoria,
        ahora.strftime("%H:%M"),
        ahora.strftime("%H:%M"),
        ahora.strftime("%H:%M")
    )).fetchone()


    conexion.close()


    if not actividad:

        return jsonify({
            "ok": False,
            "actividad": None
        })


    return jsonify({
        "ok": True,
        "actividad": dict(
            actividad
        )
    })

@app.route("/api/notificaciones")
def obtener_notificaciones():

    global notificaciones_pendientes

    notificaciones = notificaciones_pendientes.copy()

    notificaciones_pendientes.clear()

    return jsonify({
        "notificaciones": notificaciones
    })

@app.route("/api/notificaciones/prueba")
def probar_notificacion():

    crear_notificacion(
        "Control Personal 🎯",
        "Nuestro sistema de notificaciones está funcionando."
    )

    return jsonify({
        "ok": True
    })

@app.route("/api/configuracion")
def obtener_configuracion():

    conexion = conectar()

    filas = conexion.execute("""
        SELECT clave, valor
        FROM configuracion
    """).fetchall()

    conexion.close()

    configuracion = {
        fila["clave"]: fila["valor"]
        for fila in filas
    }

    return jsonify({
        "ok": True,
        "configuracion": configuracion
    })
@app.route(
    "/api/configuracion",
    methods=["PUT"]
)
def guardar_configuracion():

    datos = request.get_json() or {}

    permitidas = {
        "notificar_inicio",
        "notificar_fin",
        "confirmar_cambio_actividad",
        "deteccion_automatica",
        "detectar_duolingo",
        "detectar_kodree",
        "tema",
        "camara_habilitada"
    }

    conexion = conectar()
    cursor = conexion.cursor()

    for clave, valor in datos.items():

        if clave not in permitidas:
            continue

        valor = str(valor)

        cursor.execute("""
            INSERT INTO configuracion (
                clave,
                valor
            )
            VALUES (?, ?)

            ON CONFLICT(clave)
            DO UPDATE SET
                valor = excluded.valor
        """, (
            clave,
            valor
        ))

    conexion.commit()
    conexion.close()

    return jsonify({
        "ok": True,
        "mensaje": "Configuración guardada."
    })
@app.route("/configuracion")
def configuracion():
    return render_template(
        "configuracion.html"
    )
@app.route("/metas")
def metas():
    return render_template("metas.html")

@app.route("/api/metas")
def obtener_metas():

    conexion = conectar()

    metas = conexion.execute("""
        SELECT *
        FROM metas

        ORDER BY
            completada ASC,
            activa DESC,

            CASE
                WHEN fecha_limite IS NULL
                OR fecha_limite = ''
                THEN 1
                ELSE 0
            END,

            fecha_limite ASC,
            id DESC
    """).fetchall()

    conexion.close()

    resultado = []

    hoy = datetime.now().date()

    for meta in metas:

        item = dict(meta)

        dias_restantes = None

        if meta["fecha_limite"]:

            try:

                limite = datetime.strptime(
                    meta["fecha_limite"],
                    "%Y-%m-%d"
                ).date()

                dias_restantes = (
                    limite - hoy
                ).days

            except ValueError:
                pass

        item["dias_restantes"] = (
            dias_restantes
        )

        resultado.append(item)

    activas = sum(
        1
        for meta in resultado
        if meta["activa"]
        and not meta["completada"]
    )

    completadas = sum(
        1
        for meta in resultado
        if meta["completada"]
    )

    return jsonify({
        "metas": resultado,
        "activas": activas,
        "completadas": completadas,
        "total": len(resultado)
    })

@app.route(
    "/api/metas",
    methods=["POST"]
)
def crear_meta():

    datos = request.get_json() or {}

    nombre = datos.get(
        "nombre", ""
    ).strip()

    descripcion = datos.get(
        "descripcion", ""
    ).strip()

    icono = datos.get(
        "icono", "🎯"
    ).strip() or "🎯"

    categoria = datos.get(
        "categoria", ""
    ).strip()

    fecha_limite = datos.get(
        "fecha_limite"
    )

    if not nombre:

        return jsonify({
            "ok": False,
            "mensaje":
                "Escribe el nombre de la meta."
        }), 400

    if fecha_limite:

        try:

            datetime.strptime(
                fecha_limite,
                "%Y-%m-%d"
            )

        except ValueError:

            return jsonify({
                "ok": False,
                "mensaje":
                    "La fecha límite no es válida."
            }), 400

    fecha_inicio = (
        datetime.now()
        .strftime("%Y-%m-%d")
    )

    conexion = conectar()

    cursor = conexion.cursor()

    cursor.execute("""
        INSERT INTO metas (
            nombre,
            descripcion,
            icono,
            categoria,
            fecha_inicio,
            fecha_limite,
            progreso,
            completada,
            activa
        )

        VALUES (?, ?, ?, ?, ?, ?, 0, 0, 1)
    """, (
        nombre,
        descripcion,
        icono,
        categoria,
        fecha_inicio,
        fecha_limite or None
    ))

    meta_id = cursor.lastrowid

    conexion.commit()
    conexion.close()

    return jsonify({
        "ok": True,
        "id": meta_id
    })

@app.route(
    "/api/metas/<int:meta_id>",
    methods=["PUT"]
)
def editar_meta(meta_id):

    datos = request.get_json() or {}

    nombre = datos.get(
        "nombre", ""
    ).strip()

    descripcion = datos.get(
        "descripcion", ""
    ).strip()

    icono = datos.get(
        "icono", "🎯"
    ).strip() or "🎯"

    categoria = datos.get(
        "categoria", ""
    ).strip()

    fecha_limite = datos.get(
        "fecha_limite"
    )

    if not nombre:

        return jsonify({
            "ok": False,
            "mensaje":
                "El nombre es obligatorio."
        }), 400

    conexion = conectar()
    cursor = conexion.cursor()

    existe = cursor.execute("""
        SELECT id
        FROM metas
        WHERE id = ?
    """, (
        meta_id,
    )).fetchone()

    if not existe:

        conexion.close()

        return jsonify({
            "ok": False,
            "mensaje":
                "La meta no existe."
        }), 404

    cursor.execute("""
        UPDATE metas

        SET nombre = ?,
            descripcion = ?,
            icono = ?,
            categoria = ?,
            fecha_limite = ?

        WHERE id = ?
    """, (
        nombre,
        descripcion,
        icono,
        categoria,
        fecha_limite or None,
        meta_id
    ))

    conexion.commit()
    conexion.close()

    return jsonify({
        "ok": True
    })

@app.route(
    "/api/metas/<int:meta_id>/progreso",
    methods=["PATCH"]
)
def actualizar_progreso_meta(meta_id):

    datos = request.get_json() or {}

    try:

        progreso = int(
            datos.get("progreso", 0)
        )

    except (TypeError, ValueError):

        return jsonify({
            "ok": False,
            "mensaje":
                "El progreso no es válido."
        }), 400

    progreso = max(
        0,
        min(100, progreso)
    )

    completada = (
        1 if progreso >= 100 else 0
    )

    fecha_completada = (
        datetime.now().strftime(
            "%Y-%m-%d"
        )
        if completada
        else None
    )

    conexion = conectar()

    cursor = conexion.cursor()

    cursor.execute("""
        UPDATE metas

        SET progreso = ?,
            completada = ?,
            fecha_completada = ?

        WHERE id = ?
    """, (
        progreso,
        completada,
        fecha_completada,
        meta_id
    ))

    if cursor.rowcount == 0:

        conexion.close()

        return jsonify({
            "ok": False,
            "mensaje":
                "La meta no existe."
        }), 404

    conexion.commit()
    conexion.close()

    return jsonify({
        "ok": True,
        "progreso": progreso,
        "completada": completada
    })

@app.route(
    "/api/metas/<int:meta_id>/reabrir",
    methods=["POST"]
)
def reabrir_meta(meta_id):

    conexion = conectar()

    cursor = conexion.cursor()

    cursor.execute("""
        UPDATE metas

        SET completada = 0,
            activa = 1,
            fecha_completada = NULL

        WHERE id = ?
    """, (
        meta_id,
    ))

    if cursor.rowcount == 0:

        conexion.close()

        return jsonify({
            "ok": False,
            "mensaje":
                "La meta no existe."
        }), 404

    conexion.commit()
    conexion.close()

    return jsonify({
        "ok": True
    })

@app.route(
    "/api/metas/<int:meta_id>/estado",
    methods=["PATCH"]
)
def cambiar_estado_meta(meta_id):

    datos = request.get_json() or {}

    activo = (
        1
        if datos.get("activo")
        else 0
    )

    conexion = conectar()

    cursor = conexion.cursor()

    cursor.execute("""
        UPDATE metas
        SET activa = ?
        WHERE id = ?
    """, (
        activo,
        meta_id
    ))

    if cursor.rowcount == 0:

        conexion.close()

        return jsonify({
            "ok": False,
            "mensaje":
                "La meta no existe."
        }), 404

    conexion.commit()
    conexion.close()

    return jsonify({
        "ok": True,
        "activo": activo
    })

@app.route(
    "/api/metas/<int:meta_id>",
    methods=["DELETE"]
)
def eliminar_meta(meta_id):

    conexion = conectar()

    cursor = conexion.cursor()

    cursor.execute("""
        DELETE FROM metas
        WHERE id = ?
    """, (
        meta_id,
    ))

    if cursor.rowcount == 0:

        conexion.close()

        return jsonify({
            "ok": False,
            "mensaje":
                "La meta no existe."
        }), 404

    conexion.commit()
    conexion.close()

    return jsonify({
        "ok": True
    })

@app.route(
    "/api/horario/<int:actividad_id>",
    methods=["PUT"]
)
def editar_actividad(actividad_id):

    datos = request.get_json()

    nombre = (
        datos.get("nombre", "")
        .strip()
    )

    categoria = (
        datos.get("categoria", "")
        .strip()
    )

    icono = (
        datos.get("icono", "📌")
        .strip()
    )

    hora_inicio = datos.get("hora_inicio")
    hora_fin = datos.get("hora_fin")


    if not nombre:

        return jsonify({
            "ok": False,
            "mensaje":
                "El nombre es obligatorio."
        }), 400


    if not hora_inicio or not hora_fin:

        return jsonify({
            "ok": False,
            "mensaje":
                "Selecciona las horas."
        }), 400


    if hora_fin <= hora_inicio:

        return jsonify({
            "ok": False,
            "mensaje":
                "La hora final debe ser posterior a la inicial."
        }), 400


    conexion = conectar()
    cursor = conexion.cursor()


    actividad = cursor.execute("""
        SELECT *
        FROM actividades
        WHERE id = ?
    """, (
        actividad_id,
    )).fetchone()


    if not actividad:

        conexion.close()

        return jsonify({
            "ok": False,
            "mensaje":
                "La actividad no existe."
        }), 404


    # ==========================================
    # COMPROBAR CHOQUE
    # ==========================================

    choque = cursor.execute("""
        SELECT *
        FROM actividades

        WHERE dia_semana = ?
        AND activo = 1
        AND id != ?

        AND hora_inicio < ?
        AND hora_fin > ?

        LIMIT 1
    """, (
        actividad["dia_semana"],
        actividad_id,
        hora_fin,
        hora_inicio
    )).fetchone()


    if choque:

        conexion.close()

        return jsonify({
            "ok": False,
            "conflicto": True,
            "mensaje":
                f'Se cruza con "{choque["nombre"]}" '
                f'de {choque["hora_inicio"]} '
                f'a {choque["hora_fin"]}.'
        }), 409


    cursor.execute("""
        UPDATE actividades

        SET nombre = ?,
            categoria = ?,
            icono = ?,
            hora_inicio = ?,
            hora_fin = ?

        WHERE id = ?
    """, (
        nombre,
        categoria,
        icono or "📌",
        hora_inicio,
        hora_fin,
        actividad_id
    ))


    conexion.commit()
    conexion.close()


    return jsonify({
        "ok": True
    })

@app.route(
    "/api/horario/<int:actividad_id>/estado",
    methods=["PATCH"]
)
def cambiar_estado_actividad(actividad_id):

    datos = request.get_json()

    activo = (
        1
        if datos.get("activo")
        else 0
    )


    conexion = conectar()
    cursor = conexion.cursor()


    actividad = cursor.execute("""
        SELECT *
        FROM actividades
        WHERE id = ?
    """, (
        actividad_id,
    )).fetchone()


    if not actividad:

        conexion.close()

        return jsonify({
            "ok": False,
            "mensaje":
                "La actividad no existe."
        }), 404


    # Si vamos a activarla,
    # verificamos que no choque.

    if activo:

        choque = cursor.execute("""
            SELECT *
            FROM actividades

            WHERE dia_semana = ?
            AND activo = 1
            AND id != ?

            AND hora_inicio < ?
            AND hora_fin > ?

            LIMIT 1
        """, (
            actividad["dia_semana"],
            actividad_id,
            actividad["hora_fin"],
            actividad["hora_inicio"]
        )).fetchone()


        if choque:

            conexion.close()

            return jsonify({
                "ok": False,
                "conflicto": True,
                "mensaje":
                    f'No se puede activar porque se cruza '
                    f'con "{choque["nombre"]}".'
            }), 409


    cursor.execute("""
        UPDATE actividades
        SET activo = ?
        WHERE id = ?
    """, (
        activo,
        actividad_id
    ))


    conexion.commit()
    conexion.close()


    return jsonify({
        "ok": True,
        "activo": activo
    })

@app.route(
    "/api/horario/<int:actividad_id>",
    methods=["DELETE"]
)
def eliminar_actividad(actividad_id):

    conexion = conectar()
    cursor = conexion.cursor()


    actividad = cursor.execute("""
        SELECT *
        FROM actividades
        WHERE id = ?
    """, (
        actividad_id,
    )).fetchone()


    if not actividad:

        conexion.close()

        return jsonify({
            "ok": False,
            "mensaje":
                "La actividad no existe."
        }), 404


    sesiones = cursor.execute("""
        SELECT COUNT(*) AS cantidad
        FROM sesiones
        WHERE actividad_id = ?
    """, (
        actividad_id,
    )).fetchone()["cantidad"]


    # ==========================================
    # TIENE HISTORIAL
    # ==========================================

    if sesiones > 0:

        cursor.execute("""
            UPDATE actividades
            SET activo = 0
            WHERE id = ?
        """, (
            actividad_id,
        ))

        conexion.commit()
        conexion.close()

        return jsonify({
            "ok": True,
            "eliminada": False,
            "desactivada": True,
            "mensaje":
                "La actividad tenía historial, "
                "por lo que fue desactivada."
        })


    # ==========================================
    # SIN HISTORIAL
    # ==========================================

    cursor.execute("""
        DELETE FROM actividades
        WHERE id = ?
    """, (
        actividad_id,
    ))


    conexion.commit()
    conexion.close()


    return jsonify({
        "ok": True,
        "eliminada": True,
        "desactivada": False
    })
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

@app.route("/api/sesion/actual")
def sesion_actual():

    ahora = datetime.now()

    conexion = conectar()

    sesion = conexion.execute("""
        SELECT
            s.*,
            a.nombre,
            a.icono,
            a.categoria
        FROM sesiones s

        INNER JOIN actividades a
            ON a.id = s.actividad_id

        WHERE s.fecha = ?
        AND s.estado != 'completado'

        ORDER BY s.id DESC

        LIMIT 1
    """, (
        ahora.strftime("%Y-%m-%d"),
    )).fetchone()

    conexion.close()

    if not sesion:
        return jsonify({
            "sesion": None
        })

    datos = dict(sesion)

    segundos = datos["segundos_reales"] or 0

    # Si actualmente está contando,
    # calculamos también el tiempo transcurrido
    # desde el último inicio.

    if (
        datos["estado_timer"] == "corriendo"
        and datos["ultimo_inicio"]
    ):

        inicio = datetime.fromisoformat(
            datos["ultimo_inicio"]
        )

        segundos += int(
            (ahora - inicio).total_seconds()
        )

    datos["segundos_actuales"] = segundos

    return jsonify({
        "sesion": datos
    })




@app.route(
    "/api/sesion/pausar",
    methods=["POST"]
)
def pausar_sesion():

    ahora = datetime.now()

    fecha = ahora.strftime("%Y-%m-%d")

    conexion = conectar()
    cursor = conexion.cursor()

    sesion = cursor.execute("""
        SELECT *
        FROM sesiones

        WHERE fecha = ?
        AND estado = 'en_progreso'
        AND estado_timer = 'corriendo'

        ORDER BY id DESC
        LIMIT 1
    """, (
        fecha,
    )).fetchone()

    if not sesion:

        conexion.close()

        return jsonify({
            "ok": False,
            "mensaje": "No hay una sesión activa."
        }), 400

    inicio = datetime.fromisoformat(
        sesion["ultimo_inicio"]
    )

    adicionales = int(
        (ahora - inicio).total_seconds()
    )

    total = (
        sesion["segundos_reales"] or 0
    ) + adicionales

    cursor.execute("""
        UPDATE sesiones

        SET segundos_reales = ?,
            estado_timer = 'pausado',
            ultimo_inicio = NULL

        WHERE id = ?
    """, (
        total,
        sesion["id"]
    ))

    conexion.commit()
    conexion.close()

    return jsonify({
        "ok": True,
        "segundos": total
    })


@app.route(
    "/api/sesion/completar",
    methods=["POST"]
)
def completar_sesion():

    ahora = datetime.now()

    fecha = ahora.strftime("%Y-%m-%d")

    conexion = conectar()
    cursor = conexion.cursor()

    sesion = cursor.execute("""
        SELECT *
        FROM sesiones

        WHERE fecha = ?
        AND estado != 'completado'

        ORDER BY id DESC
        LIMIT 1
    """, (
        fecha,
    )).fetchone()

    if not sesion:

        conexion.close()

        return jsonify({
            "ok": False,
            "mensaje": "No existe una sesión."
        }), 400

    total = sesion["segundos_reales"] or 0

    # Si estaba corriendo, sumamos
    # el último bloque de tiempo.

    if (
        sesion["estado_timer"] == "corriendo"
        and sesion["ultimo_inicio"]
    ):

        inicio = datetime.fromisoformat(
            sesion["ultimo_inicio"]
        )

        total += int(
            (ahora - inicio).total_seconds()
        )

    cursor.execute("""
        UPDATE sesiones

        SET segundos_reales = ?,
            hora_fin = ?,
            estado = 'completado',
            estado_timer = 'detenido',
            ultimo_inicio = NULL

        WHERE id = ?
    """, (
        total,
        ahora.strftime("%H:%M:%S"),
        sesion["id"]
    ))

    conexion.commit()
    conexion.close()

    return jsonify({
        "ok": True,
        "segundos": total
    })

#nuevo endpoint
@app.route("/api/plan-hoy")
def plan_hoy():

    ahora = datetime.now()

    fecha = ahora.strftime("%Y-%m-%d")
    dia = ahora.weekday()

    conexion = conectar()

    actividades = conexion.execute("""
        SELECT
            a.*,

            s.id AS sesion_id,
            s.estado AS sesion_estado,
            s.estado_timer,
            s.segundos_reales,
            s.ultimo_inicio,
            s.hora_inicio AS hora_inicio_real,
            s.hora_fin AS hora_fin_real

        FROM actividades a

        LEFT JOIN sesiones s
            ON s.actividad_id = a.id
            AND s.fecha = ?

        WHERE a.dia_semana = ?
        AND a.activo = 1

        ORDER BY a.hora_inicio
    """, (
        fecha,
        dia
    )).fetchall()

    resultado = []

    for fila in actividades:

        actividad = dict(fila)

        # -------------------------------------
        # DURACIÓN PROGRAMADA
        # -------------------------------------

        inicio_programado = datetime.strptime(
            actividad["hora_inicio"],
            "%H:%M"
        )

        fin_programado = datetime.strptime(
            actividad["hora_fin"],
            "%H:%M"
        )

        duracion_segundos = int(
            (
                fin_programado
                -
                inicio_programado
            ).total_seconds()
        )

        actividad["duracion_objetivo"] = (
            duracion_segundos
        )


        # -------------------------------------
        # TIEMPO REAL
        # -------------------------------------

        segundos_reales = (
            actividad["segundos_reales"] or 0
        )

        if (
            actividad["estado_timer"]
            == "corriendo"
            and actividad["ultimo_inicio"]
        ):

            ultimo_inicio = datetime.fromisoformat(
                actividad["ultimo_inicio"]
            )

            segundos_reales += max(
                0,
                int(
                    (
                        ahora
                        -
                        ultimo_inicio
                    ).total_seconds()
                )
            )

        actividad["segundos_actuales"] = (
            segundos_reales
        )


        # -------------------------------------
        # ESTADO VISUAL
        # -------------------------------------

        if (
            actividad["sesion_estado"]
            == "completado"
        ):

            estado_visual = "completada"

        elif (
            actividad["sesion_estado"]
            == "omitido"
        ):

            estado_visual = "omitida"

        elif (
            actividad["estado_timer"]
            == "corriendo"
        ):

            estado_visual = "en_progreso"

        elif actividad["sesion_id"] is not None:

            estado_visual = "pausada"

        else:

            estado_visual = "pendiente"

        actividad["estado_visual"] = (
            estado_visual
        )

        resultado.append(actividad)

    conexion.close()


    completadas = sum(
        1
        for actividad in resultado
        if actividad["estado_visual"]
        == "completada"
    )

    pendientes = sum(
        1
        for actividad in resultado
        if actividad["estado_visual"]
        in (
            "pendiente",
            "pausada",
            "en_progreso"
        )
    )

    omitidas = sum(
        1
        for actividad in resultado
        if actividad["estado_visual"]
        == "omitida"
    )

    total = len(resultado)

    porcentaje = (
        round(
            completadas / total * 100
        )
        if total > 0
        else 0
    )


    return jsonify({
        "actividades": resultado,
        "total": total,
        "completadas": completadas,
        "pendientes": pendientes,
        "omitidas": omitidas,
        "porcentaje": porcentaje
    })

@app.route(
    "/api/sesion/iniciar/<int:actividad_id>",
    methods=["POST"]
)
def iniciar_sesion(actividad_id):

    ahora = datetime.now()

    fecha = ahora.strftime("%Y-%m-%d")
    fecha_hora = ahora.isoformat(timespec="seconds")

    conexion = conectar()
    cursor = conexion.cursor()


    # ==========================================
    # ¿HAY OTRA ACTIVIDAD CORRIENDO?
    # ==========================================

    activa = cursor.execute("""
        SELECT
            s.*,
            a.nombre,
            a.icono

        FROM sesiones s

        INNER JOIN actividades a
            ON a.id = s.actividad_id

        WHERE s.fecha = ?
        AND s.estado_timer = 'corriendo'
        AND s.actividad_id != ?

        ORDER BY s.id DESC
        LIMIT 1
    """, (
        fecha,
        actividad_id
    )).fetchone()


    # IMPORTANTE:
    # Python también bloquea el inicio.
    # No dependemos solamente de JavaScript.

    if activa:

        conexion.close()

        return jsonify({
            "ok": False,
            "requiere_confirmacion": True,

            "actividad_activa": {
                "id": activa["actividad_id"],
                "nombre": activa["nombre"],
                "icono": activa["icono"]
            },

            "mensaje":
                "Ya existe otra actividad activa."
        }), 409


    # ==========================================
    # BUSCAR SESIÓN DE ESTA ACTIVIDAD
    # ==========================================

    sesion = cursor.execute("""
        SELECT *
        FROM sesiones

        WHERE actividad_id = ?
        AND fecha = ?

        ORDER BY id DESC
        LIMIT 1
    """, (
        actividad_id,
        fecha
    )).fetchone()


    # ==========================================
    # REANUDAR
    # ==========================================

    if sesion:

        # Ya está corriendo.

        if sesion["estado_timer"] == "corriendo":

            conexion.close()

            return jsonify({
                "ok": True,
                "mensaje":
                    "La sesión ya está activa."
            })


        cursor.execute("""
            UPDATE sesiones

            SET estado = 'en_progreso',
                estado_timer = 'corriendo',
                ultimo_inicio = ?,
                omitida = 0

            WHERE id = ?
        """, (
            fecha_hora,
            sesion["id"]
        ))


    # ==========================================
    # NUEVA SESIÓN
    # ==========================================

    else:

        cursor.execute("""
            INSERT INTO sesiones
            (
                actividad_id,
                fecha,
                hora_inicio,
                segundos_reales,
                estado,
                estado_timer,
                ultimo_inicio,
                omitida
            )

            VALUES (?, ?, ?, 0, ?, ?, ?, 0)
        """, (
            actividad_id,
            fecha,
            ahora.strftime("%H:%M:%S"),
            "en_progreso",
            "corriendo",
            fecha_hora
        ))


    conexion.commit()
    conexion.close()


    return jsonify({
        "ok": True
    })
@app.route("/progreso")
def progreso():
    return render_template("progreso.html")

@app.route("/api/progreso")
def obtener_progreso():

    ahora = datetime.now()
    hoy = ahora.date()

    inicio_semana = (
        hoy - timedelta(days=6)
    )

    conexion = conectar()


    # ==========================================
    # RESUMEN DE HOY
    # ==========================================

    fecha_hoy = hoy.strftime("%Y-%m-%d")


    sesiones_hoy = conexion.execute("""
        SELECT
            s.*,
            a.nombre,
            a.categoria,
            a.icono,
            a.hora_inicio AS programada_inicio,
            a.hora_fin AS programada_fin

        FROM sesiones s

        INNER JOIN actividades a
            ON a.id = s.actividad_id

        WHERE s.fecha = ?
    """, (
        fecha_hoy,
    )).fetchall()


    segundos_hoy = 0
    completadas_hoy = 0


    for sesion in sesiones_hoy:

        segundos = sesion["segundos_reales"] or 0


        # Si justo ahora hay una actividad
        # corriendo, incluimos ese bloque.

        if (
            sesion["estado_timer"] == "corriendo"
            and sesion["ultimo_inicio"]
        ):

            inicio = datetime.fromisoformat(
                sesion["ultimo_inicio"]
            )

            segundos += max(
                0,
                int(
                    (
                        ahora - inicio
                    ).total_seconds()
                )
            )


        segundos_hoy += segundos


        if sesion["estado"] == "completado":
            completadas_hoy += 1


    # ==========================================
    # HÁBITOS DE HOY
    # ==========================================

    habitos_activos = conexion.execute("""
        SELECT COUNT(*) AS cantidad
        FROM habitos
        WHERE activo = 1
    """).fetchone()["cantidad"]


    habitos_completados = conexion.execute("""
        SELECT COUNT(*) AS cantidad

        FROM progreso_habitos p

        INNER JOIN habitos h
            ON h.id = p.habito_id

        WHERE p.fecha = ?
        AND p.completado = 1
        AND h.activo = 1
    """, (
        fecha_hoy,
    )).fetchone()["cantidad"]


    porcentaje_habitos = (
        round(
            habitos_completados
            /
            habitos_activos
            *
            100
        )
        if habitos_activos > 0
        else 0
    )


    # ==========================================
    # ÚLTIMOS 7 DÍAS
    # ==========================================

    dias = []


    nombres_cortos = [
        "Lun",
        "Mar",
        "Mié",
        "Jue",
        "Vie",
        "Sáb",
        "Dom"
    ]


    for indice in range(7):

        fecha = inicio_semana + timedelta(
            days=indice
        )


        fecha_texto = fecha.strftime("%Y-%m-%d")


        sesiones_dia = conexion.execute("""
            SELECT
                segundos_reales,
                estado_timer,
                ultimo_inicio

            FROM sesiones

            WHERE fecha = ?
        """, (
            fecha_texto,
        )).fetchall()


        segundos_dia = 0


        for sesion in sesiones_dia:

            segundos = sesion["segundos_reales"] or 0


            if (
                fecha == hoy
                and
                sesion["estado_timer"] == "corriendo"
                and
                sesion["ultimo_inicio"]
            ):

                inicio = datetime.fromisoformat(
                    sesion["ultimo_inicio"]
                )

                segundos += max(
                    0,
                    int(
                        (
                            ahora - inicio
                        ).total_seconds()
                    )
                )


            segundos_dia += segundos


        dias.append({
            "fecha": fecha_texto,

            "dia":
                nombres_cortos[
                    fecha.weekday()
                ],

            "segundos":
                segundos_dia
        })


    # ==========================================
    # TIEMPO POR CATEGORÍA - 7 DÍAS
    # ==========================================

    categorias = conexion.execute("""
        SELECT
            COALESCE(
                a.categoria,
                'Sin categoría'
            ) AS categoria,

            SUM(
                s.segundos_reales
            ) AS segundos

        FROM sesiones s

        INNER JOIN actividades a
            ON a.id = s.actividad_id

        WHERE s.fecha >= ?
        AND s.fecha <= ?

        GROUP BY a.categoria

        ORDER BY segundos DESC
    """, (
        inicio_semana.strftime(
            "%Y-%m-%d"
        ),
        fecha_hoy
    )).fetchall()


    categorias_resultado = [
        {
            "categoria":
                fila["categoria"]
                or "Sin categoría",

            "segundos":
                fila["segundos"]
                or 0
        }

        for fila in categorias
    ]


    # ==========================================
    # ACTIVIDADES DE HOY
    # ==========================================

    actividades_hoy = []


    for sesion in sesiones_hoy:

        segundos = sesion["segundos_reales"] or 0


        if (
            sesion["estado_timer"] == "corriendo"
            and
            sesion["ultimo_inicio"]
        ):

            inicio = datetime.fromisoformat(
                sesion["ultimo_inicio"]
            )

            segundos += max(
                0,
                int(
                    (
                        ahora - inicio
                    ).total_seconds()
                )
            )


        inicio_programado = datetime.strptime(
            sesion["programada_inicio"],
            "%H:%M"
        )


        fin_programado = datetime.strptime(
            sesion["programada_fin"],
            "%H:%M"
        )


        objetivo = int(
            (
                fin_programado
                -
                inicio_programado
            ).total_seconds()
        )


        porcentaje = (
            round(
                segundos
                /
                objetivo
                *
                100
            )
            if objetivo > 0
            else 0
        )


        actividades_hoy.append({
            "id":
                sesion["actividad_id"],

            "nombre":
                sesion["nombre"],

            "icono":
                sesion["icono"],

            "categoria":
                sesion["categoria"],

            "segundos":
                segundos,

            "objetivo":
                objetivo,

            "porcentaje":
                porcentaje,

            "estado":
                sesion["estado"]
        })


    conexion.close()


    return jsonify({

        "resumen": {

            "segundos_hoy":
                segundos_hoy,

            "actividades_completadas":
                completadas_hoy,

            "habitos_completados":
                habitos_completados,

            "habitos_total":
                habitos_activos,

            "porcentaje_habitos":
                porcentaje_habitos
        },

        "dias":
            dias,

        "categorias":
            categorias_resultado,

        "actividades":
            actividades_hoy
    })

@app.route("/habitos")
def habitos():
    return render_template("habitos.html")

@app.route("/api/habitos")
def obtener_habitos():

    hoy = datetime.now().strftime("%Y-%m-%d")

    conexion = conectar()

    habitos = conexion.execute("""
        SELECT
            h.id,
            h.nombre,
            h.icono,
            h.objetivo,
            h.activo,

            COALESCE(
                p.cantidad,
                0
            ) AS cantidad,

            COALESCE(
                p.completado,
                0
            ) AS completado

        FROM habitos h

        LEFT JOIN progreso_habitos p
            ON p.habito_id = h.id
            AND p.fecha = ?

        ORDER BY
            h.activo DESC,
            h.id ASC
    """, (hoy,)).fetchall()


    conexion.close()


    resultado = [
        dict(habito)
        for habito in habitos
    ]


    activos = [
        h
        for h in resultado
        if h["activo"]
    ]


    completados = sum(
        1
        for h in activos
        if h["completado"]
    )


    total = len(activos)


    porcentaje = (
        round(
            completados
            /
            total
            *
            100
        )
        if total > 0
        else 0
    )


    return jsonify({
        "fecha": hoy,
        "habitos": resultado,
        "total": total,
        "completados": completados,
        "porcentaje": porcentaje
    })

@app.route(
    "/api/habitos",
    methods=["POST"]
)
def crear_habito():

    datos = request.get_json()

    nombre = (
        datos.get("nombre", "")
        .strip()
    )

    icono = (
        datos.get("icono", "⭐")
        .strip()
    )

    try:
        objetivo = int(
            datos.get("objetivo", 1)
        )

    except (TypeError, ValueError):
        objetivo = 0


    if not nombre:

        return jsonify({
            "ok": False,
            "mensaje":
                "Escribe el nombre del hábito."
        }), 400


    if objetivo < 1:

        return jsonify({
            "ok": False,
            "mensaje":
                "El objetivo debe ser al menos 1."
        }), 400


    conexion = conectar()

    cursor = conexion.cursor()


    cursor.execute("""
        INSERT INTO habitos
        (
            nombre,
            icono,
            objetivo,
            activo
        )

        VALUES (?, ?, ?, 1)
    """, (
        nombre,
        icono or "⭐",
        objetivo
    ))


    habito_id = cursor.lastrowid


    conexion.commit()
    conexion.close()


    return jsonify({
        "ok": True,
        "id": habito_id
    })

@app.route(
    "/api/habitos/<int:habito_id>",
    methods=["PUT"]
)
def editar_habito(habito_id):

    datos = request.get_json()


    nombre = (
        datos.get("nombre", "")
        .strip()
    )

    icono = (
        datos.get("icono", "⭐")
        .strip()
    )


    try:

        objetivo = int(
            datos.get("objetivo", 1)
        )

    except (TypeError, ValueError):

        objetivo = 0


    if not nombre:

        return jsonify({
            "ok": False,
            "mensaje":
                "El nombre es obligatorio."
        }), 400


    if objetivo < 1:

        return jsonify({
            "ok": False,
            "mensaje":
                "El objetivo debe ser al menos 1."
        }), 400


    conexion = conectar()
    cursor = conexion.cursor()


    existe = cursor.execute("""
        SELECT id
        FROM habitos
        WHERE id = ?
    """, (
        habito_id,
    )).fetchone()


    if not existe:

        conexion.close()

        return jsonify({
            "ok": False,
            "mensaje":
                "El hábito no existe."
        }), 404


    cursor.execute("""
        UPDATE habitos

        SET nombre = ?,
            icono = ?,
            objetivo = ?

        WHERE id = ?
    """, (
        nombre,
        icono or "⭐",
        objetivo,
        habito_id
    ))


    # Si ya había progreso hoy,
    # recalculamos completado según
    # el nuevo objetivo.

    hoy = datetime.now().strftime(
            "%Y-%m-%d"
        )


    cursor.execute("""
        UPDATE progreso_habitos

        SET completado =
            CASE
                WHEN cantidad >= ?
                THEN 1
                ELSE 0
            END

        WHERE habito_id = ?
        AND fecha = ?
    """, (
        objetivo,
        habito_id,
        hoy
    ))


    conexion.commit()
    conexion.close()


    return jsonify({
        "ok": True
    })
@app.route(
    "/api/habitos/<int:habito_id>/sumar",
    methods=["POST"]
)
def sumar_habito(habito_id):

    hoy = datetime.now().strftime(
            "%Y-%m-%d"
        )


    conexion = conectar()
    cursor = conexion.cursor()


    habito = cursor.execute("""
        SELECT *
        FROM habitos

        WHERE id = ?
        AND activo = 1
    """, (
        habito_id,
    )).fetchone()


    if not habito:

        conexion.close()

        return jsonify({
            "ok": False,
            "mensaje":
                "El hábito no existe o está desactivado."
        }), 404


    progreso = cursor.execute("""
        SELECT *
        FROM progreso_habitos

        WHERE habito_id = ?
        AND fecha = ?

        ORDER BY id DESC
        LIMIT 1
    """, (
        habito_id,
        hoy
    )).fetchone()


    if progreso:

        nueva_cantidad = progreso["cantidad"] + 1


        completado = (
            1
            if nueva_cantidad
            >= habito["objetivo"]
            else 0
        )


        cursor.execute("""
            UPDATE progreso_habitos

            SET cantidad = ?,
                completado = ?

            WHERE id = ?
        """, (
            nueva_cantidad,
            completado,
            progreso["id"]
        ))


    else:

        nueva_cantidad = 1

        completado = (
            1
            if nueva_cantidad
            >= habito["objetivo"]
            else 0
        )


        cursor.execute("""
            INSERT INTO progreso_habitos
            (
                habito_id,
                fecha,
                cantidad,
                completado
            )

            VALUES (?, ?, ?, ?)
        """, (
            habito_id,
            hoy,
            nueva_cantidad,
            completado
        ))


    conexion.commit()
    conexion.close()


    return jsonify({
        "ok": True,
        "cantidad": nueva_cantidad,
        "completado": completado
    })
@app.route(
    "/api/habitos/<int:habito_id>/restar",
    methods=["POST"]
)
def restar_habito(habito_id):

    hoy = datetime.now().strftime(
            "%Y-%m-%d"
        )


    conexion = conectar()
    cursor = conexion.cursor()


    habito = cursor.execute("""
        SELECT *
        FROM habitos
        WHERE id = ?
    """, (
        habito_id,
    )).fetchone()


    if not habito:

        conexion.close()

        return jsonify({
            "ok": False,
            "mensaje":
                "El hábito no existe."
        }), 404


    progreso = cursor.execute("""
        SELECT *
        FROM progreso_habitos

        WHERE habito_id = ?
        AND fecha = ?

        ORDER BY id DESC
        LIMIT 1
    """, (
        habito_id,
        hoy
    )).fetchone()


    if not progreso:

        conexion.close()

        return jsonify({
            "ok": True,
            "cantidad": 0,
            "completado": 0
        })


    nueva_cantidad = max(
        0,
        progreso["cantidad"] - 1
    )


    completado = (
        1
        if nueva_cantidad
        >= habito["objetivo"]
        else 0
    )


    cursor.execute("""
        UPDATE progreso_habitos

        SET cantidad = ?,
            completado = ?

        WHERE id = ?
    """, (
        nueva_cantidad,
        completado,
        progreso["id"]
    ))


    conexion.commit()
    conexion.close()


    return jsonify({
        "ok": True,
        "cantidad": nueva_cantidad,
        "completado": completado
    })
@app.route(
    "/api/habitos/<int:habito_id>/estado",
    methods=["PATCH"]
)
def cambiar_estado_habito(habito_id):

    datos = request.get_json()


    activo = (
        1
        if datos.get("activo")
        else 0
    )


    conexion = conectar()
    cursor = conexion.cursor()


    existe = cursor.execute("""
        SELECT id
        FROM habitos
        WHERE id = ?
    """, (
        habito_id,
    )).fetchone()


    if not existe:

        conexion.close()

        return jsonify({
            "ok": False,
            "mensaje":
                "El hábito no existe."
        }), 404


    cursor.execute("""
        UPDATE habitos
        SET activo = ?
        WHERE id = ?
    """, (
        activo,
        habito_id
    ))


    conexion.commit()
    conexion.close()


    return jsonify({
        "ok": True,
        "activo": activo
    })
@app.route(
    "/api/habitos/<int:habito_id>",
    methods=["DELETE"]
)
def eliminar_habito(habito_id):

    conexion = conectar()
    cursor = conexion.cursor()


    habito = cursor.execute("""
        SELECT *
        FROM habitos
        WHERE id = ?
    """, (
        habito_id,
    )).fetchone()


    if not habito:

        conexion.close()

        return jsonify({
            "ok": False,
            "mensaje":
                "El hábito no existe."
        }), 404


    historial = cursor.execute("""
        SELECT COUNT(*) AS cantidad

        FROM progreso_habitos

        WHERE habito_id = ?
    """, (
        habito_id,
    )).fetchone()["cantidad"]


    # ==========================================
    # TIENE HISTORIAL
    # ==========================================

    if historial > 0:

        cursor.execute("""
            UPDATE habitos

            SET activo = 0

            WHERE id = ?
        """, (
            habito_id,
        ))


        conexion.commit()
        conexion.close()


        return jsonify({
            "ok": True,
            "eliminado": False,
            "desactivado": True,
            "mensaje":
                "El hábito tiene historial, "
                "por lo que fue desactivado."
        })


    # ==========================================
    # SIN HISTORIAL
    # ==========================================

    cursor.execute("""
        DELETE FROM habitos
        WHERE id = ?
    """, (
        habito_id,
    ))


    conexion.commit()
    conexion.close()


    return jsonify({
        "ok": True,
        "eliminado": True,
        "desactivado": False
    })

@app.route("/horario")
def horario():
    return render_template("horario.html")

@app.route("/api/horario")
def obtener_horario():

    conexion = conectar()

    actividades = conexion.execute("""
        SELECT
            id,
            nombre,
            categoria,
            icono,
            hora_inicio,
            hora_fin,
            dia_semana,
            activo

        FROM actividades

        ORDER BY
            dia_semana,
            hora_inicio
    """).fetchall()

    conexion.close()

    return jsonify({
        "actividades": [
            dict(actividad)
            for actividad in actividades
        ]
    })

@app.route(
    "/api/horario",
    methods=["POST"]
)
def crear_actividad():

    datos = request.get_json()

    nombre = (
        datos.get("nombre", "")
        .strip()
    )

    categoria = (
        datos.get("categoria", "")
        .strip()
    )

    icono = (
        datos.get("icono", "📌")
        .strip()
    )

    hora_inicio = datos.get("hora_inicio")
    hora_fin = datos.get("hora_fin")

    dias = datos.get("dias", [])


    # ==========================================
    # VALIDACIÓN
    # ==========================================

    if not nombre:

        return jsonify({
            "ok": False,
            "mensaje":
                "Escribe el nombre de la actividad."
        }), 400


    if not hora_inicio or not hora_fin:

        return jsonify({
            "ok": False,
            "mensaje":
                "Selecciona la hora de inicio y final."
        }), 400


    if hora_fin <= hora_inicio:

        return jsonify({
            "ok": False,
            "mensaje":
                "La hora final debe ser posterior a la inicial."
        }), 400


    if not dias:

        return jsonify({
            "ok": False,
            "mensaje":
                "Selecciona al menos un día."
        }), 400


    conexion = conectar()
    cursor = conexion.cursor()


    # ==========================================
    # REVISAR CHOQUES
    # ==========================================

    conflictos = []

    nombres_dias = [
        "Lunes",
        "Martes",
        "Miércoles",
        "Jueves",
        "Viernes",
        "Sábado",
        "Domingo"
    ]


    for dia in dias:

        choque = cursor.execute("""
            SELECT *
            FROM actividades

            WHERE dia_semana = ?
            AND activo = 1

            AND hora_inicio < ?
            AND hora_fin > ?

            LIMIT 1
        """, (
            dia,
            hora_fin,
            hora_inicio
        )).fetchone()


        if choque:

            conflictos.append({
                "dia": nombres_dias[dia],
                "actividad": choque["nombre"],
                "hora_inicio": choque["hora_inicio"],
                "hora_fin": choque["hora_fin"]
            })


    if conflictos:

        conexion.close()

        return jsonify({
            "ok": False,
            "conflicto": True,
            "mensaje":
                "La actividad se cruza con otra.",
            "conflictos": conflictos
        }), 409


    # ==========================================
    # CREAR
    # ==========================================

    ids = []


    for dia in dias:

        cursor.execute("""
            INSERT INTO actividades
            (
                nombre,
                categoria,
                icono,
                hora_inicio,
                hora_fin,
                dia_semana,
                activo
            )

            VALUES (?, ?, ?, ?, ?, ?, 1)
        """, (
            nombre,
            categoria,
            icono or "📌",
            hora_inicio,
            hora_fin,
            dia
        ))

        ids.append(
            cursor.lastrowid
        )


    conexion.commit()
    conexion.close()


    return jsonify({
        "ok": True,
        "ids": ids
    })

@app.route(
    "/api/sesion/pausar-activa",
    methods=["POST"]
)
def pausar_sesion_activa():

    ahora = datetime.now()
    fecha = ahora.strftime("%Y-%m-%d")

    conexion = conectar()
    cursor = conexion.cursor()


    sesiones = cursor.execute("""
        SELECT *
        FROM sesiones

        WHERE fecha = ?
        AND estado_timer = 'corriendo'
    """, (
        fecha,
    )).fetchall()


    # Esto además repara el bug actual:
    # si accidentalmente quedaron DOS corriendo,
    # las pausamos todas.

    for sesion in sesiones:

        total = (
            sesion["segundos_reales"]
            or 0
        )


        if sesion["ultimo_inicio"]:

            inicio = datetime.fromisoformat(
                sesion["ultimo_inicio"]
            )

            total += max(
                0,
                int(
                    (
                        ahora - inicio
                    ).total_seconds()
                )
            )


        cursor.execute("""
            UPDATE sesiones

            SET segundos_reales = ?,
                estado_timer = 'pausado',
                ultimo_inicio = NULL

            WHERE id = ?
        """, (
            total,
            sesion["id"]
        ))


    conexion.commit()
    conexion.close()


    return jsonify({
        "ok": True,
        "pausadas": len(sesiones)
    })

@app.route(
    "/api/actividad/retomar/<int:actividad_id>",
    methods=["POST"]
)

def retomar_actividad(actividad_id):

    ahora = datetime.now()

    fecha = ahora.strftime("%Y-%m-%d")

    conexion = conectar()
    cursor = conexion.cursor()


    sesion = cursor.execute("""
        SELECT *
        FROM sesiones

        WHERE actividad_id = ?
        AND fecha = ?

        ORDER BY id DESC
        LIMIT 1
    """, (
        actividad_id,
        fecha
    )).fetchone()


    if not sesion:

        conexion.close()

        return jsonify({
            "ok": False,
            "mensaje":
                "No existe una sesión para retomar."
        }), 404


    cursor.execute("""
        UPDATE sesiones

        SET estado = 'en_progreso',
            estado_timer = 'pausado',
            ultimo_inicio = NULL,
            hora_fin = NULL,
            omitida = 0

        WHERE id = ?
    """, (
        sesion["id"],
    ))


    conexion.commit()
    conexion.close()

    return jsonify({
        "ok": True
    })

# ==========================================
# MONITOR AUTOMÁTICO DEL HORARIO
# ==========================================

monitor_horario_iniciado = False

eventos_notificados = set()


def obtener_configuracion_valor(clave, predeterminado="0"):

    conexion = conectar()

    fila = conexion.execute("""
        SELECT valor
        FROM configuracion
        WHERE clave = ?
    """, (
        clave,
    )).fetchone()

    conexion.close()

    if fila:
        return fila["valor"]

    return predeterminado


def monitor_horario():

    global eventos_notificados

    print(
        "[MONITOR] Monitor de horario iniciado."
    )


    while True:

        try:

            ahora = datetime.now()

            fecha_actual = ahora.strftime(
                "%Y-%m-%d"
            )

            hora_actual = ahora.strftime(
                "%H:%M"
            )

            dia_semana = ahora.weekday()


            conexion = conectar()

            actividades = conexion.execute("""
                SELECT
                    id,
                    nombre,
                    icono,
                    hora_inicio,
                    hora_fin

                FROM actividades

                WHERE
                    dia_semana = ?
                    AND activo = 1
            """, (
                dia_semana,
            )).fetchall()

            conexion.close()


            notificar_inicio = obtener_configuracion_valor(
                    "notificar_inicio",
                    "1"
                ) == "1"

            notificar_fin = obtener_configuracion_valor(
                    "notificar_fin",
                    "1"
                ) == "1"


            for actividad in actividades:

                actividad_id = actividad["id"]

                icono = actividad["icono"] or "🎯"

                nombre = actividad["nombre"]


                # ==========================
                # INICIO
                # ==========================

                clave_inicio = (
                    fecha_actual,
                    actividad_id,
                    "inicio"
                )


                if (
                    notificar_inicio
                    and
                    hora_actual
                    ==
                    actividad["hora_inicio"]
                    and
                    clave_inicio
                    not in eventos_notificados
                ):

                    crear_notificacion(
                        f"{icono} Es hora de comenzar",
                        nombre,
                        "inicio"
                    )

                    eventos_notificados.add(
                        clave_inicio
                    )


                    print(
                        "[NOTIFICACIÓN]",
                        "Inicio:",
                        nombre
                    )


                # ==========================
                # FIN
                # ==========================

                clave_fin = (
                    fecha_actual,
                    actividad_id,
                    "fin"
                )


                if (
                    notificar_fin
                    and
                    hora_actual
                    ==
                    actividad["hora_fin"]
                    and
                    clave_fin
                    not in eventos_notificados
                ):

                    crear_notificacion(
                        f"{icono} Tiempo programado terminado",
                        nombre,
                        "fin"
                    )

                    eventos_notificados.add(
                        clave_fin
                    )


                    print(
                        "[NOTIFICACIÓN]",
                        "Fin:",
                        nombre
                    )


            # Limpiar eventos de días anteriores

            eventos_notificados = {
                evento
                for evento
                in eventos_notificados
                if evento[0] == fecha_actual
            }


        except Exception as error:

            print(
                "[MONITOR] Error:",
                error
            )


        # Revisar cada 10 segundos

        time.sleep(10)
def registrar_deteccion(
    tipo,
    icono,
    titulo,
    mensaje,
    categoria
):

    global ultima_deteccion
    global detecciones_pendientes


    ahora = datetime.now()


    ultima = ultima_deteccion.get(
        tipo
    )


    # Evitar que pregunte constantemente.
    # Después de mostrar una detección,
    # espera 15 minutos antes de volver
    # a preguntar por el mismo sitio.

    if ultima:

        diferencia = (
            ahora - ultima
        ).total_seconds()


        if diferencia < 900:
            return


    # Si ya hay una actividad corriendo,
    # igualmente permitimos la detección.
    # El usuario decidirá si quiere cambiar.


    detecciones_pendientes.append({

        "tipo": tipo,

        "icono": icono,

        "titulo": titulo,

        "mensaje": mensaje,

        "categoria": categoria,

        "fecha":
            ahora.isoformat()
    })


    ultima_deteccion[tipo] = ahora


    print(
        "[DETECTOR]",
        titulo
    )

def identificar_actividad_detectada(ventana):

    if not ventana:
        return None

    titulo = (
        ventana.get("titulo")
        or ""
    ).lower()

    proceso = (
        ventana.get("proceso")
        or ""
    ).lower()

    navegadores = {
        "msedge.exe",
        "chrome.exe",
        "firefox.exe"
    }

    if proceso not in navegadores:
        return None


    detectar_duolingo = (
        obtener_configuracion_valor(
            "detectar_duolingo",
            "1"
        ) == "1"
    )

    detectar_kodree = (
        obtener_configuracion_valor(
            "detectar_kodree",
            "1"
        ) == "1"
    )


    if (
        detectar_duolingo
        and
        "duolingo" in titulo
    ):
        return {
            "tipo": "duolingo",
            "nombre": "Duolingo",
            "categoria": "ingles",
            "icono": "🇬🇧"
        }


    if (
        detectar_kodree
        and
        "kodree" in titulo
    ):
        return {
            "tipo": "kodree",
            "nombre": "Kodree",
            "categoria": "carrera",
            "icono": "🎓"
        }


    return None
def iniciar_presencia_detectada(
    actividad
):

    global actividad_detectada_actual


    actividad_detectada_actual = {

        "tipo":
            actividad["tipo"],

        "nombre":
            actividad["nombre"],

        "categoria":
            actividad["categoria"],

        "icono":
            actividad["icono"],

        "inicio":
            datetime.now(),

        "confirmada":
            False
    }


    print(
        "[PRESENCIA] Entraste a",
        actividad["nombre"],
        flush=True
    )
def finalizar_presencia_detectada(
    motivo="cambio de ventana"
):

    global actividad_detectada_actual
    global seguimiento_automatico


    if not actividad_detectada_actual:
        return


    # Guardamos todos los datos ANTES
    # de modificar/eliminar la detección actual.

    actividad = actividad_detectada_actual

    ahora = datetime.now()

    nombre = actividad["nombre"]
    tipo = actividad["tipo"]
    confirmada = actividad["confirmada"]

    segundos = int(
        (
            ahora
            -
            actividad["inicio"]
        ).total_seconds()
    )


    # ==========================================
    # MOSTRAR RESULTADO DE PRESENCIA
    # ==========================================

    if confirmada:

        print(
            "[PRESENCIA] Saliste de",
            nombre,
            "- Tiempo:",
            segundos,
            "segundos",
            "- Motivo:",
            motivo,
            flush=True
        )

    else:

        print(
            "[PRESENCIA]",
            nombre,
            "ignorado.",
            "Solo estuvo activo",
            segundos,
            "segundos.",
            flush=True
        )


    # ==========================================
    # PAUSA AUTOMÁTICA
    # ==========================================

    seguimiento = seguimiento_automatico.get(
        tipo
    )


    if (
        confirmada
        and
        seguimiento
        and
        seguimiento.get("autorizado")
    ):

        actividad_id = seguimiento[
            "actividad_id"
        ]


        pausada = pausar_actividad_detectada(
            actividad_id
        )


        if pausada:

            print(
                "[AUTO] Actividad pausada:",
                nombre,
                flush=True
            )

        else:

            print(
                "[AUTO] No había temporizador corriendo para pausar:",
                nombre,
                flush=True
            )


    # ==========================================
    # LIMPIAR PRESENCIA
    # ==========================================

    actividad_detectada_actual = None
# ==========================================
# DETECTOR AUTOMÁTICO DE ACTIVIDADES
# ==========================================

def monitor_actividad_pc():

    global actividad_detectada_actual

    print(
        "[DETECTOR] Monitor de actividad iniciado.",
        flush=True
    )


    while True:

        try:

            deteccion_automatica = (
                obtener_configuracion_valor(
                    "deteccion_automatica",
                    "0"
                ) == "1"
            )


            # ==========================================
            # DETECCIÓN DESACTIVADA
            # ==========================================

            if not deteccion_automatica:

                if actividad_detectada_actual:

                    finalizar_presencia_detectada(
                        motivo="detección desactivada"
                    )

                time.sleep(2)
                continue


            ventana = obtener_ventana_activa()

            detectada = identificar_actividad_detectada(
                ventana
            )


            # ==========================================
            # NO ESTAMOS EN DUOLINGO/KODREE
            # ==========================================

            if detectada is None:

                if actividad_detectada_actual:

                    finalizar_presencia_detectada(
                        motivo="cambio de ventana"
                    )

                time.sleep(2)
                continue


            # ==========================================
            # ENTRAMOS A UNA ACTIVIDAD DETECTABLE
            # ==========================================

            if actividad_detectada_actual is None:

                iniciar_presencia_detectada(
                    detectada
                )

                time.sleep(2)
                continue


            # ==========================================
            # CAMBIAMOS DUOLINGO <-> KODREE
            # ==========================================

            if (
                actividad_detectada_actual["tipo"]
                !=
                detectada["tipo"]
            ):

                finalizar_presencia_detectada(
                    motivo="cambio de actividad"
                )

                iniciar_presencia_detectada(
                    detectada
                )

                time.sleep(2)
                continue


            # ==========================================
            # SEGUIMOS EN LA MISMA ACTIVIDAD
            # ==========================================

            ahora = datetime.now()

            segundos = int(
                (
                    ahora
                    -
                    actividad_detectada_actual["inicio"]
                ).total_seconds()
            )


            # Confirmar presencia después del mínimo

            if (
                not actividad_detectada_actual["confirmada"]
                and
                segundos >= tiempo_minimo_deteccion
            ):

                actividad_detectada_actual[
                    "confirmada"
                ] = True

                tipo = (actividad_detectada_actual["tipo"])

                seguimiento = (
                    seguimiento_automatico.get(
                        tipo
                    )
                )


                # Ya fue autorizado anteriormente.
                # Reanudamos sin volver a preguntar.

                if (
                    seguimiento
                    and
                    seguimiento.get(
                        "autorizado"
                    )
                ):

                    actividad_id = seguimiento[
                        "actividad_id"
                    ]


                    if reanudar_actividad_detectada(
                        actividad_id
                    ):

                        print(
                            "[AUTO] Actividad reanudada:",
                            actividad_detectada_actual[
                                "nombre"
                            ],
                            flush=True
                        )


                    # Ya está autorizado:
                    # NO mostramos otra pregunta.

                    time.sleep(2)
                    continue

                print(
                    "[PRESENCIA]",
                    actividad_detectada_actual["nombre"],
                    "confirmada después de",
                    segundos,
                    "segundos.",
                    flush=True
                )


                registrar_deteccion(
                    actividad_detectada_actual["tipo"],
                    actividad_detectada_actual["icono"],
                    (
                        actividad_detectada_actual["nombre"]
                        + " detectado"
                    ),
                    (
                        "Llevas "
                        + str(segundos)
                        + " segundos trabajando aquí."
                    ),
                    actividad_detectada_actual["categoria"]
                )


        except Exception as error:

            print(
                "[DETECTOR] Error:",
                error,
                flush=True
            )


        time.sleep(2)

@app.route(
    "/api/deteccion/autorizar/<tipo>/<int:actividad_id>",
    methods=["POST"]
)
def autorizar_deteccion(tipo, actividad_id):

    global seguimiento_automatico

    if tipo not in seguimiento_automatico:
        return jsonify({
            "ok": False,
            "error": "Tipo de detección no válido."
        }), 400


    seguimiento_automatico[tipo] = {
        "actividad_id": actividad_id,
        "autorizado": True
    }


    return jsonify({
        "ok": True,
        "tipo": tipo,
        "actividad_id": actividad_id
    })

def pausar_actividad_detectada(actividad_id):

    ahora = datetime.now()

    conexion = conectar()


    sesion = conexion.execute("""
        SELECT *
        FROM sesiones

        WHERE
            actividad_id = ?
            AND fecha = ?
            AND estado = 'en_progreso'
            AND estado_timer = 'corriendo'

        ORDER BY id DESC

        LIMIT 1
    """, (
        actividad_id,
        ahora.strftime("%Y-%m-%d")
    )).fetchone()


    if not sesion:

        conexion.close()
        return False


    segundos = sesion["segundos_reales"] or 0


    if sesion["ultimo_inicio"]:

        ultimo_inicio = datetime.fromisoformat(
            sesion["ultimo_inicio"]
        )

        segundos += int(
            (
                ahora - ultimo_inicio
            ).total_seconds()
        )


    conexion.execute("""
        UPDATE sesiones

        SET
            segundos_reales = ?,
            estado_timer = 'pausado',
            ultimo_inicio = NULL

        WHERE id = ?
    """, (
        segundos,
        sesion["id"]
    ))


    conexion.commit()
    conexion.close()

    return True
def reanudar_actividad_detectada(actividad_id):

    ahora = datetime.now()

    conexion = conectar()


    # Primero comprobamos que no haya
    # otra actividad corriendo.

    otra = conexion.execute("""
        SELECT id, actividad_id
        FROM sesiones

        WHERE
            fecha = ?
            AND estado = 'en_progreso'
            AND estado_timer = 'corriendo'
            AND actividad_id != ?

        ORDER BY id DESC

        LIMIT 1
    """, (
        ahora.strftime("%Y-%m-%d"),
        actividad_id
    )).fetchone()


    if otra:

        conexion.close()
        return False


    sesion = conexion.execute("""
        SELECT *
        FROM sesiones

        WHERE
            actividad_id = ?
            AND fecha = ?
            AND estado = 'en_progreso'

        ORDER BY id DESC

        LIMIT 1
    """, (
        actividad_id,
        ahora.strftime("%Y-%m-%d")
    )).fetchone()


    if not sesion:

        conexion.close()
        return False


    if sesion["estado_timer"] == "corriendo":

        conexion.close()
        return True


    conexion.execute("""
        UPDATE sesiones

        SET
            estado_timer = 'corriendo',
            ultimo_inicio = ?

        WHERE id = ?
    """, (
        ahora.isoformat(),
        sesion["id"]
    ))


    conexion.commit()
    conexion.close()

    return True

if __name__ == "__main__":

    crear_base_datos()
    actualizar_base_datos()

    hilo_monitor = threading.Thread(
        target=monitor_horario,
        daemon=True
    )

    hilo_monitor.start()

    hilo_detector = threading.Thread(
        target=monitor_actividad_pc,
        daemon=True
    )

    hilo_detector.start()

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True,
         use_reloader=False
    )