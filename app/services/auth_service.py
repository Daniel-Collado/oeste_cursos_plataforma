from datetime import datetime
from ..config import auth as pyrebase_auth, admin_db

class AuthService:
    @staticmethod
    def login(email, password):
        try:
            user = pyrebase_auth.sign_in_with_email_and_password(email, password)
            user_data = admin_db.reference(f"usuarios/{user['localId']}").get()
            return {
                'email': user['email'],
                'firebase_id_token': user['idToken'],
                'localId': user['localId'],
                'refreshToken': user['refreshToken'],
                'rol': user_data.get('rol', 'user') if user_data else 'user'
            }
        except Exception as e:
            error_message = "Error al iniciar sesión. Verifica tus credenciales."
            error_str = str(e)
            if "INVALID_LOGIN_CREDENTIALS" in error_str or "EMAIL_NOT_FOUND" in error_str or "INVALID_PASSWORD" in error_str:
                error_message = "Email o contraseña incorrectos."
            elif "TOO_MANY_ATTEMPTS_TRY_LATER" in error_str:
                error_message = "Demasiados intentos fallidos. Intenta de nuevo más tarde."
            raise Exception(error_message)

    @staticmethod
    def register(name, email, password, confirm_password):
        if not name or not email or not password or not confirm_password:
            raise Exception("Todos los campos son obligatorios.")
        if password != confirm_password:
            raise Exception("Las contraseñas no coinciden.")
        if len(password) < 6:
            raise Exception("La contraseña debe tener al menos 6 caracteres.")
        try:
            user = pyrebase_auth.create_user_with_email_and_password(email, password)
            admin_db.reference(f"usuarios/{user['localId']}").set({
                "nombre": name,
                "email": email,
                "rol": "user",
                "created_at": datetime.now().isoformat()
            })
            return {
                'email': user['email'],
                'firebase_id_token': user['idToken'],
                'localId': user['localId'],
                'refreshToken': user['refreshToken'],
                'rol': 'user'
            }
        except Exception as e:
            error_message = "Error al crear la cuenta. Intenta nuevamente."
            error_str = str(e)
            if "EMAIL_EXISTS" in error_str:
                error_message = "El correo electrónico ya está registrado."
            elif "WEAK_PASSWORD" in error_str:
                error_message = "La contraseña es demasiado débil. Debe tener al menos 6 caracteres."
            raise Exception(error_message)