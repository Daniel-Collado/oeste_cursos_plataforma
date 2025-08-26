from flask import Flask, session, request, redirect, url_for
from .config import SECRET_KEY
from .routes.auth import auth_bp
from .routes.public import public_bp
from .routes.cursos import cursos_bp
from .routes.dashboard import dashboard_bp
from .routes.admin import admin_bp
from .routes.api import api_bp
from .decorators import refresh_user_token
import logging
import os

# Configurar logging para forzar salida a la consola
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s:%(name)s: %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)
print("DEBUG: Iniciando módulo __init__.py")
logger.debug("Iniciando módulo __init__.py")

def create_app():
    # Especificar explícitamente los directorios templates/ y static/ con rutas absolutas
    base_dir = os.path.abspath(os.path.dirname(__file__))
    template_dir = os.path.join(base_dir, '../templates')
    static_dir = os.path.join(base_dir, '../static')
    app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
    app.config['SECRET_KEY'] = SECRET_KEY
    print(f"DEBUG: Inicializando aplicación Flask con template_folder='{app.template_folder}'")
    logger.debug(f"Inicializando aplicación Flask con template_folder='{app.template_folder}'")
    print(f"DEBUG: Directorio actual de trabajo: {os.getcwd()}")
    logger.debug(f"Directorio actual de trabajo: {os.getcwd()}")
    print(f"DEBUG: Ruta absoluta de templates: {app.template_folder}")
    logger.debug(f"Ruta absoluta de templates: {app.template_folder}")
    print(f"DEBUG: Contenido de templates/: {os.listdir(template_dir)}")
    logger.debug(f"Contenido de templates/: {os.listdir(template_dir)}")
    print(f"DEBUG: Ruta absoluta de static: {app.static_folder}")
    logger.debug(f"Ruta absoluta de static: {app.static_folder}")
    try:
        print(f"DEBUG: Contenido de static/: {os.listdir(static_dir)}")
        logger.debug(f"Contenido de static/: {os.listdir(static_dir)}")
    except Exception as e:
        print(f"ERROR: No se pudo listar static/: {e}")
        logger.error(f"No se pudo listar static/: {e}")

    # Registrar blueprints
    print("DEBUG: Registrando blueprints")
    logger.debug("Registrando blueprints")
    app.register_blueprint(auth_bp, url_prefix='/')
    app.register_blueprint(public_bp, url_prefix='/')
    app.register_blueprint(cursos_bp, url_prefix='/')
    app.register_blueprint(dashboard_bp, url_prefix='/')
    app.register_blueprint(admin_bp, url_prefix='/')
    app.register_blueprint(api_bp, url_prefix='/api')

    # Refrescar token antes de cada solicitud, excluyendo static
    @app.before_request
    def before_request_refresh_token():
        logger.debug(f"Procesando before_request para endpoint: {request.endpoint}")
        if request.endpoint and not request.endpoint.startswith('static') and 'user' in session and 'refresh_token' in session and request.endpoint != 'auth.logout':
            logger.debug("Intentando refrescar token")
            try:
                refresh_user_token()
            except Exception as e:
                logger.error(f"No se pudo refrescar el token: {e}")
                session.clear()
                return redirect(url_for('auth.login'))

    return app