from flask import Blueprint, render_template, request, session, flash, redirect, url_for, jsonify, g
from ..decorators import api_admin_required, api_user_required
from ..services.curso_service import CursoService
from ..services.user_service import UserService

api_bp = Blueprint('api', __name__)

@api_bp.route('/cursos', methods=['GET'])
def api_get_all_cursos():
    try:
        cursos = CursoService.get_all_cursos()
        return jsonify(cursos), 200
    except Exception as e:
        print(f"Error al obtener los cursos vía API: {str(e)}")
        return jsonify({"error": str(e)}), 500

@api_bp.route('/cursos', methods=['POST'])
@api_admin_required
def api_create_curso():
    try:
        curso_data = request.get_json()
        result = CursoService.create_curso(curso_data)
        return jsonify(result), 201
    except Exception as e:
        print(f"Error al crear el curso vía API: {str(e)}")
        return jsonify({"error": str(e)}), 500

@api_bp.route('/cursos/<string:curso_id>', methods=['GET'])
def api_get_curso(curso_id):
    try:
        curso = CursoService.get_curso(curso_id)
        return jsonify(curso), 200
    except Exception as e:
        print(f"Error al obtener el curso vía API: {str(e)}")
        return jsonify({"error": str(e)}), 500

@api_bp.route('/cursos/<string:curso_id>', methods=['PATCH', 'PUT'])
@api_admin_required
def api_update_curso(curso_id):
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Solicitud inválida: Se esperaba JSON.'}), 400
        result = CursoService.update_curso(curso_id, data)
        return jsonify(result), 200
    except Exception as e:
        print(f"Error al actualizar el curso vía API: {str(e)}")
        return jsonify({"error": str(e)}), 500

@api_bp.route('/cursos/<string:curso_id>', methods=['DELETE'])
@api_admin_required
def api_delete_curso(curso_id):
    try:
        result = CursoService.delete_curso(curso_id)
        return jsonify(result), 200
    except Exception as e:
        print(f"Error al eliminar el curso vía API: {str(e)}")
        return jsonify({"error": str(e)}), 500

@api_bp.route('/users', methods=['GET'])
@api_admin_required
def api_get_users():
    try:
        users = UserService.get_all_users()
        return jsonify(users), 200
    except Exception as e:
        print(f"Error al obtener usuarios vía API: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/users/<string:user_id>', methods=['GET'])
@api_user_required
def api_get_user(user_id):
    try:
        if user_id != g.user_id:
            return jsonify({'error': 'No tienes permiso para ver los datos de otro usuario.'}), 403
        user_data = UserService.get_user(user_id)
        return jsonify(user_data), 200
    except Exception as e:
        print(f"Error al obtener datos del usuario: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/users/<string:user_id>', methods=['PATCH'])
@api_admin_required
def api_update_user_role(user_id):
    try:
        data = request.get_json()
        new_role = data.get('rol')
        result = UserService.update_user_role(user_id, new_role)
        return jsonify(result), 200
    except Exception as e:
        print(f"Error al actualizar rol de usuario vía API: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/users/<string:user_id>', methods=['DELETE'])
@api_admin_required
def api_delete_user(user_id):
    try:
        result = UserService.delete_user(user_id, g.user_id)
        return jsonify(result), 200
    except Exception as e:
        print(f"Error al eliminar usuario vía API: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/adquirir_curso/<string:curso_id>', methods=['POST'])
@api_user_required
def adquirir_curso(curso_id):
    try:
        result = CursoService.adquirir_curso(g.user_id, curso_id)
        return jsonify(result), 200
    except Exception as e:
        print(f"Error al adquirir el curso: {str(e)}")
        return jsonify({'error': str(e)}), 500