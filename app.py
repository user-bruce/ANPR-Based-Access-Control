from enum import unique
from imp import reload
from multiprocessing import managers
from flask import Flask, flash, redirect, session, render_template, Response, request, url_for
import cv2
import numpy as np
from skimage.filters import threshold_local
import tensorflow as tf
from skimage import measure
import imutils
import string
import random
from flask_migrate import Migrate
from flask_login import (UserMixin,login_user,LoginManager,current_user,logout_user, login_required,)
from flask_sqlalchemy import SQLAlchemy
from forms import LoginForm, VehicleReportsForm,UserReportsForm,AddUserForm,ProfileForm
from flask_bcrypt import Bcrypt

from main import NeuralNetwork, PlateFinder


#Initialize te application and secret key for form processing
app = Flask(__name__)
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
migrate = Migrate()
camera = cv2.VideoCapture(0)


#Setup login variables
login_manager = LoginManager(app)
login_manager.session_protection = "strong"
login_manager.login_view = "login"
login_manager.login_message_category = "info"


#App configuration
app.config['SECRET_KEY'] = 'AD058365832F3657'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db.init_app(app)
migrate.init_app(app, db)

#User model 
class User(UserMixin, db.Model):

    __tablename__="Users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(20), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    role = db.Column(db.String(25), nullable=False)

    #Constructor
    def __init__(self, username, password, phone, role):
        self.username = username
        self.password = password
        self.phone = phone
        self.role = role

    #Print
    def __repr__(self):
        return '<User %r>' % self.username


#Vehicle model
class Vehicle(db.Model):

    __tablename__="vehicles"

    vehicle_id = db.Column(db.Integer, primary_key=True)
    vehicle_reg = db.Column(db.String(10), unique=True)
    img = db.Column(db.LargeBinary,nullable=True)



##Read camera function
def generate_frames():

    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg',frame)
            frame = buffer.tobytes()
        yield(b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

#Comment out this code if bugs
#Pass the video from webcam into neural network

#End of comment


#Load curent session user
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


'''
# Adding routes for navigation
'''
@app.route('/')
@app.route('/login', methods=['GET','POST'])
def home_page():
    form = LoginForm()
    error = None

    if request.method=='POST':
        

        username = request.form["username"]
        password = request.form["password"]
        
        if not username or not username.strip():
            error = 'Enter username'
        if not password or not password.strip():
            error = "Enter your password"
        if username and password:
            
            user = User.query.filter_by(username=username).first()
            print(user)

            if user:
                print(bcrypt.check_password_hash(user.password, password))
                print(bcrypt.generate_password_hash(password))
                print(user.password)
                if bcrypt.check_password_hash(user.password, password):
                    print('Logged in!...')
                    login_user(user)
                    return redirect(url_for('dashboard'))
            

    return render_template('home.html', error=error, form=form)


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    logout()
    return redirect(url_for('login'))


@app.route('/user-reports', methods=['GET','POST'])
def reports_page():
    user_form = UserReportsForm()
    user_date_error = None
    
    if request.method =='POST':
        from_date = request.form['dtlPicker1']
        to_date = request.form['dtlPicker2']

        if not from_date or not to_date:
            user_date_error = 'Please fill all fields'

        if from_date and to_date:
            print(from_date)
            print(to_date)
            return redirect(url_for('account_page'))
    return render_template('reports.html', error=user_date_error,  user_form=user_form)


@app.route('/vehicle-reports', methods=['GET','POST'])
def vehicles_reports():
    vehicles_form = VehicleReportsForm()
    vehicles_date_error = None

    if request.method =='POST':
        from_date = request.form['dtlPicker1']
        to_date = request.form['dtlPicker2']

        if not from_date or not to_date:
            vehicles_date_error = 'Please fill all fields'

        if from_date and to_date:
            print(to_date)
            print(from_date)
            return redirect(url_for('account_page'))
    return render_template('reports.html', error=vehicles_date_error, vehicles_form=vehicles_form)

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/video')
def video():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/vehicles')
def vehicles():
    return render_template('vehicles.html')

@app.route('/account')
def account_page():
    return render_template('account.html')

@app.route('/users')
def users_page():
    return render_template('users-list.html')

@app.route('/add-user', methods=['GET','POST'])
def add_user_page():
    form = AddUserForm()
    username_error = None
    phone_error = None
    password_length = 10
    role=None

    if request.method =='POST':
        username = request.form['username']
        phone = request.form['phone']

        if not phone:
            phone_error = 'Please add a phone number'
        if not username:
            username_error = 'Please enter a user name'
        if phone and username:
            if request.form.get("admin-check"):
                role='admin'
            else:
                role='non-admin'

            password = (''.join(random.choices(string.ascii_uppercase + string.digits, k = password_length)))
            print(password)
            hashed_password = bcrypt.generate_password_hash(password)

            user = User(username=username,password=hashed_password,phone=phone, role=role )
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('account_page'))
    return render_template('add-user.html', form=form,username_error=username_error, phone_error=phone_error)

@app.route('/profile', methods=['GET', 'POST'])
def edit_profile():
    form = ProfileForm()
    username_error = None
    phone_error = None
    password_error = None

    if request.method == 'POST':
        username = request.form['username']
        phone = request.form['phone']
        password = request.form['password']

        if not username:
            username_error = 'Please enter a user name'

        if not phone:
            phone_error = 'Please add a phone number'

        if not password:
            password_error = 'Please add a phone number'

        if password and username and phone:
            print(username)
            print(password)
            print(phone)
            return redirect(url_for('account_page'))

    return render_template('edit-profile.html', form=form, username_error=username_error,phone_error = phone_error,password_error=password_error)


#Run the main application
if __name__ == '__main__':
    
    app.run(use_reload=True)
