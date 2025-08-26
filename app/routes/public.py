from flask import Blueprint, render_template, request, session, flash, redirect, url_for, jsonify, g
from ..config import db
from datetime import datetime

public_bp = Blueprint('public', __name__)

@public_bp.route('/')
def home():
    return render_template('home.html')

@public_bp.route('/about')
def about():
    return render_template('about.html')

@public_bp.route('/galeria')
def galeria():
    return render_template('galeria.html')

@public_bp.route('/contacts', methods=['GET', 'POST'])
def contacts():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']
        try:
            db.child("mensajes_contacto").push({
                "name": name,
                "email": email,
                "message": message,
                "timestamp": datetime.now().isoformat()
            })
            return render_template('contacts.html', success=True)
        except Exception as e:
            print(f"Error al guardar el mensaje de contacto: {e}")
            return render_template('contacts.html', error="Error al enviar el mensaje. Por favor, inténtalo de nuevo más tarde.")
    return render_template('contacts.html')