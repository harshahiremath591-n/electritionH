from flask import Blueprint, render_template, request, redirect, session, flash
from models import db, User
from werkzeug.security import generate_password_hash, check_password_hash

auth = Blueprint('auth', __name__)

@auth.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        user = User(
            username=request.form['username'],
            password=generate_password_hash(request.form['password']),
            role=request.form['role']
        )
        db.session.add(user)
        db.session.commit()
        flash("Registered")
        return redirect('/login')
    return render_template('register.html')

@auth.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and check_password_hash(user.password, request.form['password']):
            session['user_id'] = user.id
            session['role'] = user.role
            return redirect('/')
        flash("Invalid login")
    return render_template('login.html')

@auth.route('/logout')
def logout():
    session.clear()
    return redirect('/login')