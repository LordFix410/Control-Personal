// ==========================================
// ELEMENTOS
// ==========================================

const fechaProgreso =
    document.getElementById("fechaProgreso");

const tiempoHoy =
    document.getElementById("tiempoHoy");

const actividadesCompletadas =
    document.getElementById(
        "actividadesCompletadas"
    );

const habitosCompletados =
    document.getElementById(
        "habitosCompletados"
    );

const porcentajeHabitos =
    document.getElementById(
        "porcentajeHabitos"
    );

const totalSemana =
    document.getElementById(
        "totalSemana"
    );

const graficaSemana =
    document.getElementById(
        "graficaSemana"
    );

const listaCategorias =
    document.getElementById(
        "listaCategorias"
    );

const circuloPorcentaje =
    document.getElementById(
        "circuloPorcentaje"
    );

const detalleHabitosCompletados =
    document.getElementById(
        "detalleHabitosCompletados"
    );

const detalleHabitosPendientes =
    document.getElementById(
        "detalleHabitosPendientes"
    );

const detalleHabitosTotal =
    document.getElementById(
        "detalleHabitosTotal"
    );

const listaRendimiento =
    document.getElementById(
        "listaRendimiento"
    );


// ==========================================
// FECHA
// ==========================================

function mostrarFecha() {

    const ahora =
        new Date();


    fechaProgreso.textContent =
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
// FORMATEAR TIEMPO
// ==========================================

function formatearTiempo(segundos) {

    segundos =
        Math.max(
            0,
            Number(segundos || 0)
        );


    const horas =
        Math.floor(
            segundos / 3600
        );


    const minutos =
        Math.floor(
            (segundos % 3600)
            /
            60
        );


    if (horas > 0) {

        if (minutos > 0) {

            return `${horas}h ${minutos}m`;
        }

        return `${horas}h`;
    }


    if (minutos > 0) {

        return `${minutos}m`;
    }


    return `${Math.floor(segundos)}s`;
}


// ==========================================
// CARGAR
// ==========================================

async function cargarProgreso() {

    try {

        const respuesta =
            await fetch(
                "/api/progreso"
            );


        const datos =
            await respuesta.json();


        if (!respuesta.ok) {

            throw new Error(
                "No se pudo cargar el progreso."
            );
        }


        renderizarResumen(
            datos.resumen
        );


        renderizarSemana(
            datos.dias
        );


        renderizarCategorias(
            datos.categorias
        );


        renderizarRendimiento(
            datos.actividades
        );


    } catch (error) {

        console.error(
            "Error cargando progreso:",
            error
        );


        listaCategorias.innerHTML = `
            <div class="progreso-vacio">
                No se pudieron cargar
                las estadísticas.
            </div>
        `;


        listaRendimiento.innerHTML = `
            <div class="progreso-vacio">
                No se pudieron cargar
                las actividades.
            </div>
        `;
    }
}


// ==========================================
// RESUMEN
// ==========================================

function renderizarResumen(
    resumen
) {

    tiempoHoy.textContent =
        formatearTiempo(
            resumen.segundos_hoy
        );


    actividadesCompletadas.textContent =
        resumen.actividades_completadas;


    habitosCompletados.textContent =
        `${resumen.habitos_completados}`
        +
        ` / `
        +
        `${resumen.habitos_total}`;


    porcentajeHabitos.textContent =
        `${resumen.porcentaje_habitos}%`;


    circuloPorcentaje.textContent =
        `${resumen.porcentaje_habitos}%`;


    detalleHabitosCompletados.textContent =
        resumen.habitos_completados;


    const pendientes =
        Math.max(
            0,
            resumen.habitos_total
            -
            resumen.habitos_completados
        );


    detalleHabitosPendientes.textContent =
        pendientes;


    detalleHabitosTotal.textContent =
        resumen.habitos_total;


    // Círculo visual sin librerías externas

    const porcentaje =
        Math.max(
            0,
            Math.min(
                100,
                resumen.porcentaje_habitos
            )
        );


    circuloPorcentaje.parentElement.style
        .background =
            `conic-gradient(
                #6c8cff ${porcentaje}%,
                #303645 ${porcentaje}% 100%
            )`;


    circuloPorcentaje.parentElement.style
        .border =
            "9px solid transparent";
}


// ==========================================
// SEMANA
// ==========================================

function renderizarSemana(
    dias
) {

    graficaSemana.innerHTML =
        "";


    if (!dias || dias.length === 0) {

        graficaSemana.innerHTML = `
            <div class="progreso-vacio">
                Todavía no hay datos.
            </div>
        `;

        return;
    }


    const maximo =
        Math.max(
            ...dias.map(
                dia =>
                    Number(
                        dia.segundos || 0
                    )
            ),
            1
        );


    const total =
        dias.reduce(
            (acumulado, dia) =>
                acumulado
                +
                Number(
                    dia.segundos || 0
                ),
            0
        );


    totalSemana.textContent =
        formatearTiempo(total);


    const hoy =
        obtenerFechaLocal();


    dias.forEach(
        dia => {

            const segundos =
                Number(
                    dia.segundos || 0
                );


            let altura =
                segundos
                /
                maximo
                *
                100;


            if (
                segundos > 0
                &&
                altura < 4
            ) {

                altura = 4;
            }


            const columna =
                document.createElement(
                    "div"
                );


            columna.className =
                "dia-grafica";


            if (dia.fecha === hoy) {

                columna.classList.add(
                    "hoy"
                );
            }


            columna.innerHTML = `

                <div class="valor-grafica">
                    ${
                        segundos > 0
                        ? formatearTiempo(
                            segundos
                        )
                        : "—"
                    }
                </div>


                <div class="contenedor-barra-dia">

                    <div
                        class="barra-dia"
                        style="
                            height:
                            ${altura}%
                        "
                    ></div>

                </div>


                <div class="nombre-dia">
                    ${dia.dia}
                </div>
            `;


            graficaSemana.appendChild(
                columna
            );
        }
    );
}


// ==========================================
// FECHA LOCAL YYYY-MM-DD
// ==========================================

function obtenerFechaLocal() {

    const fecha =
        new Date();


    const anio =
        fecha.getFullYear();


    const mes =
        String(
            fecha.getMonth() + 1
        ).padStart(
            2,
            "0"
        );


    const dia =
        String(
            fecha.getDate()
        ).padStart(
            2,
            "0"
        );


    return `${anio}-${mes}-${dia}`;
}


// ==========================================
// CATEGORÍAS
// ==========================================

function renderizarCategorias(
    categorias
) {

    listaCategorias.innerHTML =
        "";


    if (
        !categorias
        ||
        categorias.length === 0
    ) {

        listaCategorias.innerHTML = `
            <div class="progreso-vacio">
                Todavía no hay tiempo
                registrado esta semana.
            </div>
        `;

        return;
    }


    const maximo =
        Math.max(
            ...categorias.map(
                categoria =>
                    Number(
                        categoria.segundos
                        ||
                        0
                    )
            ),
            1
        );


    categorias.forEach(
        categoria => {

            const segundos =
                Number(
                    categoria.segundos
                    ||
                    0
                );


            const porcentaje =
                segundos
                /
                maximo
                *
                100;


            const item =
                document.createElement(
                    "div"
                );


            item.className =
                "categoria-item";


            item.innerHTML = `

                <div class="categoria-nombre">
                    ${
                        categoria.categoria
                        ||
                        "Sin categoría"
                    }
                </div>


                <div class="categoria-barra">

                    <div
                        class="categoria-barra-progreso"
                        style="
                            width:
                            ${porcentaje}%
                        "
                    ></div>

                </div>


                <div class="categoria-tiempo">
                    ${formatearTiempo(
                        segundos
                    )}
                </div>
            `;


            listaCategorias.appendChild(
                item
            );
        }
    );
}


// ==========================================
// RENDIMIENTO
// ==========================================

function renderizarRendimiento(
    actividades
) {

    listaRendimiento.innerHTML =
        "";


    if (
        !actividades
        ||
        actividades.length === 0
    ) {

        listaRendimiento.innerHTML = `
            <div class="progreso-vacio">

                Todavía no has registrado
                actividades hoy.

                <br><br>

                Cuando utilices el temporizador
                aparecerán aquí.

            </div>
        `;

        return;
    }


    actividades.forEach(
        actividad => {

            const porcentaje =
                Number(
                    actividad.porcentaje
                    ||
                    0
                );


            const porcentajeVisual =
                Math.min(
                    porcentaje,
                    100
                );


            const item =
                document.createElement(
                    "div"
                );


            item.className =
                "rendimiento-item";


            if (porcentaje >= 100) {

                item.classList.add(
                    "superado"
                );
            }


            item.innerHTML = `

                <div class="rendimiento-icono">
                    ${
                        actividad.icono
                        ||
                        "📌"
                    }
                </div>


                <div>

                    <div class="rendimiento-nombre">
                        ${actividad.nombre}
                    </div>

                    <div class="rendimiento-categoria">
                        ${
                            actividad.categoria
                            ||
                            "Sin categoría"
                        }
                    </div>

                </div>


                <div class="rendimiento-datos">

                    <div class="rendimiento-tiempos">

                        <span>
                            Real:
                            ${formatearTiempo(
                                actividad.segundos
                            )}
                        </span>

                        <span>
                            Objetivo:
                            ${formatearTiempo(
                                actividad.objetivo
                            )}
                        </span>

                    </div>


                    <div class="rendimiento-barra">

                        <div
                            class="rendimiento-barra-progreso"
                            style="
                                width:
                                ${porcentajeVisual}%
                            "
                        ></div>

                    </div>

                </div>


                <div class="rendimiento-porcentaje">
                    ${porcentaje}%
                </div>
            `;


            listaRendimiento.appendChild(
                item
            );
        }
    );
}


// ==========================================
// INICIO
// ==========================================

mostrarFecha();

cargarProgreso();


// Actualizar cada minuto.
// Así el tiempo de una sesión que está
// corriendo también se refleja aquí.

setInterval(
    cargarProgreso,
    60000
);