from flask import Flask, render_template, request, redirect, session, url_for, flash, send_file, send_from_directory
import json

from datetime import timedelta
import time
import pyrebase
import firebase_admin as firebase
from firebase_admin import firestore, storage
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os

if os.name == 'nt':
    cred = firebase.credentials.Certificate("firebaseKey.json")
    keyFile = open('pyrebaseKey.json','r')
    keyJson = keyFile.read()
    key = json.loads(keyJson)
else:
    cred = firebase.credentials.Certificate(json.loads(os.environ.get('FIREBASE')))
    key = json.loads(os.environ.get('PYREBASE'))

firebase.initialize_app(cred,{'storageBucket':'updown-nie.appspot.com'})
db = firestore.client() #USE FOR DATABASE
bucket = storage.bucket()
auth = pyrebase.initialize_app(key).auth() #USE FOR AUTHENTICATION
app = Flask(__name__)
app.secret_key = "(TIJUUV_DBOOPU_DPEF)-1" #Sunuffabich

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
        <p>Thank you for contacting us!<br/>
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

def allowed(filename):
    allowed_extensions = ['PDF','pdf']
    strList = filename.split('.')
    if len(strList) == 2 and strList[1] in allowed_extensions:
        return True
    return False

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

@app.route('/upload',methods=['GET','POST'])
def upload():
    if 'token' in session:
        message = ""
        if request.method == "POST":
            branch = request.form['branch']
            sem = request.form['semester']
            files = request.files.getlist('file')
            invalids = []
            for f in files:
                if allowed(f.filename):
                    blob = bucket.blob(f'{branch}/{sem}/{f.filename}')
                    blob.upload_from_file(f)
                else:
                    invalids.append(f.filename)
            if len(invalids)>0:
                message = "The following files have invalid extensions. "+', '.join(invalids) + ". The only allowed extension is pdf."
            else:
                message = "All files uploaded successfully"
        return render_template('upload.html', message = message)
    else: 
        return redirect(url_for('login'))

@app.route('/download',methods=["GET","POST"])
def download():
    if request.method == "POST":
        branch = request.form['branch']
        sem = request.form['semester']
        return redirect(f'/files/{branch}/{sem}')
    return render_template('download.html')

@app.route('/files/<branch>/<sem>')
def files(branch, sem):
    files = bucket.list_blobs(prefix=f'{branch}/{sem}')
    filenames = []
    for f in files:
        print(f.name)
        # name = f.name.split('/')[2]
        filenames.append(f.name)
        # string = f.download_as_string()
        # pdfFileObj = open(f'{name}', 'wb')
        # pdfFileObj.write(string)
        # pdfFileObj.close()
    return render_template('files.html',files=filenames)
        
@app.route('/files/<branch>/<sem>/<fileName>')
def downloadFile(branch, sem, fileName):
    files = bucket.list_blobs(prefix=f'{branch}/{sem}/{fileName}')
    for f in files:
        string = f.download_as_string()
        pdfFileObj = open(f'/tmp/{fileName}', 'wb')
        pdfFileObj.write(string)
        pdfFileObj.close()
        send_file(f'/tmp/{fileName}',fileName,as_attachment=True)
    return redirect(f'/files/{branch}/{sem}')

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
