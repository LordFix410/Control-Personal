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