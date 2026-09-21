// ==========================================
// ELEMENTOS
// ==========================================

const botonesDias =
    document.querySelectorAll(".dia-btn");

const listaHorario =
    document.getElementById("listaHorario");

const tituloDia =
    document.getElementById("tituloDia");

const cantidadDia =
    document.getElementById("cantidadDia");

const tiempoDia =
    document.getElementById("tiempoDia");


const nuevaActividad =
    document.getElementById("nuevaActividad");


// MODAL

const modalActividad =
    document.getElementById("modalActividad");

const tituloModal =
    document.getElementById("tituloModal");

const cerrarModal =
    document.getElementById("cerrarModal");

const cancelarModal =
    document.getElementById("cancelarModal");

const guardarActividad =
    document.getElementById("guardarActividad");


const inputNombre =
    document.getElementById("inputNombre");

const inputCategoria =
    document.getElementById("inputCategoria");

const inputIcono =
    document.getElementById("inputIcono");

const inputInicio =
    document.getElementById("inputInicio");

const inputFin =
    document.getElementById("inputFin");


const contenedorDiasModal =
    document.getElementById(
        "contenedorDiasModal"
    );

const checksDias =
    document.querySelectorAll(
        ".dias-modal input"
    );

const mensajeFormulario =
    document.getElementById(
        "mensajeFormulario"
    );


// ELIMINAR

const modalEliminar =
    document.getElementById("modalEliminar");

const nombreEliminar =
    document.getElementById("nombreEliminar");

const cancelarEliminar =
    document.getElementById("cancelarEliminar");

const confirmarEliminar =
    document.getElementById("confirmarEliminar");


// ==========================================
// VARIABLES
// ==========================================

const nombresDias = [
    "Lunes",
    "Martes",
    "Miércoles",
    "Jueves",
    "Viernes",
    "Sábado",
    "Domingo"
];


let actividades = [];

let diaSeleccionado =
    obtenerDiaActual();

let actividadEditando = null;

let actividadEliminando = null;


// ==========================================
// DÍA ACTUAL
// ==========================================

function obtenerDiaActual() {

    const diaJS =
        new Date().getDay();

    // JS:
    // domingo = 0
    // lunes = 1
    //
    // Python:
    // lunes = 0
    // domingo = 6

    return (
        diaJS === 0
        ? 6
        : diaJS - 1
    );
}


// ==========================================
// HORAS
// ==========================================

function convertirHora(hora) {

    if (!hora) {
        return "--";
    }


    const partes =
        hora.split(":");

    let horas =
        Number(partes[0]);

    const minutos =
        partes[1];

    const periodo =
        horas >= 12
        ? "PM"
        : "AM";


    horas %= 12;

    if (horas === 0) {
        horas = 12;
    }


    return (
        `${horas}:${minutos} ${periodo}`
    );
}


function calcularMinutos(
    inicio,
    fin
) {

    const i =
        inicio.split(":");

    const f =
        fin.split(":");


    const minutosInicio =
        Number(i[0]) * 60
        +
        Number(i[1]);


    const minutosFin =
        Number(f[0]) * 60
        +
        Number(f[1]);


    return Math.max(
        0,
        minutosFin - minutosInicio
    );
}


function formatearMinutos(minutos) {

    if (minutos < 60) {

        return `${minutos} min`;
    }


    const horas =
        Math.floor(
            minutos / 60
        );

    const resto =
        minutos % 60;


    if (resto === 0) {

        return `${horas} h`;
    }


    return (
        `${horas} h ${resto} min`
    );
}


// ==========================================
// CARGAR
// ==========================================

async function cargarHorario() {

    try {

        const respuesta =
            await fetch(
                "/api/horario"
            );


        const datos =
            await respuesta.json();


        actividades =
            datos.actividades;


        renderizarHorario();


    } catch (error) {

        console.error(
            "Error cargando horario:",
            error
        );


        listaHorario.innerHTML = `
            <div class="horario-vacio">
                No se pudo cargar el horario.
            </div>
        `;
    }
}


// ==========================================
// RENDER
// ==========================================

function renderizarHorario() {

    botonesDias.forEach(
        boton => {

            boton.classList.toggle(
                "activo",
                Number(
                    boton.dataset.dia
                )
                ===
                diaSeleccionado
            );
        }
    );


    tituloDia.textContent =
        nombresDias[diaSeleccionado];


    const actividadesDia =
        actividades
            .filter(
                actividad =>
                    actividad.dia_semana
                    === diaSeleccionado
            )
            .sort(
                (a, b) =>
                    a.hora_inicio.localeCompare(
                        b.hora_inicio
                    )
            );


    cantidadDia.textContent =
        `${actividadesDia.length} ${
            actividadesDia.length === 1
            ? "actividad"
            : "actividades"
        }`;


    let minutosTotales = 0;


    actividadesDia.forEach(
        actividad => {

            if (actividad.activo) {

                minutosTotales +=
                    calcularMinutos(
                        actividad.hora_inicio,
                        actividad.hora_fin
                    );
            }
        }
    );


    tiempoDia.textContent =
        `${formatearMinutos(
            minutosTotales
        )} programadas`;


    listaHorario.innerHTML = "";


    if (actividadesDia.length === 0) {

        listaHorario.innerHTML = `
            <div class="horario-vacio">

                No hay actividades programadas
                para ${nombresDias[
                    diaSeleccionado
                ].toLowerCase()}.

                <br><br>

                Usa <strong>
                    + Nueva actividad
                </strong>
                para comenzar.

            </div>
        `;

        return;
    }


    actividadesDia.forEach(
        actividad => {

            const item =
                document.createElement(
                    "div"
                );


            item.className =
                "horario-item";


            if (!actividad.activo) {

                item.classList.add(
                    "desactivada"
                );
            }


            item.innerHTML = `

                <div class="horario-hora">
                    ${convertirHora(
                        actividad.hora_inicio
                    )}
                </div>


                <div class="horario-icono">
                    ${actividad.icono || "📌"}
                </div>


                <div class="horario-info">

                    <div class="horario-nombre">
                        ${actividad.nombre}
                    </div>

                    <div class="horario-categoria">
                        ${
                            actividad.categoria
                            || "Sin categoría"
                        }
                    </div>

                </div>


                <div class="horario-rango">

                    ${convertirHora(
                        actividad.hora_inicio
                    )}

                    —

                    ${convertirHora(
                        actividad.hora_fin
                    )}

                </div>


                <label class="switch">

                    <input
                        type="checkbox"
                        class="switch-actividad"

                        ${
                            actividad.activo
                            ? "checked"
                            : ""
                        }
                    >

                    <span
                        class="switch-slider"
                    ></span>

                </label>


                <div class="horario-acciones">

                    <button
                        class="btn-editar"
                        title="Editar"
                    >
                        ✎
                    </button>

                    <button
                        class="btn-eliminar"
                        title="Eliminar"
                    >
                        🗑
                    </button>

                </div>
            `;


            const switchActividad =
                item.querySelector(
                    ".switch-actividad"
                );


            switchActividad.addEventListener(
                "change",
                async () => {

                    await cambiarEstado(
                        actividad,
                        switchActividad
                    );
                }
            );


            item.querySelector(
                ".btn-editar"
            ).addEventListener(
                "click",
                () => {

                    abrirEditar(
                        actividad
                    );
                }
            );


            item.querySelector(
                ".btn-eliminar"
            ).addEventListener(
                "click",
                () => {

                    abrirEliminar(
                        actividad
                    );
                }
            );


            listaHorario.appendChild(
                item
            );
        }
    );
}


// ==========================================
// CAMBIAR DÍA
// ==========================================

botonesDias.forEach(
    boton => {

        boton.addEventListener(
            "click",
            () => {

                diaSeleccionado =
                    Number(
                        boton.dataset.dia
                    );


                renderizarHorario();
            }
        );
    }
);


// ==========================================
// NUEVA ACTIVIDAD
// ==========================================

nuevaActividad.addEventListener(
    "click",
    () => {

        actividadEditando = null;


        tituloModal.textContent =
            "Nueva actividad";


        inputNombre.value = "";
        inputCategoria.value = "";
        inputIcono.value = "📌";

        inputInicio.value = "";
        inputFin.value = "";


        mensajeFormulario.textContent =
            "";


        contenedorDiasModal.style.display =
            "";


        checksDias.forEach(
            check => {

                check.checked =
                    Number(check.value)
                    === diaSeleccionado;
            }
        );


        modalActividad.classList.add(
            "visible"
        );


        setTimeout(
            () => inputNombre.focus(),
            50
        );
    }
);


// ==========================================
// EDITAR
// ==========================================

function abrirEditar(actividad) {

    actividadEditando =
        actividad;


    tituloModal.textContent =
        "Editar actividad";


    inputNombre.value =
        actividad.nombre;

    inputCategoria.value =
        actividad.categoria || "";

    inputIcono.value =
        actividad.icono || "📌";

    inputInicio.value =
        actividad.hora_inicio;

    inputFin.value =
        actividad.hora_fin;


    mensajeFormulario.textContent =
        "";


    // La edición modifica solamente
    // la actividad de este día.

    contenedorDiasModal.style.display =
        "none";


    modalActividad.classList.add(
        "visible"
    );


    setTimeout(
        () => inputNombre.focus(),
        50
    );
}


// ==========================================
// CERRAR MODAL
// ==========================================

function cerrarModalActividad() {

    modalActividad.classList.remove(
        "visible"
    );

    actividadEditando = null;

    mensajeFormulario.textContent = "";
}


cerrarModal.addEventListener(
    "click",
    cerrarModalActividad
);


cancelarModal.addEventListener(
    "click",
    cerrarModalActividad
);


// ==========================================
// GUARDAR
// ==========================================

guardarActividad.addEventListener(
    "click",
    async () => {

        mensajeFormulario.textContent =
            "";


        const nombre =
            inputNombre.value.trim();

        const categoria =
            inputCategoria.value.trim();

        const icono =
            inputIcono.value.trim()
            || "📌";

        const horaInicio =
            inputInicio.value;

        const horaFin =
            inputFin.value;


        if (!nombre) {

            mensajeFormulario.textContent =
                "Escribe el nombre de la actividad.";

            inputNombre.focus();

            return;
        }


        if (!horaInicio || !horaFin) {

            mensajeFormulario.textContent =
                "Selecciona la hora de inicio y final.";

            return;
        }


        if (horaFin <= horaInicio) {

            mensajeFormulario.textContent =
                "La hora final debe ser posterior a la inicial.";

            return;
        }


        let url;
        let metodo;
        let cuerpo;


        // ======================================
        // EDITAR
        // ======================================

        if (actividadEditando) {

            url =
                `/api/horario/${actividadEditando.id}`;

            metodo =
                "PUT";

            cuerpo = {
                nombre,
                categoria,
                icono,

                hora_inicio:
                    horaInicio,

                hora_fin:
                    horaFin
            };


        // ======================================
        // CREAR
        // ======================================

        } else {

            const dias =
                Array.from(
                    checksDias
                )
                .filter(
                    check =>
                        check.checked
                )
                .map(
                    check =>
                        Number(
                            check.value
                        )
                );


            if (dias.length === 0) {

                mensajeFormulario.textContent =
                    "Selecciona al menos un día.";

                return;
            }


            url =
                "/api/horario";

            metodo =
                "POST";

            cuerpo = {
                nombre,
                categoria,
                icono,

                hora_inicio:
                    horaInicio,

                hora_fin:
                    horaFin,

                dias
            };
        }


        guardarActividad.disabled =
            true;

        guardarActividad.textContent =
            "Guardando...";


        try {

            const respuesta =
                await fetch(
                    url,
                    {
                        method: metodo,

                        headers: {
                            "Content-Type":
                                "application/json"
                        },

                        body:
                            JSON.stringify(
                                cuerpo
                            )
                    }
                );


            const datos =
                await respuesta.json();


            if (!respuesta.ok) {

                if (
                    datos.conflictos
                    &&
                    datos.conflictos.length
                ) {

                    mensajeFormulario.textContent =
                        datos.conflictos
                            .map(
                                conflicto =>
                                    `${conflicto.dia}: `
                                    +
                                    `${conflicto.actividad} `
                                    +
                                    `(${conflicto.hora_inicio}`
                                    +
                                    ` - `
                                    +
                                    `${conflicto.hora_fin})`
                            )
                            .join(" · ");

                } else {

                    mensajeFormulario.textContent =
                        datos.mensaje
                        ||
                        "No se pudo guardar.";
                }


                return;
            }


            cerrarModalActividad();

            await cargarHorario();


        } catch (error) {

            console.error(
                "Error guardando:",
                error
            );


            mensajeFormulario.textContent =
                "Error de conexión.";
        }

        finally {

            guardarActividad.disabled =
                false;

            guardarActividad.textContent =
                "Guardar actividad";
        }
    }
);


// ==========================================
// ACTIVAR / DESACTIVAR
// ==========================================

async function cambiarEstado(
    actividad,
    switchElemento
) {

    const nuevoEstado =
        switchElemento.checked;


    try {

        const respuesta =
            await fetch(
                `/api/horario/${actividad.id}/estado`,
                {
                    method: "PATCH",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body:
                        JSON.stringify({
                            activo:
                                nuevoEstado
                        })
                }
            );


        const datos =
            await respuesta.json();


        if (!respuesta.ok) {

            switchElemento.checked =
                !nuevoEstado;


            alert(
                datos.mensaje
                ||
                "No se pudo cambiar el estado."
            );

            return;
        }


        await cargarHorario();


    } catch (error) {

        switchElemento.checked =
            !nuevoEstado;


        console.error(
            "Error cambiando estado:",
            error
        );
    }
}


// ==========================================
// ELIMINAR
// ==========================================

function abrirEliminar(
    actividad
) {

    actividadEliminando =
        actividad;


    nombreEliminar.textContent =
        actividad.nombre;


    modalEliminar.classList.add(
        "visible"
    );
}


cancelarEliminar.addEventListener(
    "click",
    () => {

        actividadEliminando = null;

        modalEliminar.classList.remove(
            "visible"
        );
    }
);


confirmarEliminar.addEventListener(
    "click",
    async () => {

        if (!actividadEliminando) {
            return;
        }


        confirmarEliminar.disabled =
            true;

        confirmarEliminar.textContent =
            "Eliminando...";


        try {

            const respuesta =
                await fetch(
                    `/api/horario/${actividadEliminando.id}`,
                    {
                        method: "DELETE"
                    }
                );


            const datos =
                await respuesta.json();


            if (!respuesta.ok) {

                alert(
                    datos.mensaje
                    ||
                    "No se pudo eliminar."
                );

                return;
            }


            actividadEliminando = null;


            modalEliminar.classList.remove(
                "visible"
            );


            await cargarHorario();


        } catch (error) {

            console.error(
                "Error eliminando:",
                error
            );

        }

        finally {

            confirmarEliminar.disabled =
                false;

            confirmarEliminar.textContent =
                "Eliminar";
        }
    }
);


// ==========================================
// CERRAR AL TOCAR FONDO
// ==========================================

modalActividad.addEventListener(
    "click",
    evento => {

        if (
            evento.target
            === modalActividad
        ) {

            cerrarModalActividad();
        }
    }
);


modalEliminar.addEventListener(
    "click",
    evento => {

        if (
            evento.target
            === modalEliminar
        ) {

            actividadEliminando = null;

            modalEliminar.classList.remove(
                "visible"
            );
        }
    }
);


// ==========================================
// ESC
// ==========================================

document.addEventListener(
    "keydown",
    evento => {

        if (evento.key !== "Escape") {
            return;
        }


        if (
            modalActividad.classList
                .contains("visible")
        ) {

            cerrarModalActividad();
        }


        if (
            modalEliminar.classList
                .contains("visible")
        ) {

            actividadEliminando = null;

            modalEliminar.classList.remove(
                "visible"
            );
        }
    }
);


// ==========================================
// INICIO
// ==========================================

cargarHorario();