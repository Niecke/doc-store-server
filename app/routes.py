from flask import Blueprint, jsonify, session, request, redirect, url_for, render_template, flash
from models import db, User
from sqlalchemy import text
from password_handler import verify_password
from functools import wraps

bp = Blueprint('main', __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('main.login'))
        return f(*args, **kwargs)
    return decorated_function

def ping_db():
    try:
        db.session.execute(text("SELECT 1"))
        return True
    except:
        return False

@bp.route('/health')
def health():
    is_connected = ping_db()
    return {
        'status': 'healthy' if is_connected else 'unhealthy',
        'database': 'connected' if is_connected else 'disconnected',
        'authenticated': 'user_id' in session,
        'username': session.get('username')
    }

@bp.route('/')
def hello():
    return jsonify({'message': 'Doc Store API v3'})

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        if user and verify_password(password=password, password_hash=user.password):
            session['user_id'] = user.id
            session['username'] = user.username
            return redirect(url_for('main.protected'))
        else:
            flash('Invalid username or password')
    
    return render_template('login.html')

@bp.route('/logout', methods=['POST', 'GET'])
def logout():
    session.clear()
    flash('Logged out successfully')
    return redirect(url_for('main.hello'))

@bp.route('/protected')
@login_required
def protected():
    username = session.get('username', 'Unknown')
    user = User.query.filter_by(username=username).first()
    return jsonify({
        'message': f'Hello {user.username}!', 
        'roles': [r.name for r in user.roles]
    })
