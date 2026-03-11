from flask import Blueprint, render_template, request, flash, redirect, url_for
from sqlalchemy import select
from models import db, User
from security import login_required, require_role

admin = Blueprint('admin', __name__)

@admin.route('/admin/dashboard', methods=['GET', 'POST'])
@login_required
@require_role('admin')
def dashboard():
    users = db.session.execute(select(User)).scalars().all()
    return render_template('admin/dashboard.html', users=users)


@admin.route('/admin/user_create', methods=['GET', 'POST'])
@login_required
@require_role('admin')
def user_create():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        active = 'active' in request.form
        
        # Check if user exists
        if db.session.execute(select(User).where(User.email == email)).scalar_one_or_none():
            flash('EMail already exists!', 'error')
            return render_template('admin/user_create.html')
        
        user = User(
            email=email,
            active=active,
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        flash(f'User "{email}" created successfully!', 'success')
        return redirect(url_for('admin.dashboard'))
    
    return render_template('admin/user_create.html')



@admin.route('/admin/user_edit/<int:id>', methods=['GET', 'POST'])
@login_required
@require_role('admin')
def user_edit(id):
    flash(f'Not implemented yet', 'error')
    return redirect(url_for('admin.dashboard'))



@admin.route('/admin/user_delete/<int:id>', methods=['GET'])
@login_required
@require_role('admin')
def user_delete(id):
    user = db.session.get(User, id)

    if not user:
        flash(f'User ID "{id}" unknown!', 'error')
        return redirect(url_for('admin.dashboard'))

    if user.email == "admin":
        flash(f'The internal admin user can not be deleted!', 'error')
        return redirect(url_for('admin.dashboard'))

    db.session.delete(user)
    db.session.commit()

    flash(f'User "{user.email}" deleted!', 'success')
    return redirect(url_for('admin.dashboard'))