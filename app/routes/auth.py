from flask import Blueprint, render_template, request, session, flash, redirect, url_for
from ..services.auth_service import AuthService
from ..decorators import login_required

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        try:
            user = AuthService.login(email, password)
            session['user'] = user['email']
            session['firebase_id_token'] = user['firebase_id_token']
            session['user_local_id'] = user['localId']
            session['refresh_token'] = user['refreshToken']
            session['rol'] = user['rol']
            flash('Inicio de sesión exitoso!', 'success')
            return redirect(url_for('dashboard.dashboard'))
        except Exception as e:
            flash(str(e), 'danger')
            print(f"Error de login: {e}")
            return render_template('login.html')
    return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name'].strip()
        email = request.form['email'].strip()
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        try:
            user = AuthService.register(name, email, password, confirm_password)
            session['user'] = user['email']
            session['firebase_id_token'] = user['firebase_id_token']
            session['user_local_id'] = user['localId']
            session['refresh_token'] = user['refreshToken']
            session['rol'] = user['rol']
            flash('Cuenta creada con éxito!', 'success')
            return redirect(url_for('dashboard.dashboard'))
        except Exception as e:
            print(f"Error de registro: {e}")
            return render_template('register.html', error=str(e))
    return render_template('register.html')

@auth_bp.route('/logout')
@login_required
def logout():
    session.clear()
    flash('Sesión finalizada, ¡hasta pronto!', 'success')
    return redirect(url_for('public.home'))