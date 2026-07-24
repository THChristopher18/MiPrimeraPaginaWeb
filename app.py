import os
import json
from flask import Flask, render_template, jsonify, redirect, abort
from googleapiclient.discovery import build
from google.oauth2 import service_account

app = Flask(__name__)

# Configuración de Google Drive API
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
PARENT_FOLDER_ID = '1KBMMPc0q35ea-sl75v644WyaydWqrJrg'

def obtener_servicio_drive():
    try:
        google_creds_json = os.environ.get('GOOGLE_CREDENTIALS_JSON')
        if google_creds_json:
            creds_info = json.loads(google_creds_json)
            creds = service_account.Credentials.from_service_account_info(creds_info, scopes=SCOPES)
        else:
            creds = service_account.Credentials.from_service_account_file(
                'credentials.json', scopes=SCOPES)
        
        service = build('drive', 'v3', credentials=creds)
        return service
    except Exception as e:
        print("Error conectando a Drive:", e)
        return None

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/contenido/<path:subpath>')
def obtener_contenido_ruta(subpath):
    service = obtener_servicio_drive()
    if not service:
        return jsonify({"elementos": [{"nombre": "Error: Faltan credenciales de Drive", "es_carpeta": False, "ruta_relativa": "#"}]})

    try:
        partes = [p.strip() for p in subpath.split('/') if p.strip()]
        if not partes:
            return jsonify({"elementos": []})

        # 1. Buscar la carpeta principal del Ciclo (ej. "Ciclo 2")
        ciclo_nombre = partes[0]
        query_ciclo = f"'{PARENT_FOLDER_ID}' in parents and mimeType = 'application/vnd.google-apps.folder' and name contains '{ciclo_nombre}' and trashed = false"
        res_ciclo = service.files().list(q=query_ciclo, pageSize=1, fields="files(id, name)").execute()
        folders_ciclo = res_ciclo.get('files', [])

        if not folders_ciclo:
            return jsonify({"elementos": []})

        folder_actual_id = folders_ciclo[0]['id']
        ruta_actual_acumulada = ciclo_nombre

        # 2. Si hay subcarpetas en la ruta (ej. "Ciclo 2/Semana 1"), navegar dentro de ellas
        for parte in partes[1:]:
            query_sub = f"'{folder_actual_id}' in parents and mimeType = 'application/vnd.google-apps.folder' and name = '{parte}' and trashed = false"
            res_sub = service.files().list(q=query_sub, pageSize=1, fields="files(id, name)").execute()
            folders_sub = res_sub.get('files', [])
            
            if not folders_sub:
                return jsonify({"elementos": []})
            
            folder_actual_id = folders_sub[0]['id']
            ruta_actual_acumulada += f"/{parte}"

        # 3. Listar todo el contenido de la carpeta actual (tanto subcarpetas como archivos)
        query_items = f"'{folder_actual_id}' in parents and trashed = false"
        res_items = service.files().list(q=query_items, pageSize=100, fields="files(id, name, webViewLink, mimeType)").execute()
        items = res_items.get('files', [])

        elementos = []
        for item in items:
            is_folder = item.get('mimeType') == 'application/vnd.google-apps.folder'
            nombre = item.get('name')
            
            elementos.append({
                "nombre": nombre,
                "es_carpeta": is_folder,
                "ruta_relativa": f"{ruta_actual_acumulada}/{nombre}",
                "url": item.get('webViewLink', '#')
            })

        return jsonify({"elementos": elementos})

    except Exception as e:
        print("Error al listar contenido:", e)
        return jsonify({"elementos": []})

@app.route('/download/<path:filepath>')
def descargar_archivo(filepath):
    service = obtener_servicio_drive()
    if not service:
        return abort(404)
    
    try:
        partes = [p.strip() for p in filepath.split('/') if p.strip()]
        if not partes:
            return abort(404)
            
        # Encontrar la carpeta de ciclo
        query_ciclo = f"'{PARENT_FOLDER_ID}' in parents and mimeType = 'application/vnd.google-apps.folder' and name contains '{partes[0]}' and trashed = false"
        res_ciclo = service.files().list(q=query_ciclo, pageSize=1, fields="files(id, name)").execute()
        folders_ciclo = res_ciclo.get('files', [])
        if not folders_ciclo:
            return abort(404)
            
        folder_id = folders_ciclo[0]['id']
        
        # Navegar hasta el archivo final
        for parte in partes[1:-1]:
            query_sub = f"'{folder_id}' in parents and mimeType = 'application/vnd.google-apps.folder' and name = '{parte}' and trashed = false"
            res_sub = service.files().list(q=query_sub, pageSize=1, fields="files(id, name)").execute()
            folders_sub = res_sub.get('files', [])
            if not folders_sub:
                return abort(404)
            folder_id = folders_sub[0]['id']
            
        # Buscar el archivo objetivo
        nombre_archivo = partes[-1]
        query_file = f"'{folder_id}' in parents and name = '{nombre_archivo}' and trashed = false"
        res_file = service.files().list(q=query_file, pageSize=1, fields="files(id, webViewLink)").execute()
        files = res_file.get('files', [])
        
        if not files:
            return abort(404)
            
        return redirect(files[0]['webViewLink'])
    except Exception as e:
        print("Error en descarga:", e)
        return abort(404)

if __name__ == '__main__':
    app.run(debug=True)