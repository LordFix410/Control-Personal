import argparse
import json
import os
import time
import cv2
import mediapipe as mp

parser = argparse.ArgumentParser()
parser.add_argument("--estado", required=True)
args = parser.parse_args()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODELO = os.path.join(BASE_DIR, "models", "pose_landmarker_lite.task")
NOMBRE = "Control de concentracion"

if not os.path.exists(MODELO):
    raise FileNotFoundError(f"No se encontro el modelo: {MODELO}")

BaseOptions = mp.tasks.BaseOptions
PoseLandmarker = mp.tasks.vision.PoseLandmarker
PoseLandmarkerOptions = mp.tasks.vision.PoseLandmarkerOptions
RunningMode = mp.tasks.vision.RunningMode

options = PoseLandmarkerOptions(
    base_options=BaseOptions(model_asset_path=MODELO),
    running_mode=RunningMode.IMAGE,
    num_poses=1,
    min_pose_detection_confidence=0.45,
    min_pose_presence_confidence=0.45
)

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
if not cap.isOpened():
    cap = cv2.VideoCapture(0)
if not cap.isOpened():
    raise RuntimeError("No se pudo abrir la camara 0.")

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

landmarker = PoseLandmarker.create_from_options(options)
ultimo_guardado = 0.0


def guardar_estado(presente):
    datos = {
        "presente": bool(presente),
        "timestamp": time.time()
    }

    try:
        with open(
            args.estado,
            "w",
            encoding="utf-8"
        ) as archivo:
            json.dump(datos, archivo)

    except (PermissionError, OSError):
        # Si app.py está leyendo el archivo justo
        # en ese instante, simplemente lo intentamos
        # en el siguiente ciclo de cámara.
        pass


try:
    cv2.namedWindow(NOMBRE, cv2.WINDOW_NORMAL)

    while True:
        ok, frame = cap.read()
        if not ok:
            guardar_estado(False)
            time.sleep(0.1)
            continue

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        imagen = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        resultado = landmarker.detect(imagen)

        presente = False
        if resultado.pose_landmarks:
            puntos = resultado.pose_landmarks[0]
            # Nariz + hombros/cadera: tolerante para leer, escribir o mirar otra pantalla.
            indices = [0, 11, 12, 23, 24]
            visibles = 0
            for i in indices:
                p = puntos[i]
                if getattr(p, "visibility", 1.0) >= 0.35 and getattr(p, "presence", 1.0) >= 0.35:
                    visibles += 1
            presente = visibles >= 2

        ahora = time.monotonic()
        if ahora - ultimo_guardado >= 0.35:
            guardar_estado(presente)
            ultimo_guardado = ahora

        texto = "PRESENTE" if presente else "SIN PRESENCIA"
        cv2.putText(frame, texto, (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2, cv2.LINE_AA)
        cv2.putText(frame, "Q / ESC / X para cerrar", (20, 75), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255,255,255), 2, cv2.LINE_AA)
        cv2.imshow(NOMBRE, frame)

        tecla = cv2.waitKey(1) & 0xFF
        if tecla == ord("q") or tecla == 27:
            break

        try:
            if cv2.getWindowProperty(NOMBRE, cv2.WND_PROP_VISIBLE) < 1:
                break
        except cv2.error:
            break
finally:
    cap.release()
    landmarker.close()
    cv2.destroyAllWindows()
    try:
        if os.path.exists(args.estado):
            os.remove(args.estado)
    except OSError:
        pass
