import win32gui
import win32process

try:
    import psutil
except ImportError:
    psutil = None


def obtener_ventana_activa():

    try:

        ventana = win32gui.GetForegroundWindow()

        if not ventana:
            return None

        titulo = win32gui.GetWindowText(
            ventana
        ).strip()

        _, pid = win32process.GetWindowThreadProcessId(
            ventana
        )

        proceso = ""

        if psutil:

            try:

                proceso = psutil.Process(
                    pid
                ).name()

            except Exception:
                proceso = ""

        return {
            "titulo": titulo,
            "proceso": proceso,
            "pid": pid
        }

    except Exception as error:

        print(
            "[DETECTOR] Error:",
            error
        )

        return None


if __name__ == "__main__":

    import time

    print(
        "Detector iniciado."
    )

    print(
        "Cambia entre ventanas para probar.\n"
    )

    ultimo = None

    while True:

        ventana = obtener_ventana_activa()

        if ventana:

            identificador = (
                ventana["titulo"],
                ventana["proceso"]
            )

            if identificador != ultimo:

                ultimo = identificador

                print(
                    "\nVENTANA ACTIVA"
                )

                print(
                    "Título :",
                    ventana["titulo"]
                )

                print(
                    "Proceso:",
                    ventana["proceso"]
                )

        time.sleep(1)