class User:
    def __init__(self, email, nombre, rol='user', cursos_adquiridos=None):
        self.email = email
        self.nombre = nombre
        self.rol = rol
        self.cursos_adquiridos = cursos_adquiridos or []

    @staticmethod
    def from_dict(uid, data):
        return User(
            email=data.get('email', ''),
            nombre=data.get('nombre', 'N/A'),
            rol=data.get('rol', 'user'),
            cursos_adquiridos=data.get('cursos_adquiridos', [])
        )