from flask import Flask, render_template, request, redirect, session
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
    app .permanent_session_lifetime = timedelta(seconds=20)

@app.route('/')
def home():
    print("#")
    print(session['token'])
    return render_template('home.html')

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
    return "HELLO"

@app.route('/register')
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        college = request.form['college']
        password = request.form['pwd1']
        print(username, email, college, password)
        return render_template('home.html')
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
