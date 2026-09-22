const confirmarCambio=document.getElementById("confirmarCambio");
const notificarInicio=document.getElementById("notificarInicio");
const notificarFin=document.getElementById("notificarFin");
const deteccionAutomatica=document.getElementById("deteccionAutomatica");
const detectarDuolingo=document.getElementById("detectarDuolingo");
const detectarKodree=document.getElementById("detectarKodree");
const temaAplicacion=document.getElementById("temaAplicacion");
const camaraHabilitada=document.getElementById("camaraHabilitada");
const concentracionCamara=document.getElementById("concentracionCamara");
const concentracionTolerancia=document.getElementById("concentracionTolerancia");
const estadoGuardado=document.getElementById("estadoGuardado");
const subopcionesDeteccion=document.getElementById("subopcionesDeteccion");
let cargandoConfiguracion=true,temporizadorMensaje=null;
function convertirBooleano(v){return String(v)==="1"||String(v).toLowerCase()==="true";}
async function cargarConfiguracion(){cargandoConfiguracion=true;try{const r=await fetch("/api/configuracion"),d=await r.json();if(!r.ok)throw new Error("No se pudo cargar la configuración.");const c=d.configuracion||{};confirmarCambio.checked=convertirBooleano(c.confirmar_cambio_actividad);notificarInicio.checked=convertirBooleano(c.notificar_inicio);notificarFin.checked=convertirBooleano(c.notificar_fin);deteccionAutomatica.checked=convertirBooleano(c.deteccion_automatica);detectarDuolingo.checked=convertirBooleano(c.detectar_duolingo);detectarKodree.checked=convertirBooleano(c.detectar_kodree);camaraHabilitada.checked=convertirBooleano(c.camara_habilitada);concentracionCamara.checked=convertirBooleano(c.concentracion_camara);concentracionTolerancia.value=c.concentracion_tolerancia||"10";temaAplicacion.value=c.tema||"oscuro";actualizarEstadoDeteccion();}catch(e){console.error(e);mostrarEstado("⚠ Error al cargar",true);}finally{cargandoConfiguracion=false;}}
async function guardarOpcion(k,v){if(cargandoConfiguracion)return;try{const r=await fetch("/api/configuracion",{method:"PUT",headers:{"Content-Type":"application/json"},body:JSON.stringify({[k]:v})}),d=await r.json();if(!r.ok)throw new Error(d.mensaje||"No se pudo guardar.");mostrarEstado("✓ Guardado");}catch(e){console.error(e);mostrarEstado("⚠ No se pudo guardar",true);}}
function mostrarEstado(t,e=false){clearTimeout(temporizadorMensaje);estadoGuardado.textContent=t;estadoGuardado.style.color=e?"#e4777f":"#69bd80";estadoGuardado.classList.add("visible");temporizadorMensaje=setTimeout(()=>estadoGuardado.classList.remove("visible"),1800);}
function actualizarEstadoDeteccion(){subopcionesDeteccion.classList.toggle("desactivadas",!deteccionAutomatica.checked);}
confirmarCambio.addEventListener("change",()=>guardarOpcion("confirmar_cambio_actividad",confirmarCambio.checked?"1":"0"));
notificarInicio.addEventListener("change",()=>guardarOpcion("notificar_inicio",notificarInicio.checked?"1":"0"));
notificarFin.addEventListener("change",()=>guardarOpcion("notificar_fin",notificarFin.checked?"1":"0"));
deteccionAutomatica.addEventListener("change",()=>{actualizarEstadoDeteccion();guardarOpcion("deteccion_automatica",deteccionAutomatica.checked?"1":"0");});
detectarDuolingo.addEventListener("change",()=>guardarOpcion("detectar_duolingo",detectarDuolingo.checked?"1":"0"));
detectarKodree.addEventListener("change",()=>guardarOpcion("detectar_kodree",detectarKodree.checked?"1":"0"));
temaAplicacion.addEventListener("change",()=>guardarOpcion("tema",temaAplicacion.value));
camaraHabilitada.addEventListener("change",()=>guardarOpcion("camara_habilitada",camaraHabilitada.checked?"1":"0"));
concentracionCamara.addEventListener("change",()=>guardarOpcion("concentracion_camara",concentracionCamara.checked?"1":"0"));
concentracionTolerancia.addEventListener("change",()=>guardarOpcion("concentracion_tolerancia",concentracionTolerancia.value));
cargarConfiguracion();
