from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from sqlalchemy import text
from flask import session, request, redirect, url_for, render_template, flash
from flask_migrate import Migrate
import os
import logging
import sys

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
# PyMySQL connection string
app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{os.getenv('MYSQL_USER')}:{os.getenv('MYSQL_PASSWORD')}@{os.getenv('MYSQL_HOST')}:{os.getenv('MYSQL_PORT')}/{os.getenv('MYSQL_DB')}?ssl_disabled=0&client_flag=4"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_pre_ping': True,
    'pool_recycle': 3600,  # Recycle every hour
    'pool_timeout': 30,
    'pool_size': 5,
    'max_overflow': 10
}


from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

# Global hasher instance
password_hasher = PasswordHasher(
    time_cost=2,      # iterations (balance between security/speed)
    memory_cost=65536, # memory usage (makes GPU attacks expensive)
    parallelism=4     # CPU threads
)

# Hash password
def hash_password(password):
    return password_hasher.hash(password)

# Verify password
def verify_password(password, password_hash):
    try:
        password_hasher.verify(password_hash, password)
        # Rehash if parameters changed (future-proof)
        if password_hasher.check_needs_rehash(password_hash):
            return hash_password(password)
        return True
    except VerifyMismatchError:
        return False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Clear default handlers
app.logger.handlers.clear()

# Add stdout handler
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
handler.setFormatter(formatter)
app.logger.addHandler(handler)
app.logger.setLevel(logging.INFO)

def ping_db():
    try:
        db.session.execute(text("SELECT 1"))
        app.logger.debug("Database connected!")
        return True
    except:
        app.logger.error("No connection to the database!")
        return False

# Models (same as before)
roles_users = db.Table('roles_users',
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('role.id'))
)

class Role(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

class User(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    active = db.Column(db.Boolean())
    roles = db.relationship('Role', secondary=roles_users, backref=db.backref('users', lazy='dynamic'))


# Simple session-based auth decorator
def login_required(f):
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function


@app.route('/health')
def health():
    is_connected = ping_db()
    return {
        'status': 'healthy' if is_connected else 'unhealthy',
        'database': 'connected' if is_connected else 'disconnected',
        'authenticated': 'user_id' in session,
        'username': session.get('username')
    }

@app.route('/')
def hello():
    return jsonify({'message': 'Doc Store API v3 - Flask-Security + PyMySQL'})

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        app.logger.info(f"user.password : {user.password}")
        app.logger.info(f"password : {password}")
        if user and verify_password(password=password, password_hash=user.password):
            session['user_id'] = user.id
            session['username'] = user.username
            app.logger.info(f"User {username} logged in")
            return redirect(url_for('protected'))
        else:
            app.logger.warning(f"Failed login for {username}")
            flash('Invalid username or password')
    
    return render_template('login.html')

@app.route('/logout', methods=['POST', 'GET'])
def logout():
    if 'user_id' in session:
        app.logger.info(f"User {session.get('username')} logged out")
    session.clear()
    flash('Logged out successfully')
    return redirect(url_for('hello'))

@app.route('/protected')
@login_required
def protected():
    username = session.get('username', 'Unknown')
    user = User.query.filter_by(username=username).first()
    return jsonify({
        'message': f'Hello {user.username}!', 
        'roles': [r.name for r in user.roles]  # Add roles query if needed
    })
