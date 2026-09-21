let consultandoNotificaciones = false;


function prepararNotificaciones() {

    if (
        document.getElementById(
            "contenedor-notificaciones"
        )
    ) {
        return;
    }


    const contenedor =
        document.createElement("div");

    contenedor.id =
        "contenedor-notificaciones";


    document.body.appendChild(
        contenedor
    );
}


function mostrarNotificacion(
    titulo,
    mensaje
) {

    prepararNotificaciones();


    const contenedor =
        document.getElementById(
            "contenedor-notificaciones"
        );


    const notificacion =
        document.createElement("div");


    notificacion.className =
        "notificacion-app";


    const tituloElemento =
        document.createElement("h3");

    tituloElemento.textContent =
        titulo;


    const mensajeElemento =
        document.createElement("p");

    mensajeElemento.textContent =
        mensaje;


    const cerrar =
        document.createElement("button");

    cerrar.className =
        "cerrar-notificacion";

    cerrar.textContent = "✕";


    notificacion.appendChild(
        tituloElemento
    );

    notificacion.appendChild(
        mensajeElemento
    );

    notificacion.appendChild(
        cerrar
    );


    contenedor.appendChild(
        notificacion
    );


    function eliminar() {

        if (
            notificacion.classList
                .contains("saliendo")
        ) {
            return;
        }


        notificacion.classList.add(
            "saliendo"
        );


        setTimeout(
            () => notificacion.remove(),
            250
        );
    }


    cerrar.addEventListener(
        "click",
        eliminar
    );


    setTimeout(
        eliminar,
        7000
    );
}


async function revisarNotificaciones() {

    if (consultandoNotificaciones) {
        return;
    }


    consultandoNotificaciones = true;


    try {

        const respuesta =
            await fetch(
                "/api/notificaciones",
                {
                    cache: "no-store"
                }
            );


        if (!respuesta.ok) {
            return;
        }


        const datos =
            await respuesta.json();


        for (
            const notificacion
            of datos.notificaciones || []
        ) {

            mostrarNotificacion(
                notificacion.titulo,
                notificacion.mensaje
            );
        }


    } catch (error) {

        console.error(
            "Error consultando notificaciones:",
            error
        );

    } finally {

        consultandoNotificaciones =
            false;
    }
}


prepararNotificaciones();

revisarNotificaciones();

setInterval(
    revisarNotificaciones,
    2000
);