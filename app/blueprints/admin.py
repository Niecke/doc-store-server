from flask import Blueprint, render_template, request, flash, redirect, url_for
from models import db, User
from security import login_required, require_role
from current_user import current_user

admin = Blueprint('admin', __name__)

@admin.route('/admin/dashboard', methods=['GET', 'POST'])
@login_required
@require_role('admin')
def dashboard():
    users = User.query.all()
    return render_template('admin/dashboard.html' , current_user=current_user, users=users)


@admin.route('/admin/user_create', methods=['GET', 'POST'])
@login_required
@require_role('admin')
def user_create():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        active = 'active' in request.form
        
        # Check if user exists
        if User.query.filter((User.email == email)).first():
            flash('EMail or email already exists!', 'error')
            return render_template('admin/user_create.html', current_user=current_user,)
        
        # Create user
        user = User(
            email=email,
            active=active,
        )
        user.set_password(password)  # Your password hash method
        
        db.session.add(user)
        db.session.commit()
        
        flash(f'User "{email}" created successfully!', 'success')
        return redirect(url_for('admin.dashboard'))
    
    return render_template('admin/user_create.html', current_user=current_user,)



@admin.route('/admin/user_edit', methods=['GET', 'POST'])
@login_required
@require_role('admin')
def user_edit():
    return ""


@admin.route('/admin/user_delete', methods=['GET', 'POST'])
@login_required
@require_role('admin')
def user_delete():
    return ""
