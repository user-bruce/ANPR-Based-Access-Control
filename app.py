from imp import reload
from flask import Flask, redirect, session, render_template, Response, request, url_for
import cv2
from flask_sqlalchemy import SQLAlchemy
from forms import LoginForm
from wtforms import ValidationError
from flask_bcrypt import Bcrypt

#Initialize te application and secret key for form processing
app = Flask(__name__)
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
camera = cv2.VideoCapture(0)

#App configuration
app.config['SECRET_KEY'] = 'AD058365832F3657'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
db.init_app(app)

#User model 
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False)
    password = db.Column(db.String(80), nullable=False)


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


'''
# Adding routes for navigation
'''
@app.route('/')
@app.route('/login', methods=('GET','POST'))
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

            #To replace the password with hashed password when able to add new user
            hashed_password = bcrypt.generate_password_hash(form.password.data)
            new_user = User(username=form.username.data, password=password)
            print(new_user)
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('dashboard'))

    return render_template('home.html', error=error, form=form)


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

@app.route('/reports')
def reports_page():

    #The error variales
    date_error = None
    return render_template('reports.html', error=date_error)

@app.route('/users')
def users_page():
    return render_template('users-list.html')

@app.route('/add-user')
def add_user_page():
    return render_template('add-user.html')


#Run the main application
if __name__ == '__main__':
    app.run(use_reload=True)
