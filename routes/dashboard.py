from flask import Blueprint, render_template, request, redirect, session, flash
from models import db, Task
from werkzeug.utils import secure_filename
import os
from flask import current_app

dash = Blueprint('dash', __name__)

@dash.route('/')
def dashboard():
    if 'user_id' not in session:
        return redirect('/login')

    tasks = Task.query.all()
    completed = Task.query.filter_by(status='Completed').count()
    pending = Task.query.filter_by(status='Pending').count()

    return render_template('dashboard.html', tasks=tasks, completed=completed, pending=pending)

@dash.route('/add_task', methods=['POST'])
def add_task():
    if session.get('role') != 'admin':
        flash("Unauthorized")
        return redirect('/')

    task = Task(title=request.form['title'])
    db.session.add(task)
    db.session.commit()
    return redirect('/')

@dash.route('/update_task/<int:id>')
def update_task(id):
    task = Task.query.get_or_404(id)
    task.status = 'Completed'
    db.session.commit()
    return redirect('/')

@dash.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    filename = secure_filename(file.filename)
    path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    file.save(path)
    flash("Uploaded")
    return redirect('/')