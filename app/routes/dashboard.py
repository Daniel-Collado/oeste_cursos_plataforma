from flask import Blueprint, render_template, request, session, flash, redirect, url_for, jsonify, g
from ..decorators import login_required

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard')
@login_required
def dashboard():
    firebase_id_token = session.get('firebase_id_token', '')
    firebase_auth_uid = session.get('user_local_id', '')
    user_role_class = f"dashboard-{session.get('rol', 'user')}"
    return render_template('dashboard.html', 
                        firebase_id_token=firebase_id_token,
                        firebase_auth_uid=firebase_auth_uid,
                        user_role_class=user_role_class)