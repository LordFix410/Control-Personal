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

const siguienteNombre =
    document.getElementById("siguienteNombre");

const siguienteHora =
    document.getElementById("siguienteHora");


let actividadActual = null;

let sesionActual = null;

let segundos = 0;

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

actualizarFecha();


// ==========================================
// CONVERTIR HORA
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

    horas = horas % 12;

    if (horas === 0) {
        horas = 12;
    }

    return `${horas}:${minutos} ${periodo}`;
}


// ==========================================
// TIMER
// ==========================================

function dibujarTemporizador() {

    const horas =
        Math.floor(segundos / 3600);

    const minutos =
        Math.floor(
            (segundos % 3600) / 60
        );

    const segundosRestantes =
        segundos % 60;

    temporizador.textContent =
        String(horas).padStart(2, "0")
        + ":"
        + String(minutos).padStart(2, "0")
        + ":"
        + String(segundosRestantes)
            .padStart(2, "0");
}


function detenerIntervaloVisual() {

    if (intervaloVisual) {

        clearInterval(intervaloVisual);

        intervaloVisual = null;
    }
}


function iniciarIntervaloVisual() {

    detenerIntervaloVisual();

    intervaloVisual = setInterval(
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

        actividadActual =
            datos.actual;


        if (datos.actual) {

            actividadIcono.textContent =
                datos.actual.icono;

            actividadNombre.textContent =
                datos.actual.nombre;

            actividadCategoria.textContent =
                datos.actual.categoria;

            actividadHorario.textContent =
                convertirHora(
                    datos.actual.hora_inicio
                )
                +
                " - "
                +
                convertirHora(
                    datos.actual.hora_fin
                );

        } else {

            actividadIcono.textContent =
                "😎";

            actividadNombre.textContent =
                "Tiempo libre";

            actividadCategoria.textContent =
                "No hay actividad programada";

            actividadHorario.textContent =
                "";
        }


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
// SESIÓN
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

            segundos = 0;

            detenerIntervaloVisual();

            dibujarTemporizador();

            botonIniciar.textContent =
                "▶ Iniciar";

            return;
        }


        segundos =
            sesionActual.segundos_actuales || 0;

        dibujarTemporizador();


        if (
            sesionActual.estado_timer
            === "corriendo"
        ) {

            botonIniciar.textContent =
                "⏸ Pausar";

            iniciarIntervaloVisual();

        } else {

            botonIniciar.textContent =
                "▶ Continuar";

            detenerIntervaloVisual();
        }

    } catch (error) {

        console.error(
            "Error cargando sesión:",
            error
        );
    }
}


// ==========================================
// INICIAR / PAUSAR
// ==========================================

botonIniciar.addEventListener(
    "click",
    async () => {

        // Si existe sesión corriendo:
        // PAUSAMOS

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

            await cargarSesion();

            return;
        }


        // Si hay una sesión pausada:
        // REANUDAMOS ESA MISMA

        if (sesionActual) {

            await fetch(
                `/api/sesion/iniciar/${sesionActual.actividad_id}`,
                {
                    method: "POST"
                }
            );

            await cargarSesion();

            return;
        }


        // Nueva sesión

        if (!actividadActual) {

            alert(
                "No hay una actividad programada en este momento."
            );

            return;
        }


        await fetch(
            `/api/sesion/iniciar/${actividadActual.id}`,
            {
                method: "POST"
            }
        );

        await cargarSesion();
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
                "Primero debes iniciar la actividad."
            );

            return;
        }


        const respuesta =
            await fetch(
                "/api/sesion/completar",
                {
                    method: "POST"
                }
            );


        if (!respuesta.ok) {

            alert(
                "No se pudo completar la actividad."
            );

            return;
        }


        detenerIntervaloVisual();

        await cargarSesion();

        await cargarHorarioActual();
    }
);


// ==========================================
// INICIO
// ==========================================

async function iniciarAplicacion() {

    await cargarHorarioActual();

    await cargarSesion();
}


iniciarAplicacion();


// Revisamos el horario cada 30 segundos.

setInterval(
    cargarHorarioActual,
    30000
);


// Sincronizamos el timer con SQLite
// cada minuto.

setInterval(
    cargarSesion,
    60000
);