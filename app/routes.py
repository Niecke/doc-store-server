from flask import Blueprint, session, request, redirect, url_for, render_template, flash
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
    }

@bp.route('/', methods=['GET', 'POST'])
@login_required
def index():
    username = session.get('username', 'Unknown')
    user = User.query.filter_by(username=username).first()
    return render_template('index.html' , current_user=user)


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        if user and verify_password(password=password, password_hash=user.password):
            session['user_id'] = user.id
            session['username'] = user.username
            return redirect(url_for('main.index'))
        else:
            flash('Invalid username or password')
    
    return render_template('login.html')

@bp.route('/logout', methods=['POST', 'GET'])
def logout():
    session.clear()
    flash('Logged out successfully')
    return redirect(url_for('main.index'))
