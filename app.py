import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

app = Flask(__name__)

# --- CONFIGURACIÓN DE SEGURIDAD Y LÍMITES ---
app.config['SECRET_KEY'] = 'tu_clave_secreta_super_segura' # Cambia esto por algo seguro luego
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['UPLOAD_FOLDER'] = 'uploads'

# ¡Aquí está el límite de 5 MB que elegiste! (5 * 1024 * 1024 bytes)
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024 

# Extensiones permitidas para los archivos de la universidad
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'pptx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Asegurar que exista la carpeta uploads
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# --- MODELO DE USUARIO (Base de datos) ---
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Crear la base de datos automáticamente al iniciar
with app.app_context():
    db.create_all()

# --- RUTAS DE LA APLICACIÓN ---
@app.route('/')
def index():
    return render_template('index.html')

# Ruta para subir archivos con validación de peso y formato
@app.route('/upload', methods=['POST'])
@login_required
def upload_file():
    if 'file' not in request.files:
        flash('No se seleccionó ningún archivo')
        return redirect(url_for('index'))
    
    file = request.files['file']
    
    if file.filename == '':
        flash('Nombre de archivo vacío')
        return redirect(url_for('index'))
        
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        flash('¡Archivo subido con éxito y dentro del límite permitido!')
        return redirect(url_for('index'))
    else:
        flash('Formato no permitido. Solo se aceptan PDF, DOCX o PPTX.')
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)