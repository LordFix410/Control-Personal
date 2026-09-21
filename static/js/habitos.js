// ==========================================
// ELEMENTOS
// ==========================================

const listaHabitos =
    document.getElementById("listaHabitos");

const textoResumen =
    document.getElementById("textoResumen");

const porcentajeHabitos =
    document.getElementById("porcentajeHabitos");

const barraHabitos =
    document.getElementById("barraHabitos");

const fechaHabitos =
    document.getElementById("fechaHabitos");


const nuevoHabito =
    document.getElementById("nuevoHabito");


// MODAL

const modalHabito =
    document.getElementById("modalHabito");

const tituloModalHabito =
    document.getElementById("tituloModalHabito");

const cerrarModalHabito =
    document.getElementById("cerrarModalHabito");

const cancelarModalHabito =
    document.getElementById("cancelarModalHabito");

const guardarHabito =
    document.getElementById("guardarHabito");


const inputNombreHabito =
    document.getElementById("inputNombreHabito");

const inputIconoHabito =
    document.getElementById("inputIconoHabito");

const inputObjetivoHabito =
    document.getElementById("inputObjetivoHabito");

const mensajeHabito =
    document.getElementById("mensajeHabito");


// ELIMINAR

const modalEliminarHabito =
    document.getElementById(
        "modalEliminarHabito"
    );

const nombreEliminarHabito =
    document.getElementById(
        "nombreEliminarHabito"
    );

const cancelarEliminarHabito =
    document.getElementById(
        "cancelarEliminarHabito"
    );

const confirmarEliminarHabito =
    document.getElementById(
        "confirmarEliminarHabito"
    );


// ==========================================
// VARIABLES
// ==========================================

let habitos = [];

let habitoEditando = null;

let habitoEliminando = null;


// ==========================================
// FECHA
// ==========================================

function mostrarFecha() {

    const ahora =
        new Date();


    fechaHabitos.textContent =
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
// CARGAR
// ==========================================

async function cargarHabitos() {

    try {

        const respuesta =
            await fetch("/api/habitos");


        const datos =
            await respuesta.json();


        habitos =
            datos.habitos;


        textoResumen.textContent =
            `${datos.completados} de `
            +
            `${datos.total} hábitos completados`;


        porcentajeHabitos.textContent =
            `${datos.porcentaje}%`;


        barraHabitos.style.width =
            `${datos.porcentaje}%`;


        renderizarHabitos();


    } catch (error) {

        console.error(
            "Error cargando hábitos:",
            error
        );


        listaHabitos.innerHTML = `
            <div class="habitos-vacio">
                No se pudieron cargar los hábitos.
            </div>
        `;
    }
}


// ==========================================
// RENDER
// ==========================================

function renderizarHabitos() {

    listaHabitos.innerHTML = "";


    if (habitos.length === 0) {

        listaHabitos.innerHTML = `
            <div class="habitos-vacio">

                Todavía no tienes hábitos.

                <br><br>

                Usa
                <strong>+ Nuevo hábito</strong>
                para crear el primero.

            </div>
        `;

        return;
    }


    habitos.forEach(
        habito => {

            const tarjeta =
                document.createElement(
                    "article"
                );


            tarjeta.className =
                "habito-card";


            if (!habito.activo) {

                tarjeta.classList.add(
                    "desactivado"
                );
            }


            if (
                habito.completado
                &&
                habito.activo
            ) {

                tarjeta.classList.add(
                    "completado"
                );
            }


            const cantidad =
                Number(
                    habito.cantidad || 0
                );


            const objetivo =
                Number(
                    habito.objetivo || 1
                );


            const porcentaje =
                Math.round(
                    cantidad
                    /
                    objetivo
                    *
                    100
                );


            const porcentajeVisual =
                Math.min(
                    porcentaje,
                    100
                );


            let estadoTexto =
                `${porcentaje}%`;


            if (habito.completado) {

                estadoTexto =
                    "✓ Completado";
            }


            tarjeta.innerHTML = `

                <div class="habito-cabecera">

                    <div class="habito-identidad">

                        <div class="habito-icono">
                            ${habito.icono || "⭐"}
                        </div>


                        <div>

                            <div class="habito-nombre">
                                ${habito.nombre}
                            </div>

                            <div class="habito-meta">
                                Objetivo diario:
                                ${objetivo}
                            </div>

                        </div>

                    </div>


                    <div class="habito-menu">

                        <label
                            class="switch-habito"
                            title="${
                                habito.activo
                                ? "Desactivar"
                                : "Activar"
                            }"
                        >

                            <input
                                type="checkbox"
                                class="estado-switch"

                                ${
                                    habito.activo
                                    ? "checked"
                                    : ""
                                }
                            >

                            <span
                                class="switch-habito-slider"
                            ></span>

                        </label>


                        <button
                            class="btn-editar-habito"
                            title="Editar"
                        >
                            ✎
                        </button>


                        <button
                            class="btn-borrar-habito"
                            title="Eliminar"
                        >
                            🗑
                        </button>

                    </div>

                </div>


                <div class="habito-progreso-info">

                    <span>
                        Progreso de hoy
                    </span>

                    <strong>
                        ${cantidad} / ${objetivo}
                    </strong>

                </div>


                <div class="habito-barra">

                    <div
                        class="habito-barra-progreso"
                        style="
                            width:
                            ${porcentajeVisual}%
                        "
                    ></div>

                </div>


                <div class="habito-controles">

                    <div class="control-cantidad">

                        <button
                            class="btn-cantidad restar"
                            ${
                                !habito.activo
                                ? "disabled"
                                : ""
                            }
                        >
                            −
                        </button>


                        <strong class="cantidad-actual">
                            ${cantidad}
                        </strong>


                        <button
                            class="btn-cantidad sumar"
                            ${
                                !habito.activo
                                ? "disabled"
                                : ""
                            }
                        >
                            +
                        </button>

                    </div>


                    <span
                        class="estado-habito
                        ${
                            habito.completado
                            ? "hecho"
                            : ""
                        }"
                    >
                        ${estadoTexto}
                    </span>

                </div>
            `;


            // SUMAR

            tarjeta
                .querySelector(".sumar")
                .addEventListener(
                    "click",
                    async () => {

                        await modificarCantidad(
                            habito.id,
                            "sumar"
                        );
                    }
                );


            // RESTAR

            tarjeta
                .querySelector(".restar")
                .addEventListener(
                    "click",
                    async () => {

                        await modificarCantidad(
                            habito.id,
                            "restar"
                        );
                    }
                );


            // EDITAR

            tarjeta
                .querySelector(
                    ".btn-editar-habito"
                )
                .addEventListener(
                    "click",
                    () => {

                        abrirEditarHabito(
                            habito
                        );
                    }
                );


            // ELIMINAR

            tarjeta
                .querySelector(
                    ".btn-borrar-habito"
                )
                .addEventListener(
                    "click",
                    () => {

                        abrirEliminarHabito(
                            habito
                        );
                    }
                );


            // ACTIVAR / DESACTIVAR

            const switchEstado =
                tarjeta.querySelector(
                    ".estado-switch"
                );


            switchEstado.addEventListener(
                "change",
                async () => {

                    await cambiarEstadoHabito(
                        habito,
                        switchEstado
                    );
                }
            );


            listaHabitos.appendChild(
                tarjeta
            );
        }
    );
}


// ==========================================
// SUMAR / RESTAR
// ==========================================

async function modificarCantidad(
    habitoId,
    accion
) {

    try {

        const respuesta =
            await fetch(
                `/api/habitos/${habitoId}/${accion}`,
                {
                    method: "POST"
                }
            );


        const datos =
            await respuesta.json();


        if (!respuesta.ok) {

            alert(
                datos.mensaje
                ||
                "No se pudo registrar."
            );

            return;
        }


        await cargarHabitos();


    } catch (error) {

        console.error(
            "Error modificando hábito:",
            error
        );
    }
}


// ==========================================
// NUEVO
// ==========================================

nuevoHabito.addEventListener(
    "click",
    () => {

        habitoEditando = null;


        tituloModalHabito.textContent =
            "Nuevo hábito";


        inputNombreHabito.value =
            "";

        inputIconoHabito.value =
            "⭐";

        inputObjetivoHabito.value =
            "1";

        mensajeHabito.textContent =
            "";


        modalHabito.classList.add(
            "visible"
        );


        setTimeout(
            () =>
                inputNombreHabito.focus(),
            50
        );
    }
);


// ==========================================
// EDITAR
// ==========================================

function abrirEditarHabito(
    habito
) {

    habitoEditando =
        habito;


    tituloModalHabito.textContent =
        "Editar hábito";


    inputNombreHabito.value =
        habito.nombre;

    inputIconoHabito.value =
        habito.icono || "⭐";

    inputObjetivoHabito.value =
        habito.objetivo;


    mensajeHabito.textContent =
        "";


    modalHabito.classList.add(
        "visible"
    );
}


// ==========================================
// GUARDAR
// ==========================================

guardarHabito.addEventListener(
    "click",
    async () => {

        mensajeHabito.textContent =
            "";


        const nombre =
            inputNombreHabito
                .value
                .trim();


        const icono =
            inputIconoHabito
                .value
                .trim()
            || "⭐";


        const objetivo =
            Number(
                inputObjetivoHabito.value
            );


        if (!nombre) {

            mensajeHabito.textContent =
                "Escribe el nombre del hábito.";

            inputNombreHabito.focus();

            return;
        }


        if (
            !Number.isInteger(objetivo)
            ||
            objetivo < 1
        ) {

            mensajeHabito.textContent =
                "El objetivo debe ser un número entero mayor que 0.";

            return;
        }


        const cuerpo = {
            nombre,
            icono,
            objetivo
        };


        let url =
            "/api/habitos";

        let metodo =
            "POST";


        if (habitoEditando) {

            url =
                `/api/habitos/${habitoEditando.id}`;

            metodo =
                "PUT";
        }


        guardarHabito.disabled =
            true;

        guardarHabito.textContent =
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

                mensajeHabito.textContent =
                    datos.mensaje
                    ||
                    "No se pudo guardar.";

                return;
            }


            cerrarHabito();

            await cargarHabitos();


        } catch (error) {

            console.error(
                "Error guardando hábito:",
                error
            );


            mensajeHabito.textContent =
                "Error de conexión.";
        }

        finally {

            guardarHabito.disabled =
                false;

            guardarHabito.textContent =
                "Guardar hábito";
        }
    }
);


// ==========================================
// ACTIVAR / DESACTIVAR
// ==========================================

async function cambiarEstadoHabito(
    habito,
    switchElemento
) {

    const activo =
        switchElemento.checked;


    try {

        const respuesta =
            await fetch(
                `/api/habitos/${habito.id}/estado`,
                {
                    method: "PATCH",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body:
                        JSON.stringify({
                            activo
                        })
                }
            );


        const datos =
            await respuesta.json();


        if (!respuesta.ok) {

            switchElemento.checked =
                !activo;


            alert(
                datos.mensaje
                ||
                "No se pudo cambiar el estado."
            );

            return;
        }


        await cargarHabitos();


    } catch (error) {

        switchElemento.checked =
            !activo;


        console.error(
            "Error cambiando estado:",
            error
        );
    }
}


// ==========================================
// ELIMINAR
// ==========================================

function abrirEliminarHabito(
    habito
) {

    habitoEliminando =
        habito;


    nombreEliminarHabito.textContent =
        habito.nombre;


    modalEliminarHabito.classList.add(
        "visible"
    );
}


cancelarEliminarHabito.addEventListener(
    "click",
    () => {

        cerrarEliminar();
    }
);


confirmarEliminarHabito.addEventListener(
    "click",
    async () => {

        if (!habitoEliminando) {
            return;
        }


        confirmarEliminarHabito.disabled =
            true;

        confirmarEliminarHabito.textContent =
            "Eliminando...";


        try {

            const respuesta =
                await fetch(
                    `/api/habitos/${habitoEliminando.id}`,
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


            cerrarEliminar();

            await cargarHabitos();


        } catch (error) {

            console.error(
                "Error eliminando hábito:",
                error
            );

        } finally {

            confirmarEliminarHabito.disabled =
                false;

            confirmarEliminarHabito.textContent =
                "Eliminar";
        }
    }
);


// ==========================================
// CERRAR MODALES
// ==========================================

function cerrarHabito() {

    modalHabito.classList.remove(
        "visible"
    );

    habitoEditando = null;

    mensajeHabito.textContent = "";
}


function cerrarEliminar() {

    modalEliminarHabito.classList.remove(
        "visible"
    );

    habitoEliminando = null;
}


cerrarModalHabito.addEventListener(
    "click",
    cerrarHabito
);


cancelarModalHabito.addEventListener(
    "click",
    cerrarHabito
);


modalHabito.addEventListener(
    "click",
    evento => {

        if (
            evento.target
            === modalHabito
        ) {

            cerrarHabito();
        }
    }
);


modalEliminarHabito.addEventListener(
    "click",
    evento => {

        if (
            evento.target
            === modalEliminarHabito
        ) {

            cerrarEliminar();
        }
    }
);


// ESC

document.addEventListener(
    "keydown",
    evento => {

        if (evento.key !== "Escape") {
            return;
        }


        if (
            modalHabito.classList
                .contains("visible")
        ) {

            cerrarHabito();
        }


        if (
            modalEliminarHabito.classList
                .contains("visible")
        ) {

            cerrarEliminar();
        }
    }
);


// ==========================================
// INICIO
// ==========================================

mostrarFecha();

cargarHabitos();