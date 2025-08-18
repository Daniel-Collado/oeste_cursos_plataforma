import os
import json # Importamos la librería json para parsear el contenido del archivo de credenciales
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, auth as admin_auth, db as admin_db
from flask import Flask, render_template, request, flash, redirect, url_for, session, jsonify, g
import pyrebase
import cloudinary
import cloudinary.uploader
from functools import wraps
from datetime import datetime
import validators
import re

load_dotenv() 

app = Flask(__name__)
# 1. Leer la clave secreta de una variable de entorno
app.secret_key = os.environ.get('FLASK_SECRET_KEY')

# 2. Configurar Cloudinary con variables de entorno
cloudinary.config(
    cloud_name=os.environ.get('CLOUDINARY_CLOUD_NAME'),
    api_key=os.environ.get('CLOUDINARY_API_KEY'),
    api_secret=os.environ.get('CLOUDINARY_API_SECRET')
)

# --- INICIO DE LA SECCIÓN DE CONFIGURACIÓN DE FIREBASE ---
# 3. Leer la configuración de Firebase desde variables de entorno
firebase_config = {
    "apiKey": os.environ.get('FIREBASE_API_KEY'),
    "authDomain": os.environ.get('FIREBASE_AUTH_DOMAIN'),
    "databaseURL": os.environ.get('FIREBASE_DATABASE_URL'),
    "projectId": os.environ.get('FIREBASE_PROJECT_ID'),
    "storageBucket": os.environ.get('FIREBASE_STORAGE_BUCKET'),
    "messagingSenderId": os.environ.get('FIREBASE_MESSAGING_SENDER_ID'),
    "appId": os.environ.get('FIREBASE_APP_ID'),
    "measurementId": os.environ.get('FIREBASE_MEASUREMENT_ID')
}

# 4. Leer el contenido del archivo de credenciales de Firebase Admin desde una variable de entorno
# Usamos json.loads para convertir la cadena JSON en un objeto de Python
firebase_admin_json_str = os.environ.get('FIREBASE_ADMIN_CREDENTIALS')
if firebase_admin_json_str:
    cred_json = json.loads(firebase_admin_json_str)
    cred = credentials.Certificate(cred_json)
    firebase_admin.initialize_app(cred, {
        'databaseURL': firebase_config['databaseURL']
    })
else:
    raise ValueError("La variable de entorno FIREBASE_ADMIN_CREDENTIALS no está configurada.")

# 5. Inicialización de Pyrebase con la configuración de variables de entorno
firebase = pyrebase.initialize_app(firebase_config)
auth = firebase.auth()
db = firebase.database()
storage = firebase.storage()
# --- FIN DE LA SECCIÓN DE CONFIGURACIÓN DE FIREBASE ---

# --- Decoradores de Autenticación y Autorización ---
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            flash('Necesitas iniciar sesión para acceder a esta página.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'rol' not in session or session['rol'] != 'admin':
            flash('No tienes permiso para acceder a esta página.', 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

def api_admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            print("DEBUG: No hay encabezado de autorización o es inválido.")
            return jsonify({'error': 'Token de autenticación no proporcionado o inválido'}), 401
        try:
            id_token = auth_header.split('Bearer ')[1]
            print(f"DEBUG: id_token recibido (primeros 20 chars): {id_token[:20]}...")

            decoded_token = admin_auth.verify_id_token(id_token)
            uid = decoded_token['uid']
            print(f"DEBUG: UID extraído del token: {uid}")

            # Usa admin_db.reference() para la lectura con privilegios de administrador
            user_ref = admin_db.reference(f'usuarios/{uid}')
            print(f"DEBUG: Intentando leer datos de usuarios/{uid} usando admin_db.reference().get()")
            user_data = user_ref.get() # <-- ¡Este 'get' es del Admin SDK, no de pyrebase!
            
            print(f"DEBUG: Datos de usuario obtenidos (admin_db): {user_data}")
            print(f"DEBUG: Rol del usuario (si existe): {user_data.get('rol') if user_data else 'N/A'}")

            if not user_data:
                print(f"DEBUG: user_data es None para UID: {uid}. No se encontraron datos de usuario.")
                return jsonify({'error': 'No se encontraron datos de usuario para la verificación de rol.'}), 403
            
            if user_data.get('rol') != 'admin':
                print(f"DEBUG: El rol para UID {uid} no es 'admin'. Rol actual: {user_data.get('rol')}")
                return jsonify({'error': 'No tienes permisos para realizar esta acción'}), 403
            
            print(f"DEBUG: Usuario {uid} verificado como administrador. Procediendo con la ruta.")
            g.user_id_token = id_token # Guarda el token original para usarlo en otras operaciones de DB si es necesario
            return f(*args, **kwargs)
        except Exception as e:
            print(f"ERROR: Excepción en api_admin_required: {e}")
            return jsonify({'error': f'Token inválido o expirado: {str(e)}'}), 401
    return decorated_function

# --- Lógica de Sesión (Refresco de Token) ---
@app.before_request
def before_request_refresh_token():
    """Refresca el token de Firebase antes de cada petición si el usuario está logueado."""
    if 'user' in session and 'refresh_token' in session and request.endpoint != 'logout':
        try:
            user = auth.refresh(session['refresh_token'])
            session['user_id_token'] = user['idToken']
            g.user_id_token = user['idToken']
        except Exception as e:
            print(f"No se pudo refrescar el token: {e}. Desconectando usuario.")
            flash('Tu sesión ha expirado. Por favor, inicia sesión de nuevo.', 'warning')
            session.clear()
            return redirect(url_for('login'))

# --- Rutas Públicas ---
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/galeria')
def galeria():
    return render_template('galeria.html')

@app.route('/contacts', methods=['GET', 'POST'])
def contacts():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']
        try:
            db.child("mensajes_contacto").push({
                "name": name,
                "email": email,
                "message": message,
                "timestamp": datetime.now().isoformat()
            })
            return render_template('contacts.html', success=True)
        except Exception as e:
            print(f"Error al guardar el mensaje de contacto: {e}")
            return render_template('contacts.html', error="Error al enviar el mensaje. Por favor, inténtalo de nuevo más tarde.")
    return render_template('contacts.html')

@app.route('/cursos')
def cursos():
    try:
        all_cursos = db.child("cursos_disponibles").get().val() or {}
        categories = set()
        for key, curso in all_cursos.items():
            if curso and 'tags' in curso and isinstance(curso['tags'], (str, list)):
                tags = curso['tags'] if isinstance(curso['tags'], list) else curso['tags'].split(',')
                for tag in tags:
                    categories.add(tag.strip().capitalize())
        sorted_categories = sorted(list(categories))
        return render_template('cursos.html', cursos=all_cursos, categories=sorted_categories, firebase_id_token=session.get('user_id_token', ''))
    except Exception as e:
        flash(f'Error al cargar los cursos: {str(e)}', 'danger')
        return render_template('cursos.html', cursos={}, categories=[])

@app.route('/cursos_detalle/<string:curso_id>')
def cursos_detalle(curso_id):
    try:
        curso_data = db.child("cursos_disponibles").child(curso_id).get().val()
        if not curso_data:
            flash('Curso no encontrado.', 'danger')
            return redirect(url_for('cursos'))
        return render_template('cursos_detalle.html', curso=curso_data, curso_id=curso_id, firebase_id_token=session.get('user_id_token', ''))
    except Exception as e:
        flash(f'Error al cargar el curso: {str(e)}', 'danger')
        return redirect(url_for('cursos'))

# --- Rutas de Autenticación ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        try:
            user = auth.sign_in_with_email_and_password(email, password)
            session['user'] = user['email']
            session['user_id_token'] = user['idToken']
            session['refresh_token'] = user['refreshToken']
            session['user_local_id'] = user['localId']
            
            # --- CAMBIO CLAVE: Usar admin_db para obtener el rol del usuario ---
            user_data = admin_db.reference(f"usuarios/{user['localId']}").get()
            # --- FIN CAMBIO CLAVE ---

            session['rol'] = user_data.get('rol', 'user') if user_data else 'user'
            flash('Inicio de sesión exitoso!', 'success')
            return redirect(url_for('dashboard'))
        except Exception as e:
            error_message = "Error al iniciar sesión. Verifica tus credenciales."
            error_str = str(e)
            if "INVALID_LOGIN_CREDENTIALS" in error_str or "EMAIL_NOT_FOUND" in error_str or "INVALID_PASSWORD" in error_str:
                error_message = "Email o contraseña incorrectos."
            elif "TOO_MANY_ATTEMPTS_TRY_LATER" in error_str:
                error_message = "Demasiados intentos fallidos. Intenta de nuevo más tarde."
            flash(error_message, 'danger')
            print(f"Error de login: {e}")
            return render_template('login.html')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name'].strip()
        email = request.form['email'].strip()
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        # Validaciones en el servidor
        if not name or not email or not password or not confirm_password:
            return render_template('register.html', error="Todos los campos son obligatorios.")
        if password != confirm_password:
            return render_template('register.html', error="Las contraseñas no coinciden.")
        if len(password) < 6:
            return render_template('register.html', error="La contraseña debe tener al menos 6 caracteres.")

        try:
            # Crear usuario en Firebase Authentication
            user = auth.create_user_with_email_and_password(email, password)
            
            # --- CAMBIO CLAVE: Usar admin_db para guardar datos adicionales en la Realtime Database ---
            admin_db.reference(f"usuarios/{user['localId']}").set({
                "nombre": name,
                "email": email,
                "rol": "user",
                "created_at": datetime.now().isoformat()
            })
            # --- FIN CAMBIO CLAVE ---

            # Iniciar sesión automáticamente tras el registro
            session['user'] = user['email']
            session['user_id_token'] = user['idToken']
            session['refresh_token'] = user['refreshToken']
            session['user_local_id'] = user['localId']
            session['rol'] = 'user'
            flash('Cuenta creada con éxito!', 'success')
            return redirect(url_for('dashboard'))
        except Exception as e:
            error_message = "Error al crear la cuenta. Intenta nuevamente."
            error_str = str(e)
            if "EMAIL_EXISTS" in error_str:
                error_message = "El correo electrónico ya está registrado."
            elif "WEAK_PASSWORD" in error_str:
                error_message = "La contraseña es demasiado débil. Debe tener al menos 6 caracteres."
            print(f"Error de registro: {e}")
            return render_template('register.html', error=error_message)
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Sesión finalizada, ¡hasta pronto!', 'success')
    return redirect(url_for('home'))

# --- Rutas de la Aplicación (Vistas para Usuarios) ---
@app.route('/dashboard')
@login_required
def dashboard():
    firebase_id_token = session.get('user_id_token')
    user_role_class = f"dashboard-{session.get('rol', 'user')}"
    return render_template('dashboard.html', firebase_id_token=firebase_id_token, user_role_class=user_role_class)

# --- Rutas de Administración (Formularios) ---
@app.route('/crear_curso', methods=['GET']) # Solo GET, el POST lo manejará la API
@login_required
@admin_required
def crear_curso():
    firebase_id_token = session.get('user_id_token')
    if not firebase_id_token:
        flash('No se encontró el token de autenticación. Por favor, inicia sesión de nuevo.', 'danger')
        return redirect(url_for('login'))
    return render_template('crear_curso.html', firebase_id_token=firebase_id_token)

@app.route('/editar_curso/<string:curso_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def editar_curso(curso_id):
    id_token = session.get('user_id_token') # Esto obtiene tu token de Firebase

    if request.method == 'POST':
        # Esta lógica de POST ya no debería ser usada si el frontend usa la API PATCH/PUT
        # Deberías eliminar este bloque si el frontend siempre usa la API.
        # Si lo mantienes, asegúrate de que use admin_db para la actualización.
        try:
            precio_float = float(request.form['precio'])
            updated_curso = {
                "nombre": request.form['nombre'],
                "descripcion": request.form['descripcion'],
                "duracion": request.form['duracion'],
                "precio": precio_float,
                "tags": request.form['tags'],
                "detalle": request.form['detalle']
            }
            if 'imagen' in request.form and request.form['imagen']:
                if not validators.url(request.form['imagen']):
                    flash('La URL de la imagen no es válida.', 'danger')
                    return render_template('editar_curso.html', curso=updated_curso, curso_id=curso_id, firebase_id_token=id_token)
                updated_curso['imagen'] = request.form['imagen']
            
            # Aquí también deberías usar admin_db.reference().update() si quieres bypassar las reglas de cliente
            admin_db.reference(f"cursos_disponibles/{curso_id}").update(updated_curso) # CAMBIO
            flash('Curso actualizado exitosamente.', 'success')
            return redirect(url_for('dashboard'))
        except Exception as e:
            flash(f'Error al actualizar el curso: {str(e)}', 'danger')
            return render_template('editar_curso.html', curso_id=curso_id, firebase_id_token=id_token)

    try:
        # Aquí también deberías usar admin_db.reference().get() si quieres bypassar las reglas de cliente
        curso_data = admin_db.reference(f"cursos_disponibles/{curso_id}").get() # CAMBIO
        if not curso_data:
            flash('Curso no encontrado.', 'danger')
            return redirect(url_for('dashboard'))
        curso_data['id'] = curso_id
        return render_template('editar_curso.html', 
                            curso=curso_data, 
                            curso_id=curso_id, 
                            firebase_id_token=id_token)
    except Exception as e:
        flash(f'Error al cargar el curso para edición: {str(e)}', 'danger')
        return redirect(url_for('dashboard'))
    
# --- Rutas API ---

# Ruta para OBTENER todos los cursos (Acceso Público)
@app.route('/api/cursos', methods=['GET'])
def api_get_all_cursos(): # Renombrado para claridad
    try:
        cursos = db.child('cursos_disponibles').get().val() or {}
        return jsonify(cursos), 200
    except Exception as e:
        print(f"Error al obtener los cursos vía API: {str(e)}")
        return jsonify({"error": f"Error interno del servidor al obtener los cursos: {str(e)}"}), 500

# Ruta para CREAR un nuevo curso (Requiere Admin)
@app.route('/api/cursos', methods=['POST'])
@api_admin_required # <--- ¡Aplicamos el decorador aquí!
def api_create_curso(): # Nueva función para POST
    try:
        # La autenticación y autorización ya fueron manejadas por api_admin_required
        # No necesitas repetir la lógica de token aquí.
        
        curso_data = request.get_json()
        if not curso_data or not isinstance(curso_data, dict):
            return jsonify({"error": "Datos del curso no proporcionados o inválidos"}), 400
        
        required_fields = ['nombre', 'descripcion', 'precio'] # 'precio' también es requerido
        for field in required_fields:
            if field not in curso_data or (field != 'precio' and not curso_data[field]) or (field == 'precio' and (curso_data[field] is None or curso_data[field] < 0)):
                return jsonify({"error": f"Faltan campos requeridos o son inválidos: {field}"}), 400

        # Validación de precio (más robusta)
        try:
            precio_float = float(curso_data.get('precio'))
            if precio_float < 0:
                return jsonify({"error": "El precio no puede ser negativo."}), 400
            curso_data['precio'] = precio_float
        except (ValueError, TypeError):
            return jsonify({"error": "El precio debe ser un número válido."}), 400

        # Validación de imagen URL
        if 'imagen' in curso_data and curso_data['imagen']:
            if not validators.url(curso_data['imagen']):
                return jsonify({"error": "URL de la imagen no es válida"}), 400
        
        # Manejo de tags
        if 'tags' in curso_data and isinstance(curso_data['tags'], str):
            curso_data['tags'] = [tag.strip() for tag in curso_data['tags'].split(',')] if curso_data['tags'] else []
        elif 'tags' not in curso_data or not isinstance(curso_data['tags'], list):
            curso_data['tags'] = [] # Asegura que tags sea una lista

        # Añadir fecha de creación
        curso_data['fechaCreacion'] = datetime.now().isoformat()

        # --- CAMBIO CLAVE: Usar admin_db para la operación de escritura ---
        nuevo_curso_ref = admin_db.reference('cursos_disponibles').push(curso_data)
        
        return jsonify({"message": "Curso creado exitosamente", "curso_id": nuevo_curso_ref.key}), 201
    except Exception as e:
        print(f"Error al crear el curso vía API: {str(e)}")
        return jsonify({"error": f"Error interno del servidor al crear el curso: {str(e)}"}), 500


# Ruta para OBTENER un curso por ID (Acceso Público)
@app.route('/api/cursos/<string:curso_id>', methods=['GET'])
def api_get_curso(curso_id):
    try:
        # Aquí no necesitas token, ya que es acceso público (si tus reglas RTDB lo permiten)
        curso = db.child('cursos_disponibles').child(curso_id).get().val()
        if not curso:
            return jsonify({"error": "Curso no encontrado"}), 404
        return jsonify(curso), 200
    except Exception as e:
        print(f"Error al obtener el curso vía API: {str(e)}")
        return jsonify({"error": f"Error interno del servidor al obtener el curso: {str(e)}"}), 500

# Ruta para ACTUALIZAR un curso por ID (Requiere Admin)
@app.route('/api/cursos/<string:curso_id>', methods=['PATCH', 'PUT'])
@api_admin_required # <-- Usa tu decorador de administrador aquí
def api_update_curso(curso_id):
    try:
        id_token = g.user_id_token # El token ya está verificado y disponible aquí
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Solicitud inválida: Se esperaba JSON.'}), 400

        updated_curso = {}

        fields_to_check = ['nombre', 'descripcion', 'detalle', 'duracion', 'tags']
        for field in fields_to_check:
            if field in data:
                updated_curso[field] = data[field]

        if 'precio' in data:
            if data['precio'] is not None and (not isinstance(data['precio'], (int, float)) or data['precio'] < 0):
                return jsonify({"error": "El precio debe ser un número no negativo"}), 400
            updated_curso['precio'] = data['precio']

        if 'imagen' in data:
            imagen_url = data.get('imagen')
            if imagen_url:
                if not validators.url(imagen_url):
                    return jsonify({'error': 'La URL de la imagen no es válida.'}), 400
                updated_curso['imagen'] = imagen_url
            else:
                updated_curso['imagen'] = ''

        # --- CAMBIO CLAVE: Usar admin_db para la operación de escritura ---
        if updated_curso:
            admin_db.reference(f'cursos_disponibles/{curso_id}').update(updated_curso)
            return jsonify({"message": "Curso actualizado exitosamente"}), 200
        else:
            return jsonify({"message": "No hay datos para actualizar"}), 200

    except ValueError:
        return jsonify({'error': 'El precio debe ser un número válido.'}), 400
    except Exception as e:
        print(f"Error al actualizar el curso vía API: {str(e)}")
        return jsonify({"error": f"Error interno del servidor al actualizar el curso: {str(e)}"}), 500

# Ruta para ELIMINAR un curso por ID (Requiere Admin)
@app.route('/api/cursos/<string:curso_id>', methods=['DELETE'])
@api_admin_required # <-- Usa tu decorador de administrador aquí
def api_delete_curso(curso_id):
    try:
        id_token = g.user_id_token # El token ya está verificado y disponible aquí
        
        # Opcional pero recomendado: Verificar si el curso existe antes de intentar eliminar
        # Aquí puedes usar db de pyrebase o admin_db.reference().get()
        curso_existente = admin_db.reference(f'cursos_disponibles/{curso_id}').get() # Usar admin_db para lectura privilegiada
        if not curso_existente:
            return jsonify({'error': 'Curso no encontrado.'}), 404

        # --- CAMBIO CLAVE: Usar admin_db para la operación de eliminación ---
        admin_db.reference(f'cursos_disponibles/{curso_id}').delete()

        # Eliminar la imagen de Cloudinary si existe una URL de imagen
        if 'imagen' in curso_existente and curso_existente['imagen']:
            match = re.search(r'/v\d+/(.+?)(?:\.\w+)?$', curso_existente['imagen'])
            if match:
                public_id = match.group(1)
                try:
                    cloudinary.uploader.destroy(public_id)
                    print(f"DEBUG: Imagen '{public_id}' eliminada de Cloudinary.")
                except Exception as cloudinary_e:
                    print(f"ADVERTENCIA: No se pudo eliminar la imagen de Cloudinary '{public_id}': {cloudinary_e}")
            else:
                print(f"ADVERTENCIA: No se pudo extraer public_id de la URL de la imagen: {curso_existente['imagen']}")

        return jsonify({'message': 'Curso eliminado exitosamente.'}), 200

    except Exception as e:
        print(f"Error al eliminar el curso vía API: {str(e)}")
        return jsonify({"error": f"Error interno del servidor al eliminar el curso: {str(e)}"}), 500

@app.route('/api/users', methods=['GET'])
@api_admin_required
def api_get_users():
    try:
        id_token = g.user_id_token
        # Usar admin_db para obtener todos los usuarios si las reglas de pyrebase lo impiden
        users_data = admin_db.reference("usuarios").get() or {}
        users_list = [
            {
                'id': uid,
                'nombre': user_info.get('nombre', 'N/A'),
                'email': user_info.get('email', 'N/A'),
                'rol': user_info.get('rol', 'user')
            } for uid, user_info in users_data.items()
        ]
        return jsonify(users_list), 200
    except Exception as e:
        print(f"Error al obtener usuarios via API: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/users/<string:user_id>', methods=['PATCH'])
@api_admin_required
def api_update_user_role(user_id):
    try:
        data = request.get_json()
        new_role = data.get('rol')
        if not new_role or new_role not in ['admin', 'user']:
            return jsonify({'error': "Rol inválido. Debe ser 'admin' o 'user'."}), 400
        id_token = g.user_id_token
        # Usar admin_db para actualizar el rol
        admin_db.reference(f"usuarios/{user_id}").update({"rol": new_role})
        return jsonify({'message': 'Rol de usuario actualizado exitosamente.'}), 200
    except Exception as e:
        print(f"Error al actualizar rol de usuario via API: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/users/<string:user_id>', methods=['DELETE'])
@api_admin_required
def api_delete_user(user_id):
    try:
        id_token = g.user_id_token
        if user_id == session.get('user_local_id'):
            return jsonify({'error': 'No puedes eliminar tu propia cuenta.'}), 403
        # Usar admin_db para eliminar el usuario
        admin_db.reference(f"usuarios/{user_id}").delete()
        return jsonify({'message': 'Usuario eliminado de la base de datos.'}), 200
    except Exception as e:
        print(f"Error al eliminar usuario via API: {e}")
        return jsonify({'error': str(e)}), 500

# --- Punto de Entrada de la Aplicación ---
if __name__ == '__main__':
    # Usamos os.environ.get para que el puerto sea configurable por Render
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
