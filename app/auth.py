# auth.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app as app, Response
from flask_login import login_user, logout_user, login_required, current_user
from .models import db, User
import os

auth = Blueprint('auth', __name__)

def render_template_with_paths(template_name, **context):
    template_path = os.path.join(os.getcwd(), 'templates', template_name)
    css_path = url_for('static', filename='css/signin_styles.css')
    print(f"Rendering {template_name} from: {template_path}")
    print(f"CSS path: {css_path}")
    try:
        with open(template_path) as file:
            content = file.read()
        # Manually inject the paths into the content
        content = content.replace('{{ css_path }}', css_path)
        for key, value in context.items():
            content = content.replace(f'{{{{ {key} }}}}', value)
        return Response(content, mimetype='text/html')
    except Exception as e:
        print(f"Error rendering {template_name}: {e}")
        return str(e)

@auth.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('index'))
        flash('Invalid username or password')
    return render_template_with_paths('signin.html', sign_in_url=url_for('auth.signin'), change_password_url=url_for('auth.change_password'))

@auth.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.signin'))

@auth.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        old_password = request.form['old_password']
        new_password = request.form['new_password']
        if current_user.check_password(old_password):
            current_user.set_password(new_password)
            db.session.commit()
            flash('Password changed successfully')
            return redirect(url_for('index'))
        else:
            flash('Old password is incorrect')
    return render_template_with_paths('change_password.html', change_password_url=url_for('auth.change_password'))
