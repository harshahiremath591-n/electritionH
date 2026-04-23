from flask import Flask, render_template, request, redirect, session, flash
from config import Config
from models import db, User, Task, Job, Material, TaskMaterial
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta, timezone

import os
import base64

app = Flask(__name__)
app.config.from_object(Config)

# ✅ INIT DB (ONLY ONCE)
db.init_app(app)

with app.app_context():
    db.create_all()

    if not User.query.first():
        db.session.add_all([
            User(username="admin", password=generate_password_hash("admin"), role="admin"),
            User(username="elec1", password=generate_password_hash("123"), role="electrician")
        ])
        db.session.commit()

# ================= HOME =================
@app.route('/')
def home():
    if session.get('user_id'):
        return redirect('/dashboard')
    return render_template('home.html')


# ================= LOGIN =================
@app.route('/login', methods=['GET','POST'])
def login():
    if session.get('user_id'):
        return redirect('/dashboard')

    if request.method == 'POST':
        user = User.query.filter_by(username=request.form.get('username')).first()

        if user and check_password_hash(user.password, request.form.get('password')):
            session['user_id'] = user.id
            session['role'] = user.role
            session['username'] = user.username
            return redirect('/dashboard')

        flash("❌ Invalid login")

    return render_template('login.html')


# ================= REGISTER =================
@app.route('/register', methods=['GET', 'POST'])
def register():
    if session.get('user_id'):
        return redirect('/dashboard')

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role')

        file = request.files.get('profile_pic')
        image_data = None

        if file and file.filename:
            image_data = base64.b64encode(file.read()).decode('utf-8')

        if not username or not password or not role:
            flash("⚠️ Fill all fields")
            return redirect('/register')

        if User.query.filter_by(username=username).first():
            flash("⚠️ User already exists")
            return redirect('/register')

        user = User(
            username=username,
            password=generate_password_hash(password),
            role=role,
            profile_pic=image_data
        )

        db.session.add(user)
        db.session.commit()

        flash("✅ Registered successfully")
        return redirect('/login')

    return render_template('register.html')


# ================= DASHBOARD =================
@app.route('/dashboard')
def dashboard():
    if not session.get('user_id'):
        return redirect('/login')

    if session['role'] == 'electrician':
        tasks = Task.query.filter_by(assigned_to=session['user_id']).all()
    else:
        tasks = Task.query.all()

    completed = Task.query.filter_by(status="Completed").count()
    pending = Task.query.filter_by(status="Pending").count()
    processing = Task.query.filter_by(status="Processing").count()

    return render_template('dashboard.html',
                           tasks=tasks,
                           completed=completed,
                           pending=pending,
                           processing=processing)


# ================= ADD TASK =================
@app.route('/add_task', methods=['GET', 'POST'])
def add_task():
    if not session.get('user_id'):
        return redirect('/login')

    if session.get('role') != 'admin':
        flash("⚠️ Only admin allowed")
        return redirect('/dashboard')

    electricians = User.query.filter_by(role='electrician').all()
    jobs = Job.query.all()

    if request.method == 'POST':
        title = request.form.get('title')
        user_id = request.form.get('user_id')
        job_id = request.form.get('job_id')

        if not title or not user_id or not job_id:
            flash("⚠️ Fill all fields")
            return redirect('/add_task')

        user = db.session.get(User, int(user_id))
        job = db.session.get(Job, int(job_id))

        if not user or user.role != 'electrician':
            flash("⚠️ Invalid electrician")
            return redirect('/add_task')

        if not job:
            flash("⚠️ Invalid job")
            return redirect('/add_task')

        task = Task(title=title, assigned_to=user.id, job_id=job.id, status="Pending")

        db.session.add(task)
        db.session.commit()

        flash("✅ Task Assigned")
        return redirect('/dashboard')

    return render_template('add_task.html', electricians=electricians, jobs=jobs)


# ================= JOBS =================
@app.route('/jobs', methods=['GET','POST'])
def jobs():
    if not session.get('user_id'):
        return redirect('/login')

    if request.method == 'POST':
        if session.get('role') != 'admin':
            flash("⚠️ Only admin can add jobs")
            return redirect('/jobs')

        job = Job(
            title=request.form.get('title'),
            location=request.form.get('location')
        )
        db.session.add(job)
        db.session.commit()

    jobs = Job.query.all()
    return render_template('jobs.html', jobs=jobs)


# ================= MATERIALS =================
@app.route('/materials', methods=['GET', 'POST'])
def materials():
    if not session.get('user_id'):
        return redirect('/login')

    if request.method == 'POST':
        if session.get('role') != 'admin':
            flash("⚠️ Only admin can add materials")
            return redirect('/materials')

        material = Material(
            name=request.form.get('name'),
            quantity=int(request.form.get('quantity')),
            cost=float(request.form.get('cost'))
        )

        db.session.add(material)
        db.session.commit()

        flash("✅ Material Added")

    materials = Material.query.all()
    return render_template('materials.html', materials=materials)

# ================= ASSIGN MATERIALS =================
@app.route('/assign_material/<int:task_id>', methods=['POST'])
def assign_material(task_id):
    if session.get('role') != 'admin':
        return redirect('/dashboard')

    material_id = int(request.form.get('material_id'))
    qty = int(request.form.get('quantity'))

    tm = TaskMaterial(
        task_id=task_id,
        material_id=material_id,
        quantity_used=qty
    )

    db.session.add(tm)
    db.session.commit()

    flash("✅ Material assigned to task")
    return redirect('/dashboard')

# ================= ELECTRICIANS =================
@app.route('/electricians')
def electricians():
    if not session.get('user_id'):
        return redirect('/login')

    users = User.query.filter_by(role='electrician').all()
    return render_template('electricians.html', users=users)


# ================= REPORTS =================
@app.route('/reports')
def reports():
    if not session.get('user_id'):
        return redirect('/login')

    now = datetime.now(timezone.utc)
    tasks = Task.query.filter(Task.created_at >= now - timedelta(days=30)).all()

    return render_template('reports.html', tasks=tasks)


# ================= UPDATE TASK =================
@app.route('/update/<int:id>', methods=['POST'])
def update(id):
    if not session.get('user_id'):
        return redirect('/login')

    task = db.session.get(Task, id)

    if not task:
        flash("Task not found")
        return redirect('/dashboard')

    # 🔒 Only electrician
    if session.get('role') != 'electrician':
        return redirect('/dashboard')

    # 🔒 Only assigned electrician
    if task.assigned_to != session.get('user_id'):
        return "Unauthorized", 403

    status = request.form.get('status')

    if status in ["Pending", "Processing", "Completed"]:
        task.status = status

        if status == "Completed":
            task.completed_at = datetime.now(timezone.utc)

            # ================= MATERIAL AUTO DEDUCT =================
            materials_used = TaskMaterial.query.filter_by(task_id=task.id).all()

            for item in materials_used:
                material = db.session.get(Material, item.material_id)

                if material:
                    material.quantity -= item.quantity_used

                    # ❗ LOW STOCK ALERT
                    if material.quantity < 5:
                        flash(f"⚠️ Low stock: {material.name}")

        else:
            task.completed_at = None

    # ================= REPORT UPLOAD =================
    file = request.files.get('report')

    if file and file.filename:
        path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(path)
        task.report = file.filename

    db.session.commit()
    flash("✅ Task updated")
    return redirect('/dashboard')


# ================= PROFILE =================
@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if not session.get('user_id'):
        return redirect('/login')

    user = db.session.get(User, session['user_id'])

    if request.method == 'POST':
        if request.form.get('username'):
            user.username = request.form.get('username')
            session['username'] = user.username

        if request.form.get('password'):
            user.password = generate_password_hash(request.form.get('password'))

        file = request.files.get('profile_pic')
        if file and file.filename:
            user.profile_pic = base64.b64encode(file.read()).decode('utf-8')

        db.session.commit()
        flash("✅ Profile updated")
        return redirect('/profile')

    return render_template('profile.html', user=user)


# ================= GLOBAL USER =================
@app.context_processor
def inject_user():
    if session.get('user_id'):
        return dict(user=db.session.get(User, session['user_id']))
    return dict(user=None)


# ================= ERRORS =================
@app.errorhandler(404)
def not_found(e):
    return render_template("error.html", msg="404 Page Not Found"), 404

@app.errorhandler(500)
def server_error(e):
    return render_template("error.html", msg="500 Server Error"), 500


# ================= LOGOUT =================
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')


# ================= RUN =================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)