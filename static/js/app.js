const fecha = document.getElementById("fecha");

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


let segundos = 0;
let ejecutando = false;
let intervalo = null;


const temporizador =
    document.getElementById("temporizador");

const botonIniciar =
    document.getElementById("iniciar");


function actualizarTemporizador() {

    const horas =
        Math.floor(segundos / 3600);

    const minutos =
        Math.floor((segundos % 3600) / 60);

    const segundosRestantes =
        segundos % 60;


    temporizador.textContent =
        String(horas).padStart(2, "0")
        + ":" +
        String(minutos).padStart(2, "0")
        + ":" +
        String(segundosRestantes).padStart(2, "0");
}


botonIniciar.addEventListener(
    "click",
    () => {

        if (!ejecutando) {

            ejecutando = true;

            botonIniciar.textContent =
                "⏸ Pausar";


            intervalo = setInterval(
                () => {

                    segundos++;

                    actualizarTemporizador();

                },
                1000
            );

        } else {

            ejecutando = false;

            botonIniciar.textContent =
                "▶ Continuar";

            clearInterval(intervalo);
        }
    }
);

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


async function cargarHorarioActual() {

    try {

        const respuesta =
            await fetch("/api/hoy");

        const datos =
            await respuesta.json();


        // ACTIVIDAD ACTUAL

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

            actividadIcono.textContent = "😎";

            actividadNombre.textContent =
                "Tiempo libre";

            actividadCategoria.textContent =
                "No hay actividad programada";

            actividadHorario.textContent = "";

        }


        // SIGUIENTE ACTIVIDAD

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

            siguienteHora.textContent = "";

        }

    } catch (error) {

        console.error(
            "Error cargando horario:",
            error
        );
    }
}


cargarHorarioActual();


// Revisamos cada 30 segundos
setInterval(
    cargarHorarioActual,
    30000
);