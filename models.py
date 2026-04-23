from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone

db = SQLAlchemy()

# ================= USER =================
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(200))
    role = db.Column(db.String(20))

    # ✅ Store profile image as base64
    profile_pic = db.Column(db.Text)


# ================= JOB =================
class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    location = db.Column(db.String(200))


# ================= TASK =================
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))

    status = db.Column(db.String(50), default="Pending")

    # ✅ FIXED TIMEZONE ERROR
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    date = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    completed_at = db.Column(db.DateTime)

    assigned_to = db.Column(db.Integer, db.ForeignKey('user.id'))
    job_id = db.Column(db.Integer, db.ForeignKey('job.id'))

    image = db.Column(db.String(200))
    report = db.Column(db.String(200))
    
    #=======material=======
class Material(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    quantity = db.Column(db.Integer)
    cost = db.Column(db.Float)

    created_at = db.Column(db.DateTime, default=db.func.now())
    
class TaskMaterial(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    task_id = db.Column(db.Integer, db.ForeignKey('task.id'))
    material_id = db.Column(db.Integer, db.ForeignKey('material.id'))

    quantity_used = db.Column(db.Integer)
    
