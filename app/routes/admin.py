from flask import Blueprint, render_template, request, session, flash, redirect, url_for, jsonify, g
from ..decorators import login_required, admin_required
from ..config import admin_db
import validators

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/crear_curso', methods=['GET'])
@login_required
@admin_required
def crear_curso():
    firebase_id_token = session.get('firebase_id_token')
    if not firebase_id_token:
        flash('No se encontró el token de autenticación. Por favor, inicia sesión de nuevo.', 'danger')
        return redirect(url_for('auth.login'))
    return render_template('crear_curso.html', firebase_id_token=firebase_id_token)

@admin_bp.route('/editar_curso/<string:curso_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def editar_curso(curso_id):
    id_token = session.get('firebase_id_token')
    if request.method == 'POST':
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
            admin_db.reference(f"cursos_disponibles/{curso_id}").update(updated_curso)
            flash('Curso actualizado exitosamente.', 'success')
            return redirect(url_for('dashboard.dashboard'))
        except Exception as e:
            flash(f'Error al actualizar el curso: {str(e)}', 'danger')
            return render_template('editar_curso.html', curso_id=curso_id, firebase_id_token=id_token)
    try:
        curso_data = admin_db.reference(f"cursos_disponibles/{curso_id}").get()
        if not curso_data:
            flash('Curso no encontrado.', 'danger')
            return redirect(url_for('dashboard.dashboard'))
        curso_data['id'] = curso_id
        return render_template('editar_curso.html', curso=curso_data, curso_id=curso_id, firebase_id_token=id_token)
    except Exception as e:
        flash(f'Error al cargar el curso para edición: {str(e)}', 'danger')
        return redirect(url_for('dashboard.dashboard'))