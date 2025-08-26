from ..config import admin_db
from ..models.user import User

class UserService:
    @staticmethod
    def get_all_users():
        try:
            users_data = admin_db.reference("usuarios").get() or {}
            users_list = [
                {
                    'id': uid,
                    'nombre': user_info.get('nombre', 'N/A'),
                    'email': user_info.get('email', 'N/A'),
                    'rol': user_info.get('rol', 'user')
                } for uid, user_info in users_data.items()
            ]
            return users_list
        except Exception as e:
            raise Exception(f"Error al obtener usuarios: {str(e)}")

    @staticmethod
    def get_user(user_id):
        try:
            user_data = admin_db.reference(f"usuarios/{user_id}").get()
            if not user_data:
                raise Exception("Usuario no encontrado")
            return User.from_dict(user_id, user_data).__dict__
        except Exception as e:
            raise Exception(f"Error al obtener datos del usuario: {str(e)}")

    @staticmethod
    def update_user_role(user_id, new_role):
        if new_role not in ['admin', 'user']:
            raise Exception("Rol inválido. Debe ser 'admin' o 'user'.")
        try:
            admin_db.reference(f"usuarios/{user_id}").update({"rol": new_role})
            return {"message": "Rol de usuario actualizado exitosamente"}
        except Exception as e:
            raise Exception(f"Error al actualizar rol de usuario: {str(e)}")

    @staticmethod
    def delete_user(user_id, current_user_id):
        if user_id == current_user_id:
            raise Exception("No puedes eliminar tu propia cuenta")
        try:
            admin_db.reference(f"usuarios/{user_id}").delete()
            return {"message": "Usuario eliminado de la base de datos"}
        except Exception as e:
            raise Exception(f"Error al eliminar usuario: {str(e)}")