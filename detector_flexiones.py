import cv2
import argparse
import json
import mediapipe as mp
import numpy as np
import math
import os
import time
import queue
import threading
import pyttsx3

from mediapipe.tasks import python
from mediapipe.tasks.python import vision

parser = argparse.ArgumentParser()
parser.add_argument(
    "--resultado",
    default=None,
    help="Archivo JSON donde guardar el resultado del entrenamiento."
)
ARGS = parser.parse_args()


# ============================================================
# CONFIGURACION
# ============================================================

MODELO = r"D:\GITHUB\Control Personal\models\pose_landmarker_lite.task"
ANCHO = 1280
ALTO = 720
FPS = 30

# Angulos sencillos para flexion lateral.
ARRIBA = 155
ABAJO = 105
INICIO_BAJADA = 145

# Ritmo: no exige exactamente 2 s; solo avisa si vas demasiado rapido.
BAJADA_RAPIDA = 0.65
SUBIDA_RAPIDA = 0.55

# Postura lateral.
CUERPO_MIN = 150          # hombro-cadera-tobillo
CUELLO_MIN = 135          # oreja-hombro-cadera
PERSISTENCIA_ERROR = 0.45

# ============================================================
# VOZ: UNA SOLA CONSEJERA + COLA FIFO
# ============================================================

cola_voz = queue.Queue(maxsize=8)
pendientes = set()
ultima_por_clave = {}
voz_activa = True


def hilo_voz():
    try:
        motor = pyttsx3.init()
        motor.setProperty("rate", 165)
        motor.setProperty("volume", 1.0)
    except Exception as e:
        print("No se pudo iniciar la voz:", e)
        return

    while voz_activa:
        try:
            item = cola_voz.get(timeout=0.25)
        except queue.Empty:
            continue

        if item is None:
            cola_voz.task_done()
            break

        texto, clave = item
        try:
            print("COACH:", texto)
            motor.say(texto)
            motor.runAndWait()
        except Exception as e:
            print("Error de voz:", e)
        finally:
            pendientes.discard(clave)
            cola_voz.task_done()


threading.Thread(target=hilo_voz, daemon=True).start()


def decir(texto, clave=None, cooldown=2.0):
    """Encola y NO interrumpe lo que ya se esta diciendo."""
    clave = clave or texto
    ahora = time.perf_counter()

    if clave in pendientes:
        return
    if ahora - ultima_por_clave.get(clave, -999) < cooldown:
        return

    try:
        cola_voz.put_nowait((texto, clave))
        pendientes.add(clave)
        ultima_por_clave[clave] = ahora
    except queue.Full:
        # Si la cola ya esta llena, no acumulamos consejos viejos.
        pass


# ============================================================
# CAMARA: SOLO IVCAM
# ============================================================

def buscar_ivcam():
    # Primero intentamos por nombre DirectShow.
    try:
        from pygrabber.dshow_graph import FilterGraph
        nombres = FilterGraph().get_input_devices()
        for i, nombre in enumerate(nombres):
            if "ivcam" in nombre.lower() or "e2esoft" in nombre.lower():
                cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
                if cap.isOpened():
                    cap.set(cv2.CAP_PROP_FRAME_WIDTH, ANCHO)
                    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, ALTO)
                    cap.set(cv2.CAP_PROP_FPS, FPS)
                    ok, frame = cap.read()
                    if ok and frame is not None:
                        print(f"IVCam: [{i}] {nombre}")
                        return cap
                cap.release()
    except Exception as e:
        print("No pude identificar IVCam por nombre:", e)

    # Fallback: probar indices.
    for i in range(6):
        cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
        if cap.isOpened():
            ok, frame = cap.read()
            if ok and frame is not None:
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, ANCHO)
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, ALTO)
                cap.set(cv2.CAP_PROP_FPS, FPS)
                print(f"Usando camara indice {i}. Verifica que sea IVCam.")
                return cap
        cap.release()

    raise RuntimeError("No pude abrir IVCam.")


# ============================================================
# MEDIAPIPE
# ============================================================

if not os.path.exists(MODELO):
    raise FileNotFoundError(f"No existe el modelo: {MODELO}")

opciones = vision.PoseLandmarkerOptions(
    base_options=python.BaseOptions(model_asset_path=MODELO),
    running_mode=vision.RunningMode.VIDEO,
    num_poses=1,
    min_pose_detection_confidence=0.45,
    min_pose_presence_confidence=0.45,
    min_tracking_confidence=0.45,
)

landmarker = vision.PoseLandmarker.create_from_options(opciones)

CONEXIONES = [
    (7, 11), (8, 12),
    (11, 12), (11, 13), (13, 15),
    (12, 14), (14, 16),
    (11, 23), (12, 24), (23, 24),
    (23, 25), (25, 27), (24, 26), (26, 28)
]


def visible(p, minimo=0.35):
    return getattr(p, "visibility", 1.0) >= minimo


def xy(p):
    return np.array([p.x, p.y], dtype=float)


def angulo(a, b, c):
    ba = a - b
    bc = c - b
    den = np.linalg.norm(ba) * np.linalg.norm(bc)
    if den < 1e-9:
        return None
    coseno = np.clip(np.dot(ba, bc) / den, -1.0, 1.0)
    return float(np.degrees(np.arccos(coseno)))


def promedio(vals):
    vals = [v for v in vals if v is not None]
    return sum(vals) / len(vals) if vals else None


def analizar(frame, timestamp_ms):
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    imagen = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
    resultado = landmarker.detect_for_video(imagen, timestamp_ms)

    if not resultado.pose_landmarks:
        return None

    p = resultado.pose_landmarks[0]

    # izquierda
    ci = angulo(xy(p[11]), xy(p[13]), xy(p[15])) if all(visible(p[i]) for i in (11,13,15)) else None
    bi = angulo(xy(p[11]), xy(p[23]), xy(p[27])) if all(visible(p[i]) for i in (11,23,27)) else None
    ni = angulo(xy(p[7]), xy(p[11]), xy(p[23])) if all(visible(p[i]) for i in (7,11,23)) else None

    # derecha
    cd = angulo(xy(p[12]), xy(p[14]), xy(p[16])) if all(visible(p[i]) for i in (12,14,16)) else None
    bd = angulo(xy(p[12]), xy(p[24]), xy(p[28])) if all(visible(p[i]) for i in (12,24,28)) else None
    nd = angulo(xy(p[8]), xy(p[12]), xy(p[24])) if all(visible(p[i]) for i in (8,12,24)) else None

    return {
        "puntos": p,
        "codo": promedio([ci, cd]),
        "cuerpo": promedio([bi, bd]),
        "cuello": promedio([ni, nd]),
    }


def dibujar(frame, datos):
    if not datos:
        return
    p = datos["puntos"]
    h, w = frame.shape[:2]

    def pt(i):
        return int(p[i].x*w), int(p[i].y*h)

    for a,b in CONEXIONES:
        if visible(p[a]) and visible(p[b]):
            cv2.line(frame, pt(a), pt(b), (255,255,255), 3, cv2.LINE_AA)
    for i in sorted({x for par in CONEXIONES for x in par}):
        if visible(p[i]):
            cv2.circle(frame, pt(i), 5, (0,220,0), -1, cv2.LINE_AA)


# ============================================================
# ESTADO
# ============================================================

cap = buscar_ivcam()

estado = "PREPARATE"
validas = 0
no_contadas = 0
inicio_bajada = None
inicio_subida = None
min_codo = 180.0
ultimo_codo = None

# Correcciones sostenidas para que no hable por ruido de un solo frame.
desde_error = {}
errores_rep = set()

inicio_programa = time.perf_counter()
inicio_entreno = None
timestamp_anterior = -1

# 3,2,1 se mete una sola vez a la cola.
decir("Prepárate.", "inicio", 999)
decir("Tres.", "tres", 999)
decir("Dos.", "dos", 999)
decir("Uno.", "uno", 999)
decir("Ya. Comienza.", "ya", 999)

# Damos unos segundos para la cuenta visual/voz antes de activar conteo.
activar_en = inicio_programa + 4.2

NOMBRE = "Coach Flexiones - IVCam 2D"
cv2.namedWindow(NOMBRE, cv2.WINDOW_NORMAL)


def error_persistente(clave, condicion, ahora):
    if condicion:
        desde_error.setdefault(clave, ahora)
        return ahora - desde_error[clave] >= PERSISTENCIA_ERROR
    desde_error.pop(clave, None)
    return False


try:
    while True:
        ok, frame = cap.read()
        if not ok or frame is None:
            continue

        frame = cv2.flip(frame, 1)
        ahora = time.perf_counter()
        timestamp_ms = int((ahora - inicio_programa) * 1000)
        if timestamp_ms <= timestamp_anterior:
            timestamp_ms = timestamp_anterior + 1
        timestamp_anterior = timestamp_ms

        datos = analizar(frame, timestamp_ms)
        dibujar(frame, datos)

        mensaje = "Colocate de lado y deja todo el cuerpo visible."
        fase_tiempo = 0.0

        if ahora < activar_en:
            faltan = activar_en - ahora
            if faltan > 3:
                mensaje = "PREPARATE - 3"
            elif faltan > 2:
                mensaje = "PREPARATE - 2"
            elif faltan > 1:
                mensaje = "PREPARATE - 1"
            else:
                mensaje = "YA"
        elif datos is None or datos["codo"] is None:
            estado = "PREPARATE"
            mensaje = "No veo bien el brazo. Vuelve a posicion."
            decir("No veo bien tu brazo. Vuelve a posición.", "no_visible", 5)
        else:
            if inicio_entreno is None:
                inicio_entreno = ahora

            codo = datos["codo"]
            cuerpo = datos["cuerpo"]
            cuello = datos["cuello"]

            # -------- POSTURA: solo consejos sencillos --------
            moviendo = estado in ("BAJANDO", "ABAJO", "SUBIENDO")

            if cuerpo is not None:
                mal_cuerpo = error_persistente("cuerpo", cuerpo < CUERPO_MIN, ahora)
                if mal_cuerpo:
                    if moviendo:
                        errores_rep.add("postura")
                    decir("Mantén hombros, cadera y tobillos alineados.", "postura", 5)

            if cuello is not None:
                mal_cuello = error_persistente("cuello", cuello < CUELLO_MIN, ahora)
                if mal_cuello:
                    decir("Mantén la cabeza alineada con la espalda.", "cuello", 5)

            # -------- CONTADOR SIMPLE --------
            if estado == "PREPARATE":
                if codo >= ARRIBA:
                    estado = "ARRIBA"
                    mensaje = "LISTO - empieza cuando quieras"

            elif estado == "ARRIBA":
                mensaje = "ARRIBA"
                if codo < INICIO_BAJADA:
                    estado = "BAJANDO"
                    inicio_bajada = ahora
                    min_codo = codo
                    errores_rep.clear()
                    mensaje = "BAJA"
                    decir("Baja controlado.", "baja", 1.2)

            elif estado == "BAJANDO":
                fase_tiempo = ahora - inicio_bajada
                min_codo = min(min_codo, codo)
                mensaje = f"BAJANDO  {fase_tiempo:.1f}s"

                if codo <= ABAJO:
                    if fase_tiempo < BAJADA_RAPIDA:
                        errores_rep.add("rapida_bajada")
                        decir("Más lento al bajar.", "rapida_bajada", 3)

                    estado = "ABAJO"
                    mensaje = "ABAJO - AHORA SUBE"
                    decir("Ahora sube.", "sube", 1.2)

                # Regresó arriba sin llegar a profundidad.
                elif ultimo_codo is not None and codo > ultimo_codo + 3 and min_codo > ABAJO:
                    # Esperamos a que realmente regrese arriba para declararla incompleta.
                    if codo >= ARRIBA:
                        no_contadas += 1
                        decir("Baja un poco más en la siguiente.", "profundidad", 3)
                        estado = "ARRIBA"
                        inicio_bajada = None
                        min_codo = 180.0
                        errores_rep.clear()

            elif estado == "ABAJO":
                mensaje = "ABAJO - SUBE"
                if codo > ABAJO + 8:
                    estado = "SUBIENDO"
                    inicio_subida = ahora

            elif estado == "SUBIENDO":
                fase_tiempo = ahora - inicio_subida
                mensaje = f"SUBIENDO  {fase_tiempo:.1f}s"

                if codo >= ARRIBA:
                    if fase_tiempo < SUBIDA_RAPIDA:
                        errores_rep.add("rapida_subida")
                        decir("Controla un poco más la subida.", "rapida_subida", 3)

                    # Para empezar, postura/ritmo aconsejan pero NO destruyen el conteo.
                    # Una repeticion completa arriba->abajo->arriba cuenta.
                    validas += 1
                    mensaje = f"REPETICION {validas}"
                    estado = "ARRIBA"
                    inicio_bajada = None
                    inicio_subida = None
                    min_codo = 180.0
                    errores_rep.clear()

            ultimo_codo = codo

        # ====================================================
        # HUD
        # ====================================================
        h,w = frame.shape[:2]
        cv2.rectangle(frame, (0,0), (w,105), (0,0,0), -1)

        cv2.putText(frame, f"FLEXIONES: {validas}", (20,35),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255,255,255), 2, cv2.LINE_AA)
        cv2.putText(frame, f"INCOMPLETAS: {no_contadas}", (250,35),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (220,220,220), 2, cv2.LINE_AA)

        if inicio_entreno:
            total = ahora - inicio_entreno
            mins = int(total//60)
            segs = int(total%60)
            reloj = f"{mins:02d}:{segs:02d}"
        else:
            reloj = "00:00"

        cv2.putText(frame, f"TIEMPO: {reloj}", (520,35),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2, cv2.LINE_AA)

        if datos:
            c = datos.get("codo")
            b = datos.get("cuerpo")
            n = datos.get("cuello")
            valores = f"Codo: {int(c) if c else '--'}  Cuerpo: {int(b) if b else '--'}  Cuello: {int(n) if n else '--'}"
            cv2.putText(frame, valores, (20,67),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.55, (210,210,210), 1, cv2.LINE_AA)

        cv2.putText(frame, mensaje, (20,96),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.72, (255,255,255), 2, cv2.LINE_AA)

        cv2.imshow(NOMBRE, frame)

        tecla = cv2.waitKey(1) & 0xFF

        # Cerrar con Q o ESC
        if tecla == ord("q") or tecla == 27:
            break

        # Cerrar al pulsar la X de la ventana
        try:
            if cv2.getWindowProperty(
                NOMBRE,
                cv2.WND_PROP_VISIBLE
            ) < 1:
                break
        except cv2.error:
            break

finally:
    voz_activa = False
    try:
        cola_voz.put_nowait(None)
    except Exception:
        pass
    cap.release()
    landmarker.close()
    cv2.destroyAllWindows()

duracion_final = 0

if inicio_entreno is not None:
    duracion_final = int(
        time.perf_counter() - inicio_entreno
    )

resultado_final = {
    "tipo": "flexiones",
    "repeticiones": validas,
    "incompletas": no_contadas,
    "duracion_segundos": duracion_final
}

if ARGS.resultado:
    try:
        with open(
            ARGS.resultado,
            "w",
            encoding="utf-8"
        ) as archivo:
            json.dump(
                resultado_final,
                archivo,
                ensure_ascii=False,
                indent=2
            )
    except Exception as error:
        print(
            "No se pudo guardar el resultado:",
            error
        )

print(
    f"Terminado. Flexiones completas: {validas}. "
    f"Incompletas: {no_contadas}. "
    f"Duración: {duracion_final}s."
)
