let consultandoDetecciones = false;


async function revisarDetecciones() {

    if (consultandoDetecciones) {
        return;
    }


    consultandoDetecciones = true;


    try {

        const respuesta =
            await fetch(
                "/api/detecciones",
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
            const deteccion
            of datos.detecciones || []
        ) {

            await mostrarDeteccion(
                deteccion
            );
        }


    } catch (error) {

        console.error(
            "Error consultando detecciones:",
            error
        );

    } finally {

        consultandoDetecciones =
            false;
    }
}



async function mostrarDeteccion(
    deteccion
) {

    try {

        const respuesta =
            await fetch(
                `/api/actividad/categoria/${
                    encodeURIComponent(
                        deteccion.categoria
                    )
                }`
            );


        const datos =
            await respuesta.json();


        if (
            !respuesta.ok
            ||
            !datos.actividad
        ) {

            mostrarNotificacion(
                `${deteccion.icono} ${deteccion.titulo}`,
                deteccion.mensaje
            );

            return;
        }


        const actividad =
            datos.actividad;


        crearAvisoDeteccion(
            deteccion,
            actividad
        );


    } catch (error) {

        console.error(
            "Error buscando actividad:",
            error
        );
    }
}



function crearAvisoDeteccion(
    deteccion,
    actividad
) {

    prepararNotificaciones();


    const contenedor =
        document.getElementById(
            "contenedor-notificaciones"
        );


    const aviso =
        document.createElement("div");


    aviso.className =
        "notificacion-app deteccion-app";


    const titulo =
        document.createElement("h3");


    titulo.textContent =
        `${deteccion.icono} ${deteccion.titulo}`;


    const mensaje =
        document.createElement("p");


    mensaje.textContent =
        deteccion.mensaje;


    const acciones =
        document.createElement("div");


    acciones.className =
        "acciones-deteccion";


    const iniciar =
        document.createElement("button");


    iniciar.className =
        "btn-deteccion-iniciar";


    iniciar.textContent =
        `▶ Iniciar ${actividad.nombre}`;


    const ignorar =
        document.createElement("button");


    ignorar.className =
        "btn-deteccion-ignorar";


    ignorar.textContent =
        "Ignorar";


    acciones.appendChild(
        iniciar
    );


    acciones.appendChild(
        ignorar
    );


    aviso.appendChild(
        titulo
    );


    aviso.appendChild(
        mensaje
    );


    aviso.appendChild(
        acciones
    );


    contenedor.appendChild(
        aviso
    );


    ignorar.addEventListener(
        "click",
        () => aviso.remove()
    );


    iniciar.addEventListener(
        "click",
        async () => {

            iniciar.disabled = true;


            try {

                /*
                    Esta función ya existe
                    en nuestro app.js.

                    Además, nuestro backend
                    ya controla que solo haya
                    UNA actividad corriendo.
                */

                await iniciarActividad(
                    actividad.id
                );


                const autorizacion =
                    await fetch(
                        `/api/deteccion/autorizar/${
                            deteccion.tipo
                        }/${
                            actividad.id
                        }`,
                        {
                            method: "POST"
                        }
                    );


                if (!autorizacion.ok) {

                    throw new Error(
                        "No se pudo autorizar el seguimiento."
                    );
                }


                aviso.remove();


            } catch (error) {

                console.error(
                    "Error iniciando actividad:",
                    error
                );


                iniciar.disabled = false;
            }
        }
    );
}



revisarDetecciones();


setInterval(
    revisarDetecciones,
    3000
);