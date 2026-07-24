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
                            <a href="/download/${item.ruta_relativa}" target="_blank" title="Descargar archivo" style="background: #f1f3f4; color: #333; padding: 8px 12px; border-radius: 50%; text-decoration: none; display: flex; align-items: center; justify-content: center; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                                ⬇️
                            </a>
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