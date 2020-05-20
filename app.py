from flask import Flask, render_template, request, redirect, session
import json
from datetime import timedelta
import time
import pyrebase
import firebase_admin as firebase
from firebase_admin import firestore
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders


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
        senderAddress = "updown.updown.website@gmail.com"
        senderPassword = "Updown123"
        server = 'smtp.gmail.com:587'
        recieverAddress = email
        text = """
        Dear %s,

        Thank you for signing up at UP-DOWN!
        You can upload the resources you have and download those uploaded by others!
        Happy Learning!

        Regards,
        Admin,
        UP-DOWN
        """ %username

        html = """
        <html>

        <head>
        </head>

        <body>
            <p>Dear %s,</p>
            <p>Thank you for signing up at UP-DOWN!<br/>
            You can upload the resources you have and download those uploaded by others!<br/>
            Happy Learning!</p><br/>
            <p>Regards,</p><br/>
            <p>Admin,</p><br/>
            <p>UP-DOWN</p>
        </body>

        </html>
        """ %username

        message = MIMEMultipart("alternative", None, [MIMEText(text), MIMEText(html,'html')])
        message['Subject'] = "UP-DOWN | Sign-Up"
        message['From'] = senderAddress
        message['To'] = recieverAddress
        server = smtplib.SMTP(server)
        server.ehlo()
        server.starttls()
        server.login(senderAddress, senderPassword)
        server.sendmail(senderAddress, recieverAddress, message.as_string())
        print('Email Sent')
        server.quit()

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
