from ..config import admin_db, db
from datetime import datetime
import validators
import re
import cloudinary.uploader

class CursoService:
    @staticmethod
    def get_all_cursos():
        try:
            cursos = db.child('cursos_disponibles').get().val() or {}
            return cursos
        except Exception as e:
            raise Exception(f"Error al obtener los cursos: {str(e)}")

    @staticmethod
    def get_curso(curso_id):
        try:
            curso = db.child('cursos_disponibles').child(curso_id).get().val()
            if not curso:
                raise Exception("Curso no encontrado")
            return curso
        except Exception as e:
            raise Exception(f"Error al obtener el curso: {str(e)}")

    @staticmethod
    def create_curso(curso_data):
        required_fields = ['nombre', 'descripcion', 'precio']
        for field in required_fields:
            if field not in curso_data or (field != 'precio' and not curso_data[field]) or (field == 'precio' and (curso_data[field] is None or curso_data[field] < 0)):
                raise Exception(f"Faltan campos requeridos o son inválidos: {field}")
        try:
            precio_float = float(curso_data.get('precio'))
            if precio_float < 0:
                raise Exception("El precio no puede ser negativo.")
            curso_data['precio'] = precio_float
        except (ValueError, TypeError):
            raise Exception("El precio debe ser un número válido.")
        if 'imagen' in curso_data and curso_data['imagen'] and not validators.url(curso_data['imagen']):
            raise Exception("URL de la imagen no es válida")
        if 'tags' in curso_data and isinstance(curso_data['tags'], str):
            curso_data['tags'] = [tag.strip() for tag in curso_data['tags'].split(',')] if curso_data['tags'] else []
        elif 'tags' not in curso_data or not isinstance(curso_data['tags'], list):
            curso_data['tags'] = []
        curso_data['fechaCreacion'] = datetime.now().isoformat()
        try:
            nuevo_curso_ref = admin_db.reference('cursos_disponibles').push(curso_data)
            return {"message": "Curso creado exitosamente", "curso_id": nuevo_curso_ref.key}
        except Exception as e:
            raise Exception(f"Error al crear el curso: {str(e)}")

    @staticmethod
    def update_curso(curso_id, data):
        updated_curso = {}
        fields_to_check = ['nombre', 'descripcion', 'detalle', 'duracion', 'tags']
        for field in fields_to_check:
            if field in data:
                updated_curso[field] = data[field]
        if 'precio' in data:
            if data['precio'] is not None and (not isinstance(data['precio'], (int, float)) or data['precio'] < 0):
                raise Exception("El precio debe ser un número no negativo")
            updated_curso['precio'] = data['precio']
        if 'imagen' in data:
            imagen_url = data.get('imagen')
            if imagen_url and not validators.url(imagen_url):
                raise Exception("La URL de la imagen no es válida.")
            updated_curso['imagen'] = imagen_url if imagen_url else ''
        if updated_curso:
            try:
                admin_db.reference(f'cursos_disponibles/{curso_id}').update(updated_curso)
                return {"message": "Curso actualizado exitosamente"}
            except Exception as e:
                raise Exception(f"Error al actualizar el curso: {str(e)}")
        return {"message": "No hay datos para actualizar"}

    @staticmethod
    def delete_curso(curso_id):
        try:
            curso_existente = admin_db.reference(f'cursos_disponibles/{curso_id}').get()
            if not curso_existente:
                raise Exception("Curso no encontrado")
            admin_db.reference(f'cursos_disponibles/{curso_id}').delete()
            if 'imagen' in curso_existente and curso_existente['imagen']:
                match = re.search(r'/v\d+/(.+?)(?:\.\w+)?$', curso_existente['imagen'])
                if match:
                    public_id = match.group(1)
                    try:
                        cloudinary.uploader.destroy(public_id)
                        print(f"DEBUG: Imagen '{public_id}' eliminada de Cloudinary.")
                    except Exception as cloudinary_e:
                        print(f"ADVERTENCIA: No se pudo eliminar la imagen de Cloudinary '{public_id}': {cloudinary_e}")
            return {"message": "Curso eliminado exitosamente"}
        except Exception as e:
            raise Exception(f"Error al eliminar el curso: {str(e)}")

    @staticmethod
    def adquirir_curso(user_id, curso_id):
        try:
            user_data = admin_db.reference(f'usuarios/{user_id}').get()
            course_data = admin_db.reference(f'cursos_disponibles/{curso_id}').get()
            if not user_data:
                raise Exception("Usuario no encontrado")
            if not course_data:
                raise Exception("Curso no encontrado")
            cursos_adquiridos = user_data.get('cursos_adquiridos', [])
            if curso_id in cursos_adquiridos:
                return {"message": "Ya has adquirido este curso"}
            cursos_adquiridos.append(curso_id)
            admin_db.reference(f'usuarios/{user_id}').update({'cursos_adquiridos': cursos_adquiridos})
            return {"message": "Curso adquirido exitosamente"}
        except Exception as e:
            raise Exception(f"Error al adquirir el curso: {str(e)}")