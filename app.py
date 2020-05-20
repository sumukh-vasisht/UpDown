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
        # print(session['token'])
        return render_template('home.html')
    else:
        return redirect(url_for('login'))

@app.route('/login', methods=["GET","POST"])
def login():
    if 'token' not in session:
        message = ""
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            try:
                userData = auth.sign_in_with_email_and_password(username,password)
                userDetails = db.collection('users').document(username).get().to_dict()
                print(userDetails)
                session['name'] = userDetails['name']
                session['email'] = userDetails['email']
                session['college'] = userDetails['college']
                session['token'] = userData['idToken']
                print(dict(session))
                return redirect('/')
            except Exception as e:
                error = ""
                error = json.loads(e.args[1])['error']['message']
                message = error.replace('_',' ')
        return render_template('login.html',message=message)
    else:
        return redirect('/')

@app.route('/logout')
def logout():
    if 'token' in session:
        session.pop('token')
        session.pop('name')
        session.pop('email')
        session.pop('college')
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
        userData = auth.sign_in_with_email_and_password(email,password) 
        session['name'] = username
        session['email'] = email
        session['college'] = college
        session['token'] = userData['idToken']
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
            <p>Regards,<br/>
            <p>Admin,<br/>
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
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/upload')
def upload():
    if 'token' in session:
        if request.method == "POST":
            branch = request.form['branch']
            sem = request.form['semester']
            files = request.files
        return render_template('upload.html')

@app.route('/download')
def download():
    return render_template('download.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if 'token' in session:
        if request.method == 'POST':
            name = session['name']
            email = session['email']
            subject = request.form['subject']
            sendQueryAckToUser(email, name)
            sendQueryToAdmin(email, subject)
            flash('Query submitted! We will get in touch with you shortly.')
            return render_template('contact.html')
        return render_template('contact.html')
    else:
        return redirect(url_for('login'))

if __name__ == '__main__':
   app.run(debug = True)
