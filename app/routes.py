from flask import Blueprint, session, request, redirect, url_for, render_template, flash
from models import db, User
from sqlalchemy import text
from password_handler import verify_password
from security import login_required
from current_user import current_user

bp = Blueprint('main', __name__)

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
    return render_template('index.html' , current_user=current_user)


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        if user and verify_password(password=password, password_hash=user.password):
            session['user_id'] = user.id
            session['email'] = user.email
            return redirect(url_for('main.index'))
        else:
            flash('Invalid email or password')
    
    return render_template('login.html')

@bp.route('/logout', methods=['POST', 'GET'])
def logout():
    session.clear()
    flash('Logged out successfully')
    return redirect(url_for('main.index'))
