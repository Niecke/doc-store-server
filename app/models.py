from flask_sqlalchemy import SQLAlchemy
from password_handler import hash_password, password_hasher
from argon2.exceptions import VerifyMismatchError
from config import MIN_PASSWORD_LENGTH

db = SQLAlchemy()

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
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    active = db.Column(db.Boolean())
    roles = db.relationship('Role', secondary=roles_users, backref=db.backref('users', lazy='dynamic'))

    def is_authenticated(self):
        """Returns True if user is active"""
        return self.active
    
    def set_password(self, password):
        if len(password) < MIN_PASSWORD_LENGTH:
            raise ValueError(f"Password needs to be longer than {MIN_PASSWORD_LENGTH}")
        self.password = hash_password(password)

    def verify_password(self, password):
        try:
            password_hasher.verify(self.password, password)
        except VerifyMismatchError:
            return False
        if password_hasher.check_needs_rehash(self.password):
            self.set_password(password)
            db.session.commit()
        return True