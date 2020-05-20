from flask import Flask, render_template, request, redirect, session, url_for
import json
from datetime import timedelta
import time
import pyrebase
import firebase_admin as firebase
from firebase_admin import firestore

cred = firebase.credentials.Certificate("firebaseKey.json")
keyFile = open('pyrebaseKey.json','r')
keyJson = keyFile.read()
key = json.loads(keyJson)

firebase.initialize_app(cred)
db = firestore.client() #USE FOR DATABASE
auth = pyrebase.initialize_app(key).auth() #USE FOR AUTHENTICATION
app = Flask(__name__)
app.secret_key = "(TIJUUV_DBOOPU_DPEF)-1"

@app.before_request
def before_request():
    session.permanent = True
    app .permanent_session_lifetime = timedelta(minutes=10)

@app.route('/')
def home():
    if 'token' in session:
        print(session['token'])
        return render_template('home.html')
    else:
        return redirect(url_for('login'))

@app.route('/login', methods=["GET","POST"])
def login():
    message = ""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        try:
            userData = auth.sign_in_with_email_and_password(username,password)
            session['token'] = userData['idToken']
            return redirect('/')
        except Exception as e:
            error = ""
            error = json.loads(e.args[1])['error']['message']
            message = error.replace('_',' ')
    return render_template('login.html',message=message)

@app.route('/logout')
def logout():
    session.pop('token')
    return redirect(url_for('login'))

@app.route('/register')
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        # branch = request.form['branch']
        # semester = request.form['semester']
        college = request.form['college']
        password = request.form['pwd1']
        # print(username, email, college, password)
        auth.create_user_with_email_and_password(email,password)
        db.collection(u'users').document(email).set({
            'name':username,
            'email':email,
            # 'branch':branch,
            # 'semester':semester,
            'college':college
        })
        auth.send_email_verification(email)
        return redirect(url_for('login', message="Please Check Your Email"))
    return render_template('register.html')

@app.route('/upload')
def upload():
    return render_template('upload.html')

@app.route('/download')
def download():
    return render_template('download.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

if __name__ == '__main__':
   app.run(debug = True)
