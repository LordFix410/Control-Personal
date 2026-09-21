// ==========================================
// ELEMENTOS
// ==========================================

const listaMetas =
    document.getElementById("listaMetas");

const metasActivas =
    document.getElementById("metasActivas");

const metasCompletadas =
    document.getElementById("metasCompletadas");

const metasTotal =
    document.getElementById("metasTotal");

const nuevaMeta =
    document.getElementById("nuevaMeta");

const filtros =
    document.querySelectorAll(".filtro-meta");


// MODAL

const modalMeta =
    document.getElementById("modalMeta");

const tituloModalMeta =
    document.getElementById("tituloModalMeta");

const cerrarModalMeta =
    document.getElementById("cerrarModalMeta");

const cancelarModalMeta =
    document.getElementById("cancelarModalMeta");

const guardarMeta =
    document.getElementById("guardarMeta");

const inputNombreMeta =
    document.getElementById("inputNombreMeta");

const inputDescripcionMeta =
    document.getElementById("inputDescripcionMeta");

const inputIconoMeta =
    document.getElementById("inputIconoMeta");

const inputCategoriaMeta =
    document.getElementById("inputCategoriaMeta");

const inputFechaMeta =
    document.getElementById("inputFechaMeta");

const mensajeMeta =
    document.getElementById("mensajeMeta");


// ELIMINAR

const modalEliminarMeta =
    document.getElementById("modalEliminarMeta");

const nombreEliminarMeta =
    document.getElementById("nombreEliminarMeta");

const cancelarEliminarMeta =
    document.getElementById("cancelarEliminarMeta");

const confirmarEliminarMeta =
    document.getElementById("confirmarEliminarMeta");


// ==========================================
// VARIABLES
// ==========================================

let metas = [];

let filtroActual = "activas";

let metaEditando = null;

let metaEliminando = null;


// ==========================================
// CARGAR
// ==========================================

async function cargarMetas() {

    try {

        const respuesta =
            await fetch("/api/metas");

        const datos =
            await respuesta.json();


        if (!respuesta.ok) {

            throw new Error(
                "No se pudieron cargar las metas."
            );
        }


        metas = datos.metas;


        metasActivas.textContent =
            datos.activas;

        metasCompletadas.textContent =
            datos.completadas;

        metasTotal.textContent =
            datos.total;


        renderizarMetas();


    } catch (error) {

        console.error(
            "Error cargando metas:",
            error
        );


        listaMetas.innerHTML = `
            <div class="metas-vacio">
                No se pudieron cargar las metas.
            </div>
        `;
    }
}


// ==========================================
// FILTROS
// ==========================================

filtros.forEach(
    boton => {

        boton.addEventListener(
            "click",
            () => {

                filtros.forEach(
                    item =>
                        item.classList.remove(
                            "activo"
                        )
                );


                boton.classList.add(
                    "activo"
                );


                filtroActual =
                    boton.dataset.filtro;


                renderizarMetas();
            }
        );
    }
);


// ==========================================
// RENDER
// ==========================================

function renderizarMetas() {

    listaMetas.innerHTML = "";


    let resultado =
        metas.filter(
            meta => {

                if (
                    filtroActual
                    === "activas"
                ) {

                    return (
                        meta.activa
                        &&
                        !meta.completada
                    );
                }


                if (
                    filtroActual
                    === "completadas"
                ) {

                    return Boolean(
                        meta.completada
                    );
                }


                return true;
            }
        );


    if (resultado.length === 0) {

        let mensaje =
            "No hay metas para mostrar.";


        if (
            filtroActual === "activas"
        ) {

            mensaje =
                "No tienes metas activas. Crea una nueva meta para comenzar.";
        }


        if (
            filtroActual
            === "completadas"
        ) {

            mensaje =
                "Todavía no has completado ninguna meta.";
        }


        listaMetas.innerHTML = `
            <div class="metas-vacio">
                ${mensaje}
            </div>
        `;

        return;
    }


    resultado.forEach(
        meta => {

            const tarjeta =
                document.createElement(
                    "article"
                );


            tarjeta.className =
                "meta-card";


            if (meta.completada) {

                tarjeta.classList.add(
                    "completada"
                );
            }


            if (!meta.activa) {

                tarjeta.classList.add(
                    "desactivada"
                );
            }


            const progreso =
                Number(
                    meta.progreso || 0
                );


            const informacionFecha =
                obtenerInformacionFecha(
                    meta
                );


            tarjeta.innerHTML = `

                <div class="meta-card-header">

                    <div class="meta-identidad">

                        <div class="meta-icono">
                            ${meta.icono || "🎯"}
                        </div>


                        <div>

                            <div class="meta-nombre">
                                ${meta.nombre}
                            </div>

                            <div class="meta-categoria">
                                ${
                                    meta.categoria
                                    ||
                                    "Sin categoría"
                                }
                            </div>

                        </div>

                    </div>


                    <div class="meta-menu">

                        <button
                            class="btn-editar-meta"
                            title="Editar"
                        >
                            ✎
                        </button>

                        <button
                            class="btn-borrar-meta"
                            title="Eliminar"
                        >
                            🗑
                        </button>

                    </div>

                </div>


                <div class="meta-descripcion">
                    ${
                        meta.descripcion
                        ||
                        "Sin descripción."
                    }
                </div>


                <div class="meta-fecha">

                    <span>
                        ${
                            meta.fecha_limite
                            ? "📅 "
                              + formatearFecha(
                                  meta.fecha_limite
                              )
                            : "📅 Sin fecha límite"
                        }
                    </span>


                    <span
                        class="
                            meta-dias
                            ${informacionFecha.clase}
                        "
                    >
                        ${informacionFecha.texto}
                    </span>

                </div>


                <div class="meta-progreso-superior">

                    <span>
                        Progreso
                    </span>

                    <strong>
                        ${progreso}%
                    </strong>

                </div>


                <div class="meta-barra">

                    <div
                        class="meta-barra-progreso"
                        style="
                            width:
                            ${Math.min(
                                progreso,
                                100
                            )}%
                        "
                    ></div>

                </div>


                <div class="meta-controles">

                    ${
                        meta.completada

                        ? `

                            <button
                                class="btn-reabrir-meta"
                            >
                                ↻ Reabrir meta
                            </button>

                            <span class="meta-dias completa">
                                ✓ Completada
                            </span>
                        `

                        : `

                            <div class="control-progreso-meta">

                                <button
                                    class="btn-progreso-meta restar"
                                    ${
                                        !meta.activa
                                        ? "disabled"
                                        : ""
                                    }
                                >
                                    −10
                                </button>


                                <button
                                    class="btn-progreso-meta sumar"
                                    ${
                                        !meta.activa
                                        ? "disabled"
                                        : ""
                                    }
                                >
                                    +10
                                </button>

                            </div>


                            <label
                                class="switch-meta"
                                title="${
                                    meta.activa
                                    ? "Desactivar"
                                    : "Activar"
                                }"
                            >

                                <input
                                    class="estado-meta"
                                    type="checkbox"

                                    ${
                                        meta.activa
                                        ? "checked"
                                        : ""
                                    }
                                >

                                <span
                                    class="switch-meta-slider"
                                ></span>

                            </label>
                        `
                    }

                </div>
            `;


            // EDITAR

            tarjeta
                .querySelector(
                    ".btn-editar-meta"
                )
                .addEventListener(
                    "click",
                    () =>
                        abrirEditarMeta(
                            meta
                        )
                );


            // ELIMINAR

            tarjeta
                .querySelector(
                    ".btn-borrar-meta"
                )
                .addEventListener(
                    "click",
                    () =>
                        abrirEliminarMeta(
                            meta
                        )
                );


            // COMPLETADA

            if (meta.completada) {

                tarjeta
                    .querySelector(
                        ".btn-reabrir-meta"
                    )
                    .addEventListener(
                        "click",
                        async () => {

                            await reabrirMeta(
                                meta.id
                            );
                        }
                    );

            } else {

                // RESTAR

                tarjeta
                    .querySelector(
                        ".restar"
                    )
                    .addEventListener(
                        "click",
                        async () => {

                            await cambiarProgreso(
                                meta,
                                -10
                            );
                        }
                    );


                // SUMAR

                tarjeta
                    .querySelector(
                        ".sumar"
                    )
                    .addEventListener(
                        "click",
                        async () => {

                            await cambiarProgreso(
                                meta,
                                10
                            );
                        }
                    );


                // ESTADO

                const switchEstado =
                    tarjeta.querySelector(
                        ".estado-meta"
                    );


                switchEstado.addEventListener(
                    "change",
                    async () => {

                        await cambiarEstado(
                            meta,
                            switchEstado
                        );
                    }
                );
            }


            listaMetas.appendChild(
                tarjeta
            );
        }
    );
}


// ==========================================
// FECHAS
// ==========================================

function formatearFecha(
    fechaTexto
) {

    const partes =
        fechaTexto.split("-");


    if (partes.length !== 3) {
        return fechaTexto;
    }


    const fecha =
        new Date(
            Number(partes[0]),
            Number(partes[1]) - 1,
            Number(partes[2])
        );


    return fecha.toLocaleDateString(
        "es-GT",
        {
            day: "numeric",
            month: "short",
            year: "numeric"
        }
    );
}


function obtenerInformacionFecha(
    meta
) {

    if (meta.completada) {

        return {
            texto: "✓ Completada",
            clase: "completa"
        };
    }


    if (
        meta.dias_restantes
        === null
        ||
        meta.dias_restantes
        === undefined
    ) {

        return {
            texto: "Sin límite",
            clase: ""
        };
    }


    const dias =
        Number(
            meta.dias_restantes
        );


    if (dias < 0) {

        const cantidad =
            Math.abs(dias);


        return {
            texto:
                `Vencida hace ${cantidad} `
                +
                `${cantidad === 1 ? "día" : "días"}`,

            clase: "vencida"
        };
    }


    if (dias === 0) {

        return {
            texto: "Vence hoy",
            clase: "urgente"
        };
    }


    if (dias === 1) {

        return {
            texto: "Queda 1 día",
            clase: "urgente"
        };
    }


    return {
        texto: `Quedan ${dias} días`,

        clase:
            dias <= 7
            ? "urgente"
            : ""
    };
}


// ==========================================
// CAMBIAR PROGRESO
// ==========================================

async function cambiarProgreso(
    meta,
    diferencia
) {

    const nuevo =
        Math.max(
            0,
            Math.min(
                100,
                Number(meta.progreso || 0)
                +
                diferencia
            )
        );


    try {

        const respuesta =
            await fetch(
                `/api/metas/${meta.id}/progreso`,
                {
                    method: "PATCH",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body:
                        JSON.stringify({
                            progreso: nuevo
                        })
                }
            );


        const datos =
            await respuesta.json();


        if (!respuesta.ok) {

            alert(
                datos.mensaje
                ||
                "No se pudo actualizar."
            );

            return;
        }


        await cargarMetas();


    } catch (error) {

        console.error(
            "Error actualizando progreso:",
            error
        );
    }
}


// ==========================================
// REABRIR
// ==========================================

async function reabrirMeta(
    metaId
) {

    try {

        const respuesta =
            await fetch(
                `/api/metas/${metaId}/reabrir`,
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
                "No se pudo reabrir."
            );

            return;
        }


        // La dejamos en 90% para que
        // vuelva a ser una meta pendiente.

        await fetch(
            `/api/metas/${metaId}/progreso`,
            {
                method: "PATCH",

                headers: {
                    "Content-Type":
                        "application/json"
                },

                body:
                    JSON.stringify({
                        progreso: 90
                    })
            }
        );


        await cargarMetas();


    } catch (error) {

        console.error(
            "Error reabriendo meta:",
            error
        );
    }
}


// ==========================================
// ACTIVAR / DESACTIVAR
// ==========================================

async function cambiarEstado(
    meta,
    switchElemento
) {

    const activo =
        switchElemento.checked;


    try {

        const respuesta =
            await fetch(
                `/api/metas/${meta.id}/estado`,
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


        await cargarMetas();


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
// NUEVA META
// ==========================================

nuevaMeta.addEventListener(
    "click",
    () => {

        metaEditando = null;


        tituloModalMeta.textContent =
            "Nueva meta";


        inputNombreMeta.value = "";
        inputDescripcionMeta.value = "";
        inputIconoMeta.value = "🎯";
        inputCategoriaMeta.value = "";
        inputFechaMeta.value = "";

        mensajeMeta.textContent = "";


        modalMeta.classList.add(
            "visible"
        );


        setTimeout(
            () =>
                inputNombreMeta.focus(),
            50
        );
    }
);


// ==========================================
// EDITAR
// ==========================================

function abrirEditarMeta(
    meta
) {

    metaEditando = meta;


    tituloModalMeta.textContent =
        "Editar meta";


    inputNombreMeta.value =
        meta.nombre || "";

    inputDescripcionMeta.value =
        meta.descripcion || "";

    inputIconoMeta.value =
        meta.icono || "🎯";

    inputCategoriaMeta.value =
        meta.categoria || "";

    inputFechaMeta.value =
        meta.fecha_limite || "";


    mensajeMeta.textContent = "";


    modalMeta.classList.add(
        "visible"
    );
}


// ==========================================
// GUARDAR
// ==========================================

guardarMeta.addEventListener(
    "click",
    async () => {

        mensajeMeta.textContent = "";


        const nombre =
            inputNombreMeta
                .value
                .trim();


        if (!nombre) {

            mensajeMeta.textContent =
                "Escribe el nombre de la meta.";

            inputNombreMeta.focus();

            return;
        }


        const cuerpo = {

            nombre,

            descripcion:
                inputDescripcionMeta
                    .value
                    .trim(),

            icono:
                inputIconoMeta
                    .value
                    .trim()
                || "🎯",

            categoria:
                inputCategoriaMeta
                    .value
                    .trim(),

            fecha_limite:
                inputFechaMeta.value
                || null
        };


        let url =
            "/api/metas";

        let metodo =
            "POST";


        if (metaEditando) {

            url =
                `/api/metas/${metaEditando.id}`;

            metodo =
                "PUT";
        }


        guardarMeta.disabled = true;

        guardarMeta.textContent =
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

                mensajeMeta.textContent =
                    datos.mensaje
                    ||
                    "No se pudo guardar.";

                return;
            }


            cerrarMeta();

            await cargarMetas();


        } catch (error) {

            console.error(
                "Error guardando meta:",
                error
            );


            mensajeMeta.textContent =
                "Error de conexión.";

        } finally {

            guardarMeta.disabled =
                false;

            guardarMeta.textContent =
                "Guardar meta";
        }
    }
);


// ==========================================
// ELIMINAR
// ==========================================

function abrirEliminarMeta(
    meta
) {

    metaEliminando = meta;


    nombreEliminarMeta.textContent =
        meta.nombre;


    modalEliminarMeta.classList.add(
        "visible"
    );
}


cancelarEliminarMeta.addEventListener(
    "click",
    cerrarEliminar
);


confirmarEliminarMeta.addEventListener(
    "click",
    async () => {

        if (!metaEliminando) {
            return;
        }


        confirmarEliminarMeta.disabled =
            true;

        confirmarEliminarMeta.textContent =
            "Eliminando...";


        try {

            const respuesta =
                await fetch(
                    `/api/metas/${metaEliminando.id}`,
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

            await cargarMetas();


        } catch (error) {

            console.error(
                "Error eliminando meta:",
                error
            );

        } finally {

            confirmarEliminarMeta.disabled =
                false;

            confirmarEliminarMeta.textContent =
                "Eliminar";
        }
    }
);


// ==========================================
// CERRAR MODALES
// ==========================================

function cerrarMeta() {

    modalMeta.classList.remove(
        "visible"
    );

    metaEditando = null;

    mensajeMeta.textContent = "";
}


function cerrarEliminar() {

    modalEliminarMeta.classList.remove(
        "visible"
    );

    metaEliminando = null;
}


cerrarModalMeta.addEventListener(
    "click",
    cerrarMeta
);


cancelarModalMeta.addEventListener(
    "click",
    cerrarMeta
);


modalMeta.addEventListener(
    "click",
    evento => {

        if (
            evento.target
            === modalMeta
        ) {

            cerrarMeta();
        }
    }
);


modalEliminarMeta.addEventListener(
    "click",
    evento => {

        if (
            evento.target
            === modalEliminarMeta
        ) {

            cerrarEliminar();
        }
    }
);


document.addEventListener(
    "keydown",
    evento => {

        if (evento.key !== "Escape") {
            return;
        }


        if (
            modalMeta.classList
                .contains("visible")
        ) {

            cerrarMeta();
        }


        if (
            modalEliminarMeta.classList
                .contains("visible")
        ) {

            cerrarEliminar();
        }
    }
);


// ==========================================
// INICIO
// ==========================================

cargarMetas();