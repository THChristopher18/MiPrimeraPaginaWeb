let cicloActual = "";
let historialRutas = []; 
let indiceHistorial = -1; 

function seleccionarCiclo(numeroCiclo) {
    cicloActual = numeroCiclo;
    historialRutas = [`Ciclo ${numeroCiclo}`]; 
    indiceHistorial = 0; 
    
    const tabBar = document.getElementById('tab-bar');
    tabBar.innerHTML = `<div class="tab">HOME</div><div class="tab active">Ciclo ${numeroCiclo}</div>`;
    
    renderizarCarpetaActual();
}

function renderizarCarpetaActual() {
    const subpath = historialRutas[indiceHistorial];
    
    let partes = subpath.split('/');
    let tituloTexto = partes.join(' / ');
    document.getElementById('semana-title').innerText = tituloTexto;

    const btnAnterior = document.getElementById('btn-anterior');
    const btnSiguiente = document.getElementById('btn-siguiente');

    if (indiceHistorial <= 0) {
        btnAnterior.style.opacity = "0.4";
        btnAnterior.style.cursor = "not-allowed";
        btnAnterior.disabled = true;
    } else {
        btnAnterior.style.opacity = "1";
        btnAnterior.style.cursor = "pointer";
        btnAnterior.disabled = false;
    }

    if (indiceHistorial >= historialRutas.length - 1) {
        btnSiguiente.style.opacity = "0.4";
        btnSiguiente.style.cursor = "not-allowed";
        btnSiguiente.disabled = true;
    } else {
        btnSiguiente.style.opacity = "1";
        btnSiguiente.style.cursor = "pointer";
        btnSiguiente.disabled = false;
    }

    fetch(`/api/contenido/${subpath}`)
        .then(response => response.json())
        .then(data => {
            let contenidoHtml = `<ul style="list-style: none; padding: 0; margin: 0;">`;

            if (data.elementos && data.elementos.length > 0) {
                data.elementos.forEach(item => {
                    if (item.es_carpeta) {
                        contenidoHtml += `<li style="cursor: pointer; padding: 12px 15px; display: flex; align-items: center; border-bottom: 1px solid #eee;" onclick="entrarCarpeta('${item.ruta_relativa}')">
                            <span style="font-size: 18px;">📁</span> 
                            <strong style="margin-left: 12px; text-align: left; font-weight: 600;">${item.nombre}</strong>
                        </li>`;
                    } else {
                        contenidoHtml += `<li style="padding: 10px 15px; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #eee;">
                            <div style="display: flex; align-items: center;">
                                <span style="font-size: 18px;">📄</span> 
                                <span style="margin-left: 12px; text-align: left;">${item.nombre}</span>
                            </div>
                            <div style="display: flex; gap: 8px;">
                                <button onclick="verPdf('${item.url_ver}', '${item.nombre}')" style="background: #0056b3; color: white; border: none; padding: 8px 14px; border-radius: 8px; cursor: pointer; font-size: 14px; font-weight: 500;">
                                    Ver 👁
                                </button>
                                <a href="${item.url_descargar}" target="_blank" title="Descargar archivo" style="background: #f1f3f4; color: #333; padding: 8px 12px; border-radius: 8px; text-decoration: none; display: flex; align-items: center; justify-content: center; font-size: 14px; font-weight: 500;">
                                    Descargar ⬇
                                </a>
                            </div>
                        </li>`;
                    }
                });
            } else {
                contenidoHtml += `<p style="color: #999; padding: 15px;">Esta carpeta está vacía.</p>`;
            }
            contenidoHtml += `</ul>`;
            document.getElementById('file-list').innerHTML = contenidoHtml;
        })
        .catch(error => console.error("Error al cargar el contenido:", error));
}

function entrarCarpeta(rutaRelativa) {
    historialRutas = historialRutas.slice(0, indiceHistorial + 1);
    historialRutas.push(rutaRelativa);
    indiceHistorial++;
    renderizarCarpetaActual();
}

function cambiarSemana(direccion) {
    if (direccion === -1 && indiceHistorial > 0) {
        indiceHistorial--;
        renderizarCarpetaActual();
    } else if (direccion === 1 && indiceHistorial < historialRutas.length - 1) {
        indiceHistorial++;
        renderizarCarpetaActual();
    }
}

// Función para abrir el PDF en una ventana flotante (Modal estilo Blackboard)
function verPdf(url, nombre) {
    let modal = document.getElementById('pdf-modal');
    if (!modal) {
        modal = document.createElement('div');
        modal.id = 'pdf-modal';
        modal.style.cssText = "position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.7); display: flex; justify-content: center; align-items: center; z-index: 1000;";
        modal.innerHTML = `
            <div style="background: white; width: 85%; height: 85%; border-radius: 12px; display: flex; flex-direction: column; overflow: hidden; box-shadow: 0 5px 15px rgba(0,0,0,0.3);">
                <div style="background: #1e293b; color: white; padding: 12px 20px; display: flex; justify-content: space-between; align-items: center;">
                    <h3 id="modal-title" style="margin: 0; font-size: 16px;">Visualizador</h3>
                    <button onclick="cerrarModal()" style="background: #ef4444; color: white; border: none; padding: 6px 12px; border-radius: 6px; cursor: pointer; font-weight: bold;">✕ Cerrar</button>
                </div>
                <iframe id="modal-iframe" style="width: 100%; height: 100%; border: none;"></iframe>
            </div>
        `;
        document.body.appendChild(modal);
    }
    document.getElementById('modal-title').innerText = nombre;
    document.getElementById('modal-iframe').src = url;
    modal.style.display = 'flex';
}

function cerrarModal() {
    let modal = document.getElementById('pdf-modal');
    if (modal) {
        modal.style.display = 'none';
        document.getElementById('modal-iframe').src = "";
    }
}