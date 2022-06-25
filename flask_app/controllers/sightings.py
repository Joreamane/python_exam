from flask_app import app
from flask import render_template, redirect, request, session, flash
from flask_app.models.user import User
from flask_app.models.sighting import Sighting
from flask_bcrypt import Bcrypt
bcrypt = Bcrypt(app)

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    data = {'id':session['user_id']}
    return render_template('dashboard.html', user = User.get_user(data), all_sightings = Sighting.get_all_sightings_with_creator(), believers = Sighting.get_total_believers())

@app.route('/register', methods=['post'])
def register():
    pw_hash = bcrypt.generate_password_hash(request.form['password'])
    print(pw_hash)
    data = {
        'first_name': request.form['fname'],
        'last_name': request.form['lname'],
        'email': request.form['email'],
        'password': pw_hash,
    }
    if not User.validate_registration(request.form):
        return redirect('/')
    user_id = User.add_user(data)
    session['user_id'] = user_id
    session['first_name'] = data['first_name']
    session['last_name'] = data['last_name']
    return redirect('/dashboard')

@app.route('/login', methods=['post'])
def login():
    data = {'email': request.form['loginemail']}
    user_in_db = User.get_by_email(data)
    if not user_in_db:
        flash('Email does not have an associated account.', 'login')
        return redirect('/')
    if not bcrypt.check_password_hash(user_in_db.password, request.form['loginpassword']):
        flash('Invalid email/password combination.', 'login')
        return redirect('/')
    session['user_id'] = user_in_db.id
    session['first_name'] = user_in_db.first_name
    session['last_name'] = user_in_db.last_name
    return redirect('/dashboard')

@app.route('/logout', methods=['get', 'post'])
def logout():
    session.clear()
    return redirect('/')

@app.route('/create_sighting')
def create_page():
    data = {'id': session['user_id']}
    return render_template('/create.html', user=User.get_user(data))

@app.route('/create', methods=['post'])
def create_sighting():
    data = {
        'location': request.form['location'],
        'what_happened': request.form['what_happened'],
        'date': request.form['date'],
        'number': request.form['number'],
        'user_id': session['user_id']
    }
    if not Sighting.validate_sighting(data):
        return redirect('/create_sighting')
    Sighting.add_sighting(data)
    return redirect('/dashboard')

@app.route('/view_profile/<int:user_id>', methods = ['get'])
def view_profile(user_id):
    data = {
        'id' : session['user_id']
    }
    return render_template('profile.html', user = User.get_user(data), your_sightings = Sighting.get_sightings(data))

@app.route('/edit_page/<int:sighting_id>', methods = ['get'])
def edit_page(sighting_id):
    data= {'id' : sighting_id}
    return render_template('edit.html', sighting= Sighting.get_one(data))

@app.route('/edit/<int:sighting_id>', methods=['post'])
def edit_sighting(sighting_id):
    print(request.form)
    data = {
        'id' : sighting_id,
        'location': request.form['location'],
        'what_happened': request.form['what_happened'],
        'date': request.form['date'],
        'number': request.form['number']
    }
    if not Sighting.validate_sighting(data):
        return redirect('/edit_page/<int:sighting_id>')
    Sighting.update_sighting(data)
    flash('Sighting successfully updated!', 'sighting')
    return redirect('/dashboard')

@app.route('/delete/<int:sighting_id>', methods=['get'])
def delete_sighting(sighting_id):
    data = {
        'id': sighting_id
    }
    Sighting.delete_sighting(data)
    return redirect('/dashboard')

@app.route('/view_sighting/<int:sighting_id>', methods=['get'])
def view_sighting(sighting_id):
    data = {
        'id' : sighting_id
    }
    return render_template('sighting.html', sighting = Sighting.get_one(data))

@app.route('/skeptic/<int:sighting_id>', methods=['get','post'])
def become_skeptic(sighting_id):
    data = {
        'sighting_id' : sighting_id,
        'user_id' : session['user_id']
    }
    Sighting.add_skeptic(data)
    return redirect('/dashboard')

@app.route('/believer/<int:sighting_id>', methods=['get','post'])
def become_believer(sighting_id):
    data = {
        'sighting_id' : sighting_id,
        'user_id' : session['user_id']
    }
    Sighting.add_believer(data)
    return redirect('/dashboard')