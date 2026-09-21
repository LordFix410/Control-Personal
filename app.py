from flask import (
    Flask,
    render_template,
    jsonify,
    request
)
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

if __name__ == "__main__":

    crear_base_datos()
    actualizar_base_datos()

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )