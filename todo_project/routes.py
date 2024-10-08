from flask import render_template, url_for, flash, redirect, request
from todo_project import app, db, bcrypt
from todo_project.forms import (LoginForm, RegistrationForm, UpdateUserInfoForm, 
                                UpdateUserPassword, TaskForm, UpdateTaskForm)
from todo_project.models import User, Task
from flask_login import login_required, current_user, login_user, logout_user
from flask import Flask, make_response


# 1. Adicionando a política CSP com restrição de form-action e fontes externas específicas
@app.after_request
def apply_csp(response):
    response.headers['Content-Security-Policy'] = (
        "default-src 'self'; "
        "script-src 'self' https://code.jquery.com; "
        "style-src 'self' https://stackpath.bootstrapcdn.com; "
        "form-action 'self'; "  # Restringir envio de formulários à mesma origem
        "frame-ancestors 'none'; "
    )
    return response

# 2. Removendo a divulgação da versão do servidor
@app.after_request
def apply_security_headers(response):
    # Content-Security-Policy
    response.headers['Content-Security-Policy'] = (
        "default-src 'self'; "
        "script-src 'self' https://code.jquery.com; "
        "style-src 'self' https://stackpath.bootstrapcdn.com; "
        "form-action 'self'; "  # Restringir envio de formulários à mesma origem
        "frame-ancestors 'none'; "
    )
    response.headers['Permissions-Policy'] = "camera=(), microphone=(), geolocation=()"  # Ajuste conforme necessário
    return response

# 3. Configurando SameSite para cookies
@app.after_request
def set_samesite_cookie(response):
    if 'Set-Cookie' in response.headers:
        cookies = response.headers.getlist('Set-Cookie')
        response.headers['Set-Cookie'] = [cookie.replace('Set-Cookie:', 'Set-Cookie: SameSite=Lax;') for cookie in cookies]
    return response

# 4. Personalizando página de erro 500
@app.errorhandler(500)
def error_500(error):
    return render_template('errors/500.html'), 500

# Error Handlers
@app.errorhandler(404)
def error_404(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(403)
def error_403(error):
    return render_template('errors/403.html'), 403

@app.errorhandler(500)
def error_500(error):
    return render_template('errors/500.html'), 500

@app.errorhandler(Exception)
def handle_exception(e):
    # Retornar uma página de erro genérica para todas as exceções não tratadas
    return render_template("errors/generic.html", message="An unexpected error occurred"), 500

# Home and About
@app.route("/")
@app.route("/about")
def about():
    return render_template('about.html', title='About')


# User Authentication Routes
@app.route("/login", methods=['POST', 'GET'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('all_tasks'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            flash('Login Successful', 'success')
            return redirect(url_for('all_tasks'))
        else:
            flash('Login Unsuccessful. Please check Username or Password', 'danger')

    return render_template('login.html', title='Login', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route("/register", methods=['POST', 'GET'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('all_tasks'))

    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f'Account Created For {form.username.data}', 'success')
        return redirect(url_for('login'))

    return render_template('register.html', title='Register', form=form)


# Task Routes
@app.route("/all_tasks")
@login_required
def all_tasks():
    tasks = Task.query.filter_by(user_id=current_user.id).all()
    return render_template('all_tasks.html', title='All Tasks', tasks=tasks)


@app.route("/add_task", methods=['POST', 'GET'])
@login_required
def add_task():
    form = TaskForm()
    if form.validate_on_submit():
        task = Task(content=form.task_name.data, author=current_user)
        db.session.add(task)
        db.session.commit()
        flash('Task Created', 'success')
        return redirect(url_for('all_tasks'))
    return render_template('add_task.html', form=form, title='Add Task')


@app.route("/all_tasks/<int:task_id>/update_task", methods=['GET', 'POST'])
@login_required
def update_task(task_id):
    task = Task.query.get_or_404(task_id)
    form = UpdateTaskForm()
    if form.validate_on_submit():
        if form.task_name.data != task.content:
            task.content = form.task_name.data
            db.session.commit()
            flash('Task Updated', 'success')
            return redirect(url_for('all_tasks'))
        else:
            flash('No Changes Made', 'warning')
            return redirect(url_for('all_tasks'))
    elif request.method == 'GET':
        form.task_name.data = task.content
    return render_template('add_task.html', title='Update Task', form=form)


@app.route("/all_tasks/<int:task_id>/delete_task")
@login_required
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    flash('Task Deleted', 'info')
    return redirect(url_for('all_tasks'))


# Account Routes
@app.route("/account", methods=['POST', 'GET'])
@login_required
def account():
    form = UpdateUserInfoForm()
    if form.validate_on_submit():
        if form.username.data != current_user.username:
            current_user.username = form.username.data
            db.session.commit()
            flash('Username Updated Successfully', 'success')
            return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username

    return render_template('account.html', title='Account Settings', form=form)


@app.route("/account/change_password", methods=['POST', 'GET'])
@login_required
def change_password():
    form = UpdateUserPassword()
    if form.validate_on_submit():
        if bcrypt.check_password_hash(current_user.password, form.old_password.data):
            current_user.password = bcrypt.generate_password_hash(form.new_password.data).decode('utf-8')
            db.session.commit()
            flash('Password Changed Successfully', 'success')
            return redirect(url_for('account'))
        else:
            flash('Please Enter Correct Password', 'danger')

    return render_template('change_password.html', title='Change Password', form=form)


# Search Tasks Route
@app.route("/search_tasks", methods=['GET'])
@login_required
def search_tasks():
    query = request.args.get('query')
    if query:
        tasks = Task.query.filter(Task.content.contains(query), Task.user_id == current_user.id).all()
    else:
        tasks = []
    return render_template('all_tasks.html', title='Search Results', tasks=tasks)
