import os
import json
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, auth as admin_auth, db as admin_db
import pyrebase
import cloudinary

load_dotenv()

# Configuración de Flask
SECRET_KEY = os.environ.get('FLASK_SECRET_KEY')

# Configuración de Cloudinary
cloudinary.config(
    cloud_name=os.environ.get('CLOUDINARY_CLOUD_NAME'),
    api_key=os.environ.get('CLOUDINARY_API_KEY'),
    api_secret=os.environ.get('CLOUDINARY_API_SECRET')
)

# Configuración de Firebase
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

# Configuración de Firebase Admin SDK
firebase_admin_json_str = os.environ.get('FIREBASE_ADMIN_CREDENTIALS')
if firebase_admin_json_str:
    cred_json = json.loads(firebase_admin_json_str)
    cred = credentials.Certificate(cred_json)
    firebase_admin.initialize_app(cred, {
        'databaseURL': firebase_config['databaseURL']
    })
else:
    raise ValueError("La variable de entorno FIREBASE_ADMIN_CREDENTIALS no está configurada.")

# Inicialización de Pyrebase
firebase = pyrebase.initialize_app(firebase_config)
auth = firebase.auth()
db = firebase.database()
storage = firebase.storage()
admin_db = admin_db