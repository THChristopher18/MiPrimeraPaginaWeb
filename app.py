import os
import json
from flask import Flask, render_template, jsonify, redirect, abort
from googleapiclient.discovery import build
from google.oauth2 import service_account

app = Flask(__name__)

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
        return build('drive', 'v3', credentials=creds)
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
        return jsonify({"elementos": []})

    try:
        partes = [p.strip() for p in subpath.split('/') if p.strip()]
        if not partes:
            return jsonify({"elementos": []})

        ciclo_nombre = partes[0]
        query_ciclo = f"'{PARENT_FOLDER_ID}' in parents and mimeType = 'application/vnd.google-apps.folder' and name contains '{ciclo_nombre}' and trashed = false"
        res_ciclo = service.files().list(q=query_ciclo, pageSize=1, fields="files(id, name)").execute()
        folders_ciclo = res_ciclo.get('files', [])

        if not folders_ciclo:
            return jsonify({"elementos": []})

        folder_actual_id = folders_ciclo[0]['id']
        ruta_actual_acumulada = ciclo_nombre

        for parte in partes[1:]:
            query_sub = f"'{folder_actual_id}' in parents and mimeType = 'application/vnd.google-apps.folder' and name = '{parte}' and trashed = false"
            res_sub = service.files().list(q=query_sub, pageSize=1, fields="files(id, name)").execute()
            folders_sub = res_sub.get('files', [])
            
            if not folders_sub:
                return jsonify({"elementos": []})
            
            folder_actual_id = folders_sub[0]['id']
            ruta_actual_acumulada += f"/{parte}"

        # Pedimos webContentLink para enlaces directos y ordenamos por nombre
        query_items = f"'{folder_actual_id}' in parents and trashed = false"
        res_items = service.files().list(q=query_items, pageSize=100, fields="files(id, name, webContentLink, webViewLink, mimeType)").execute()
        items = res_items.get('files', [])

        # Ordenar carpetas primero y luego por nombre de forma alfabética/natural
        items = sorted(items, key=lambda x: (x.get('mimeType') != 'application/vnd.google-apps.folder', x.get('name')))

        elementos = []
        for item in items:
            is_folder = item.get('mimeType') == 'application/vnd.google-apps.folder'
            nombre = item.get('name')
            
            # Si es archivo, intentamos darle un enlace directo para que abra limpio
            link = item.get('webContentLink') or item.get('webViewLink', '#')
            
            elementos.append({
                "nombre": nombre,
                "es_carpeta": is_folder,
                "ruta_relativa": f"{ruta_actual_acumulada}/{nombre}",
                "url": link
            })

        return jsonify({"elementos": elementos})

    except Exception as e:
        print("Error al listar contenido:", e)
        return jsonify({"elementos": []})

if __name__ == '__main__':
    app.run(debug=True)