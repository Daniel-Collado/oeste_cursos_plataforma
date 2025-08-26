from functools import wraps
from flask import session, flash, redirect, url_for, request, jsonify, g
from firebase_admin import auth as admin_auth
from .config import auth as pyrebase_auth, admin_db

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            flash('Necesitas iniciar sesión para acceder a esta página.', 'warning')
            return redirect(url_for('auth.login'))
        try:
            decoded_token = admin_auth.verify_id_token(session['firebase_id_token'])
            g.user_id = decoded_token['uid']
        except admin_auth.ExpiredIdTokenError:
            if refresh_user_token():
                decoded_token = admin_auth.verify_id_token(session['firebase_id_token'])
                g.user_id = decoded_token['uid']
            else:
                flash('Sesión expirada. Por favor, inicia sesión de nuevo.', 'warning')
                session.clear()
                return redirect(url_for('auth.login'))
        except Exception as e:
            flash('Sesión inválida. Por favor, inicia sesión de nuevo.', 'warning')
            session.clear()
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'rol' not in session or session['rol'] != 'admin':
            flash('No tienes permiso para acceder a esta página.', 'danger')
            return redirect(url_for('dashboard.dashboard'))
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
            user_data = admin_db.reference(f'usuarios/{uid}').get()
            print(f"DEBUG: Datos de usuario obtenidos: {user_data}")
            if not user_data:
                print(f"DEBUG: user_data es None para UID: {uid}.")
                return jsonify({'error': 'No se encontraron datos de usuario.'}), 403
            if user_data.get('rol') != 'admin':
                print(f"DEBUG: Rol no es admin: {user_data.get('rol')}")
                return jsonify({'error': 'No tienes permisos para realizar esta acción'}), 403
            g.user_id = uid
            return f(*args, **kwargs)
        except Exception as e:
            print(f"ERROR: Excepción en api_admin_required: {e}")
            return jsonify({'error': f'Token inválido o expirado: {str(e)}'}), 401
    return decorated_function

def api_user_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'El token de autorización no tiene el formato correcto.'}), 401
        try:
            id_token = auth_header.split(' ')[1]
            decoded_token = admin_auth.verify_id_token(id_token)
            g.user_id = decoded_token['uid']
        except Exception as e:
            print(f"Error de autenticación: {e}")
            return jsonify({'error': 'Token de autenticación inválido o expirado.'}), 401
        return f(*args, **kwargs)
    return decorated_function

def refresh_user_token():
    if 'refresh_token' in session:
        try:
            refreshed = pyrebase_auth.refresh(session['refresh_token'])
            session['firebase_id_token'] = refreshed['idToken']
            session['refresh_token'] = refreshed['refreshToken']
            g.user_id_token = refreshed['idToken']
            return True
        except Exception as e:
            print(f"Error al renovar el token: {e}")
            return False
    return False