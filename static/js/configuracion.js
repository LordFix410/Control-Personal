// ==========================================
// ELEMENTOS
// ==========================================

const confirmarCambio =
    document.getElementById(
        "confirmarCambio"
    );

const notificarInicio =
    document.getElementById(
        "notificarInicio"
    );

const notificarFin =
    document.getElementById(
        "notificarFin"
    );

const deteccionAutomatica =
    document.getElementById(
        "deteccionAutomatica"
    );

const detectarDuolingo =
    document.getElementById(
        "detectarDuolingo"
    );

const detectarKodree =
    document.getElementById(
        "detectarKodree"
    );

const temaAplicacion =
    document.getElementById(
        "temaAplicacion"
    );

const camaraHabilitada =
    document.getElementById(
        "camaraHabilitada"
    );

const estadoGuardado =
    document.getElementById(
        "estadoGuardado"
    );

const subopcionesDeteccion =
    document.getElementById(
        "subopcionesDeteccion"
    );


let cargandoConfiguracion = true;

let temporizadorMensaje = null;


// ==========================================
// CONVERSIÓN
// ==========================================

function convertirBooleano(
    valor
) {

    return (
        String(valor) === "1"
        ||
        String(valor).toLowerCase()
            === "true"
    );
}


// ==========================================
// CARGAR CONFIGURACIÓN
// ==========================================

async function cargarConfiguracion() {

    cargandoConfiguracion = true;


    try {

        const respuesta =
            await fetch(
                "/api/configuracion"
            );


        const datos =
            await respuesta.json();


        if (!respuesta.ok) {

            throw new Error(
                "No se pudo cargar la configuración."
            );
        }


        const config =
            datos.configuracion || {};


        confirmarCambio.checked =
            convertirBooleano(
                config.confirmar_cambio_actividad
            );


        notificarInicio.checked =
            convertirBooleano(
                config.notificar_inicio
            );


        notificarFin.checked =
            convertirBooleano(
                config.notificar_fin
            );


        deteccionAutomatica.checked =
            convertirBooleano(
                config.deteccion_automatica
            );


        detectarDuolingo.checked =
            convertirBooleano(
                config.detectar_duolingo
            );


        detectarKodree.checked =
            convertirBooleano(
                config.detectar_kodree
            );


        camaraHabilitada.checked =
            convertirBooleano(
                config.camara_habilitada
            );


        temaAplicacion.value =
            config.tema
            ||
            "oscuro";


        actualizarEstadoDeteccion();


    } catch (error) {

        console.error(
            "Error cargando configuración:",
            error
        );


        mostrarEstado(
            "⚠ Error al cargar",
            true
        );

    } finally {

        cargandoConfiguracion = false;
    }
}


// ==========================================
// GUARDAR UNA OPCIÓN
// ==========================================

async function guardarOpcion(
    clave,
    valor
) {

    if (cargandoConfiguracion) {
        return;
    }


    try {

        const respuesta =
            await fetch(
                "/api/configuracion",
                {
                    method: "PUT",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body:
                        JSON.stringify({
                            [clave]: valor
                        })
                }
            );


        const datos =
            await respuesta.json();


        if (!respuesta.ok) {

            throw new Error(
                datos.mensaje
                ||
                "No se pudo guardar."
            );
        }


        mostrarEstado(
            "✓ Guardado"
        );


    } catch (error) {

        console.error(
            "Error guardando configuración:",
            error
        );


        mostrarEstado(
            "⚠ No se pudo guardar",
            true
        );
    }
}


// ==========================================
// MENSAJE GUARDADO
// ==========================================

function mostrarEstado(
    texto,
    error = false
) {

    clearTimeout(
        temporizadorMensaje
    );


    estadoGuardado.textContent =
        texto;


    estadoGuardado.style.color =
        error
        ? "#e4777f"
        : "#69bd80";


    estadoGuardado.classList.add(
        "visible"
    );


    temporizadorMensaje =
        setTimeout(
            () => {

                estadoGuardado.classList.remove(
                    "visible"
                );

            },
            1800
        );
}


// ==========================================
// DETECCIÓN
// ==========================================

function actualizarEstadoDeteccion() {

    if (
        deteccionAutomatica.checked
    ) {

        subopcionesDeteccion
            .classList.remove(
                "desactivadas"
            );

    } else {

        subopcionesDeteccion
            .classList.add(
                "desactivadas"
            );
    }
}


// ==========================================
// EVENTOS
// ==========================================

confirmarCambio.addEventListener(
    "change",
    () => {

        guardarOpcion(
            "confirmar_cambio_actividad",
            confirmarCambio.checked
                ? "1"
                : "0"
        );
    }
);


notificarInicio.addEventListener(
    "change",
    () => {

        guardarOpcion(
            "notificar_inicio",
            notificarInicio.checked
                ? "1"
                : "0"
        );
    }
);


notificarFin.addEventListener(
    "change",
    () => {

        guardarOpcion(
            "notificar_fin",
            notificarFin.checked
                ? "1"
                : "0"
        );
    }
);


deteccionAutomatica.addEventListener(
    "change",
    () => {

        actualizarEstadoDeteccion();


        guardarOpcion(
            "deteccion_automatica",
            deteccionAutomatica.checked
                ? "1"
                : "0"
        );
    }
);


detectarDuolingo.addEventListener(
    "change",
    () => {

        guardarOpcion(
            "detectar_duolingo",
            detectarDuolingo.checked
                ? "1"
                : "0"
        );
    }
);


detectarKodree.addEventListener(
    "change",
    () => {

        guardarOpcion(
            "detectar_kodree",
            detectarKodree.checked
                ? "1"
                : "0"
        );
    }
);


temaAplicacion.addEventListener(
    "change",
    () => {

        guardarOpcion(
            "tema",
            temaAplicacion.value
        );
    }
);


// ==========================================
// INICIO
// ==========================================

cargarConfiguracion();