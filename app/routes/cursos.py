from flask import Blueprint, render_template, request, session, flash, redirect, url_for, jsonify, g
from ..config import db

cursos_bp = Blueprint('cursos', __name__)

@cursos_bp.route('/cursos')
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
        return render_template('cursos.html', cursos=all_cursos, categories=sorted_categories, firebase_id_token=session.get('firebase_id_token', ''))
    except Exception as e:
        flash(f'Error al cargar los cursos: {str(e)}', 'danger')
        return render_template('cursos.html', cursos={}, categories=[])

@cursos_bp.route('/cursos_detalle/<string:curso_id>')
def cursos_detalle(curso_id):
    try:
        curso_data = db.child("cursos_disponibles").child(curso_id).get().val()
        if not curso_data:
            flash('Curso no encontrado.', 'danger')
            return redirect(url_for('cursos.cursos'))
        firebase_id_token = session.get('firebase_id_token', '')
        return render_template('cursos_detalle.html', curso=curso_data, curso_id=curso_id, firebase_id_token=firebase_id_token)
    except Exception as e:
        flash(f'Error al cargar el curso: {str(e)}', 'danger')
        return redirect(url_for('cursos.cursos'))