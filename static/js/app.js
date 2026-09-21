// ==========================================
// ELEMENTOS
// ==========================================

const fecha =
    document.getElementById("fecha");

const temporizador =
    document.getElementById("temporizador");

const botonIniciar =
    document.getElementById("iniciar");

const botonCompletar =
    document.getElementById("completar");


const actividadIcono =
    document.getElementById("actividadIcono");

const actividadNombre =
    document.getElementById("actividadNombre");

const actividadCategoria =
    document.getElementById("actividadCategoria");

const actividadHorario =
    document.getElementById("actividadHorario");

const estadoActividad =
    document.getElementById("estadoActividad");


const tiempoObjetivo =
    document.getElementById("tiempoObjetivo");

const barraTiempo =
    document.getElementById("barraTiempo");

const textoTiempo =
    document.getElementById("textoTiempo");


const siguienteNombre =
    document.getElementById("siguienteNombre");

const siguienteHora =
    document.getElementById("siguienteHora");


const listaActividades =
    document.getElementById("listaActividades");


const porcentajeProgreso =
    document.getElementById("porcentajeProgreso");

const barraProgreso =
    document.getElementById("barraProgreso");

const cantidadCompletadas =
    document.getElementById("cantidadCompletadas");

const cantidadPendientes =
    document.getElementById("cantidadPendientes");

const cantidadOmitidas =
    document.getElementById("cantidadOmitidas");

const planCompletadas =
    document.getElementById("planCompletadas");

const planTotal =
    document.getElementById("planTotal");


// MODAL

const modalCambio =
    document.getElementById("modalCambio");

const modalActividadActual =
    document.getElementById("modalActividadActual");

const modalTiempoActual =
    document.getElementById("modalTiempoActual");

const cancelarCambio =
    document.getElementById("cancelarCambio");

const confirmarCambio =
    document.getElementById("confirmarCambio");


// ==========================================
// VARIABLES
// ==========================================

let actividadHorarioActual = null;

let sesionActual = null;

let actividadSeleccionada = null;

let segundos = 0;

let objetivoSegundos = 0;

let intervaloVisual = null;


// ==========================================
// FECHA
// ==========================================

function actualizarFecha() {

    const ahora = new Date();

    fecha.textContent =
        ahora.toLocaleDateString(
            "es-GT",
            {
                weekday: "long",
                day: "numeric",
                month: "long",
                year: "numeric"
            }
        );
}


// ==========================================
// HORAS
// ==========================================

function convertirHora(hora) {

    if (!hora) {
        return "--";
    }

    const partes = hora.split(":");

    let horas = Number(partes[0]);

    const minutos = partes[1];

    const periodo =
        horas >= 12 ? "PM" : "AM";

    horas %= 12;

    if (horas === 0) {
        horas = 12;
    }

    return `${horas}:${minutos} ${periodo}`;
}


function calcularDuracion(
    horaInicio,
    horaFin
) {

    if (!horaInicio || !horaFin) {
        return 0;
    }

    const inicio =
        horaInicio.split(":");

    const fin =
        horaFin.split(":");

    const segundosInicio =
        Number(inicio[0]) * 3600
        +
        Number(inicio[1]) * 60;

    const segundosFin =
        Number(fin[0]) * 3600
        +
        Number(fin[1]) * 60;

    return Math.max(
        0,
        segundosFin - segundosInicio
    );
}


// ==========================================
// FORMATEAR DURACIÓN
// ==========================================

function formatearTiempo(totalSegundos) {

    totalSegundos =
        Math.max(
            0,
            Math.floor(totalSegundos || 0)
        );

    const horas =
        Math.floor(
            totalSegundos / 3600
        );

    const minutos =
        Math.floor(
            (totalSegundos % 3600) / 60
        );

    const segundosRestantes =
        totalSegundos % 60;

    return (
        String(horas).padStart(2, "0")
        +
        ":"
        +
        String(minutos).padStart(2, "0")
        +
        ":"
        +
        String(segundosRestantes)
            .padStart(2, "0")
    );
}


function formatearDuracionCorta(
    totalSegundos
) {

    const minutos =
        Math.round(
            totalSegundos / 60
        );

    if (minutos < 60) {
        return `${minutos} min`;
    }

    const horas =
        Math.floor(minutos / 60);

    const resto =
        minutos % 60;

    if (resto === 0) {
        return `${horas} h`;
    }

    return `${horas} h ${resto} min`;
}


// ==========================================
// TEMPORIZADOR
// ==========================================

function dibujarTemporizador() {

    temporizador.textContent =
        formatearTiempo(segundos);

    tiempoObjetivo.textContent =
        formatearTiempo(objetivoSegundos);


    let porcentaje = 0;

    if (objetivoSegundos > 0) {

        porcentaje =
            Math.round(
                segundos
                /
                objetivoSegundos
                *
                100
            );
    }


    textoTiempo.textContent =
        `${porcentaje}% del tiempo objetivo`;


    // Visualmente la barra no pasa de 100%.
    // El texto sí puede mostrar 120%, 150%, etc.

    barraTiempo.style.width =
        `${Math.min(porcentaje, 100)}%`;
}


function detenerIntervaloVisual() {

    if (intervaloVisual) {

        clearInterval(
            intervaloVisual
        );

        intervaloVisual = null;
    }
}


function iniciarIntervaloVisual() {

    detenerIntervaloVisual();

    intervaloVisual =
        setInterval(
            () => {

                segundos++;

                dibujarTemporizador();

            },
            1000
        );
}


// ==========================================
// HORARIO
// ==========================================

async function cargarHorarioActual() {

    try {

        const respuesta =
            await fetch("/api/hoy");

        const datos =
            await respuesta.json();

        actividadHorarioActual =
            datos.actual;


        if (datos.siguiente) {

            siguienteNombre.textContent =
                datos.siguiente.icono
                +
                " "
                +
                datos.siguiente.nombre;

            siguienteHora.textContent =
                convertirHora(
                    datos.siguiente.hora_inicio
                );

        } else {

            siguienteNombre.textContent =
                "🌙 No quedan actividades";

            siguienteHora.textContent =
                "";
        }

    } catch (error) {

        console.error(
            "Error cargando horario:",
            error
        );
    }
}


// ==========================================
// ACTIVIDAD PRINCIPAL
// ==========================================

function mostrarActividadPrincipal(
    actividad
) {

    if (!actividad) {

        actividadIcono.textContent =
            "😎";

        actividadNombre.textContent =
            "Tiempo libre";

        actividadCategoria.textContent =
            "No hay actividad activa";

        actividadHorario.textContent =
            "";

        estadoActividad.textContent =
            "○ SIN ACTIVIDAD";

        objetivoSegundos = 0;

        segundos = 0;

        dibujarTemporizador();

        return;
    }


    actividadIcono.textContent =
        actividad.icono || "📌";

    actividadNombre.textContent =
        actividad.nombre;

    actividadCategoria.textContent =
        actividad.categoria || "";


    actividadHorario.textContent =
        convertirHora(
            actividad.hora_inicio
        )
        +
        " - "
        +
        convertirHora(
            actividad.hora_fin
        );


    objetivoSegundos =
        calcularDuracion(
            actividad.hora_inicio,
            actividad.hora_fin
        );


    if (
        actividad.estado_timer
        === "corriendo"
    ) {

        estadoActividad.textContent =
            "▶ EN PROGRESO";

        botonIniciar.textContent =
            "⏸ Pausar";

    } else if (actividad.sesion_id) {

        estadoActividad.textContent =
            "⏸ PAUSADA";

        botonIniciar.textContent =
            "▶ Continuar";

    } else {

        estadoActividad.textContent =
            "○ PENDIENTE";

        botonIniciar.textContent =
            "▶ Iniciar";
    }


    dibujarTemporizador();
}


// ==========================================
// SESIÓN ACTUAL
// ==========================================

async function cargarSesion() {

    try {

        const respuesta =
            await fetch(
                "/api/sesion/actual"
            );

        const datos =
            await respuesta.json();

        sesionActual =
            datos.sesion;


        if (!sesionActual) {

            detenerIntervaloVisual();

            segundos = 0;

            // Si no estamos realizando nada,
            // mostramos lo que corresponde
            // según el horario.

            if (actividadHorarioActual) {

                mostrarActividadPrincipal(
                    actividadHorarioActual
                );

            } else {

                mostrarActividadPrincipal(
                    null
                );
            }

            return;
        }


        segundos =
            sesionActual.segundos_actuales
            || 0;


        // Buscamos datos completos
        // en el plan de hoy.

        const respuestaPlan =
            await fetch(
                "/api/plan-hoy"
            );

        const datosPlan =
            await respuestaPlan.json();


        const actividad =
            datosPlan.actividades.find(
                item =>
                    item.id
                    ===
                    sesionActual.actividad_id
            );


        if (actividad) {

            mostrarActividadPrincipal(
                actividad
            );
        }


        if (
            sesionActual.estado_timer
            === "corriendo"
        ) {

            iniciarIntervaloVisual();

        } else {

            detenerIntervaloVisual();
        }


        dibujarTemporizador();

    } catch (error) {

        console.error(
            "Error cargando sesión:",
            error
        );
    }
}


// ==========================================
// PLAN DE HOY
// ==========================================

async function cargarPlanHoy() {

    try {

        const respuesta =
            await fetch(
                "/api/plan-hoy"
            );

        const datos =
            await respuesta.json();


        porcentajeProgreso.textContent =
            `${datos.porcentaje}%`;

        barraProgreso.style.width =
            `${datos.porcentaje}%`;


        cantidadCompletadas.textContent =
            datos.completadas;

        cantidadPendientes.textContent =
            datos.pendientes;

        cantidadOmitidas.textContent =
            datos.omitidas;


        planCompletadas.textContent =
            datos.completadas;

        planTotal.textContent =
            datos.total;


        listaActividades.innerHTML = "";


        if (
            datos.actividades.length
            === 0
        ) {

            listaActividades.innerHTML =
                `
                <div class="cargando-plan">
                    No hay actividades programadas para hoy.
                </div>
                `;

            return;
        }


        for (
            const actividad
            of datos.actividades
        ) {

            const fila =
                document.createElement(
                    "div"
                );

            fila.className =
                "actividad-plan "
                +
                actividad.estado_visual;


            let simbolo = "○";

            let textoBoton =
                "▶ Iniciar";

            let accionPrincipal =
                "iniciar";


            if (
                actividad.estado_visual
                === "en_progreso"
            ) {

                simbolo = "▶";
                textoBoton = "⏸ Activa";
                accionPrincipal = "activa";

            } else if (
                actividad.estado_visual
                === "pausada"
            ) {

                simbolo = "⏸";
                textoBoton = "▶ Continuar";
                accionPrincipal = "iniciar";

            } else if (
                actividad.estado_visual
                === "completada"
            ) {

                simbolo = "✓";
                textoBoton = "↶ Retomar";
                accionPrincipal = "retomar";

            } else if (
                actividad.estado_visual
                === "omitida"
            ) {

                simbolo = "✕";
                textoBoton = "↶ Retomar";
                accionPrincipal = "retomar";
            }


            

            fila.innerHTML = `
                <div class="plan-estado">
                    ${simbolo}
                </div>

                <div class="plan-info">

                    <div class="plan-nombre">

                        <span>
                            ${actividad.icono}
                        </span>

                        <span>
                            ${actividad.nombre}
                        </span>

                    </div>

                    <span class="plan-categoria">
                        ${actividad.categoria || ""}
                    </span>

                </div>

                <div class="plan-horario">
                    ${convertirHora(
                        actividad.hora_inicio
                    )}
                    -
                    ${convertirHora(
                        actividad.hora_fin
                    )}
                </div>

                <div class="plan-duracion">
                    ${formatearDuracionCorta(
                        actividad.duracion_objetivo
                    )}
                </div>

                <div class="plan-acciones">

                <button
                    class="btn-plan"
                    data-accion="${accionPrincipal}"
                >
                    ${textoBoton}
                </button>

                ${
                    actividad.estado_visual === "pendiente"
                    ||
                    actividad.estado_visual === "pausada"

                    ?

                    `
                    <button
                        class="btn-omitir"
                        data-accion="omitir"
                        title="Omitir actividad"
                    >
                        ✕
                    </button>
                    `

                    :

                    ""
                }

            </div>
            `;


            const botonPrincipal =
                fila.querySelector(
                    ".btn-plan"
                );


            botonPrincipal.addEventListener(
                "click",
                async () => {

                    const accion =
                        botonPrincipal.dataset.accion;


                    if (accion === "activa") {

                        return;
                    }


                    if (accion === "retomar") {

                        await fetch(
                            `/api/actividad/retomar/${actividad.id}`,
                            {
                                method: "POST"
                            }
                        );

                        await actualizarTodo();

                        return;
                    }


                    solicitarInicio(
                        actividad
                    );
                }
            );


            const botonOmitir =
                fila.querySelector(
                    ".btn-omitir"
                );


            if (botonOmitir) {

                botonOmitir.addEventListener(
                    "click",
                    async () => {

                        await omitirActividad(
                            actividad
                        );
                    }
                );
            }

            listaActividades.appendChild(
                fila
            );
        }

    } catch (error) {

        console.error(
            "Error cargando plan:",
            error
        );
    }
}


// ==========================================
// SOLICITAR INICIO
// ==========================================

async function solicitarInicio(
    actividad
) {

    // Si es la misma actividad pausada,
    // simplemente continuar.

    if (
        sesionActual
        &&
        sesionActual.actividad_id
            === actividad.id
        &&
        sesionActual.estado_timer
            !== "corriendo"
    ) {

        await iniciarActividad(
            actividad.id
        );

        return;
    }


    // Si esa misma actividad ya está activa,
    // no hacemos nada.

    if (
        sesionActual
        &&
        sesionActual.actividad_id
            === actividad.id
        &&
        sesionActual.estado_timer
            === "corriendo"
    ) {

        return;
    }


    // Hay otra actividad corriendo.

    if (
        sesionActual
        &&
        sesionActual.estado_timer
            === "corriendo"
    ) {

        actividadSeleccionada =
            actividad;

        modalActividadActual.textContent =
            sesionActual.icono
            +
            " "
            +
            sesionActual.nombre;

        modalTiempoActual.textContent =
            formatearTiempo(
                segundos
            );

        modalCambio.classList.add(
            "visible"
        );

        return;
    }


    // No hay nada corriendo.

    await iniciarActividad(
        actividad.id
    );
}


// ==========================================
// INICIAR
// ==========================================

async function iniciarActividad(
    actividadId
) {

    const respuesta =
        await fetch(
            `/api/sesion/iniciar/${actividadId}`,
            {
                method: "POST"
            }
        );


    const datos =
        await respuesta.json();


    // ==========================================
    // HAY OTRA ACTIVIDAD ACTIVA
    // ==========================================

    if (
        respuesta.status === 409
        &&
        datos.requiere_confirmacion
    ) {

        actividadSeleccionada = {
            id: actividadId
        };


        const activa =
            datos.actividad_activa;


        modalActividadActual.textContent =
            (activa.icono || "📌")
            +
            " "
            +
            activa.nombre;


        modalTiempoActual.textContent =
            "En progreso";


        modalCambio.classList.add(
            "visible"
        );


        return false;
    }


    // ==========================================
    // ERROR
    // ==========================================

    if (!respuesta.ok) {

        console.error(
            "No se pudo iniciar:",
            datos
        );

        return false;
    }


    await actualizarTodo();

    return true;
}


// ==========================================
// BOTÓN PRINCIPAL
// ==========================================

botonIniciar.addEventListener(
    "click",
    async () => {

        // SESIÓN CORRIENDO -> PAUSAR

        if (
            sesionActual
            &&
            sesionActual.estado_timer
                === "corriendo"
        ) {

            await fetch(
                "/api/sesion/pausar",
                {
                    method: "POST"
                }
            );

            await actualizarTodo();

            return;
        }


        // SESIÓN PAUSADA -> CONTINUAR

        if (sesionActual) {

            await iniciarActividad(
                sesionActual.actividad_id
            );

            return;
        }


        // ACTIVIDAD SEGÚN HORARIO

        if (actividadHorarioActual) {

            await iniciarActividad(
                actividadHorarioActual.id
            );

            return;
        }


        alert(
            "No hay una actividad seleccionada."
        );
    }
);


// ==========================================
// COMPLETAR
// ==========================================

botonCompletar.addEventListener(
    "click",
    async () => {

        if (!sesionActual) {

            alert(
                "Primero debes iniciar una actividad."
            );

            return;
        }


        await fetch(
            "/api/sesion/completar",
            {
                method: "POST"
            }
        );


        detenerIntervaloVisual();

        await actualizarTodo();
    }
);


// ==========================================
// MODAL
// ==========================================

cancelarCambio.addEventListener(
    "click",
    () => {

        actividadSeleccionada = null;

        modalCambio.classList.remove(
            "visible"
        );
    }
);


confirmarCambio.addEventListener(
    "click",
    async () => {

        if (!actividadSeleccionada) {
            return;
        }


        const nuevaId =
            actividadSeleccionada.id;


        // ======================================
        // PAUSAR CUALQUIER SESIÓN CORRIENDO
        // ======================================

        await fetch(
            "/api/sesion/pausar-activa",
            {
                method: "POST"
            }
        );


        actividadSeleccionada = null;


        modalCambio.classList.remove(
            "visible"
        );


        // ======================================
        // INICIAR LA NUEVA
        // ======================================

        await iniciarActividad(
            nuevaId
        );
    }
);


// ==========================================
// ACTUALIZAR TODO
// ==========================================

async function actualizarTodo() {

    await cargarHorarioActual();

    await cargarSesion();

    await cargarPlanHoy();
}


// ==========================================
// INICIO
// ==========================================

actualizarFecha();

actualizarTodo();


// Horario / plan

setInterval(
    async () => {

        await cargarHorarioActual();

        await cargarPlanHoy();

    },
    30000
);


// Sincronización real con SQLite

setInterval(
    cargarSesion,
    60000
);