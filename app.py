from flask import Flask, render_template, request, redirect, session, url_for, flash
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

def sendQueryAckToUser(email, name):
    senderAddress = "updown.updown.website@gmail.com"
    senderPassword = "Updown123"
    server = 'smtp.gmail.com:587'
    recieverAddress1 = email
    text1 = """
    Dear %s,
    Thank you for contacting us!
    We whave recieved your message/query!
    One of our teammates will get in tough with you shortly.
    Thanks & Regards,
    Admin,
    UP-DOWN
    """ %name
    html1 = """
    <html>
    <head>
    </head>
    <body>
        <p>Dear %s,</p>
        <p>Thank you for signing up at UP-DOWN!<br/>
        We whave recieved your message/query!<br/>
        One of our teammates will get in tough with you shortly.</p><br/>
        <p>Thanks & Regards,<br/>
        <p>Admin,<br/>
        <p>UP-DOWN</p>
    </body>
    </html>
    """ %name
    message = MIMEMultipart("alternative", None, [MIMEText(text1), MIMEText(html1,'html')])
    message['Subject'] = "UP-DOWN | Contact"
    message['From'] = senderAddress
    message['To'] = recieverAddress1
    server = smtplib.SMTP(server)
    server.ehlo()
    server.starttls()
    server.login(senderAddress, senderPassword)
    server.sendmail(senderAddress, recieverAddress1, message.as_string())
    print('Email to User Sent')
    server.quit()

def sendQueryToAdmin(email, subject):
    senderAddress = "updown.updown.website@gmail.com"
    senderPassword = "Updown123"
    server = 'smtp.gmail.com:587'
    recieverAddress2 = "updown.updown.website@gmail.com"
    text2 = """
    You have got a query!
    Sender : """ + email + """
    Subject : %s
    """  %subject
    html2 = """
    <html>
    <head>
    </head>
    <body>
        <p>You have recieved a query!<br/>
        Sender : """ + str(email) + """ <br/>
        Subject : %s</p><br/>
    </body>
    </html>
    """  %subject
    message = MIMEMultipart("alternative", None, [MIMEText(text2), MIMEText(html2,'html')])
    message['Subject'] = "UP-DOWN | Contact"
    message['From'] = senderAddress
    message['To'] = recieverAddress2
    server = smtplib.SMTP(server)
    server.ehlo()
    server.starttls()
    server.login(senderAddress, senderPassword)
    server.sendmail(senderAddress, recieverAddress2, message.as_string())
    print('Email to Admin Sent')
    server.quit()

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

@app.route('/register', methods=['GET', 'POST'])
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

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        subject = request.form['subject']
        sendQueryAckToUser(email, name)
        sendQueryToAdmin(email, subject)
        flash('Query submitted! We will get in touch with you shortly.')
        return render_template('contact.html')
    return render_template('contact.html')

if __name__ == '__main__':
   app.run(debug = True)
