from flask import Blueprint, jsonify
from models import Task

api = Blueprint('api', __name__)

@api.route('/api/tasks')
def get_tasks():
    tasks = Task.query.all()
    return jsonify([{
        "id": t.id,
        "title": t.title,
        "status": t.status
    } for t in tasks])