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
                            <a href="${item.url}" target="_blank" title="Abrir archivo" style="background: #f1f3f4; color: #333; padding: 8px 12px; border-radius: 8px; text-decoration: none; display: flex; align-items: center; justify-content: center; font-size: 14px;">
                                Ver ↗
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