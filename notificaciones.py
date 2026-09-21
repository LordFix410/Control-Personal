from winotify import Notification


def enviar_notificacion(
    titulo,
    mensaje
):
    try:

        notificacion = Notification(
            app_id="Control Personal",
            title=titulo,
            msg=mensaje,
            duration="short"
        )

        notificacion.show()

        return True

    except Exception as error:

        print(
            "[NOTIFICACIONES]",
            error
        )

        return False

if __name__ == "__main__":

    enviar_notificacion(
        "Control Personal 🎯",
        "Las notificaciones están funcionando."
    )
