import os
import json
from flask import Flask, render_template, jsonify
from googleapiclient.discovery import build
from google.oauth2 import service_account

app = Flask(__name__)

# Configuración de Google Drive API
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
PARENT_FOLDER_ID = '1KBMMPc0q35ea-sl75v644WyaydWqrJrg'

def obtener_servicio_drive():
    try:
        # Cargar credenciales desde la variable de entorno de Render o respaldo local
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

@app.route('/api/contenido/<int:numero_ciclo>')
def obtener_archivos_ciclo(numero_ciclo):
    service = obtener_servicio_drive()
    
    if not service:
        return jsonify([
            {"nombre": f"Configura credentials para ver Ciclo {numero_ciclo}", "url": "#"}
        ])

    try:
        # Paso A: Buscar la carpeta del ciclo correspondiente dentro de tu Drive
        query_folder = f"'{PARENT_FOLDER_ID}' in parents and mimeType = 'application/vnd.google-apps.folder' and name contains 'Ciclo {numero_ciclo}' and trashed = false"
        results_folder = service.files().list(q=query_folder, pageSize=1, fields="files(id, name)").execute()
        folders = results_folder.get('files', [])

        if not folders:
            return jsonify([{"nombre": f"No se encontró la carpeta 'Ciclo {numero_ciclo}' en tu Drive", "url": "#"}])

        ciclo_folder_id = folders[0]['id']

        # Paso B: Listar los archivos que están dentro de esa carpeta del ciclo
        query_files = f"'{ciclo_folder_id}' in parents and trashed = false"
        results_files = service.files().list(q=query_files, pageSize=50, fields="files(id, name, webViewLink, mimeType)").execute()
        files = results_files.get('files', [])

        lista_archivos = []
        for file in files:
            lista_archivos.append({
                "nombre": file.get('name'),
                "url": file.get('webViewLink'),
                "tipo": "folder" if "folder" in file.get('mimeType') else "file"
            })

        return jsonify(lista_archivos)

    except Exception as e:
        print("Error al listar archivos:", e)
        return jsonify([{"nombre": "Error al conectar con la API de Google Drive", "url": "#"}])

if __name__ == '__main__':
    app.run(debug=True)