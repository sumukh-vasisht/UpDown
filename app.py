from flask import Flask, render_template, request, redirect
import firebase_admin as firebase

cred = firebase.credentials.Certificate("firebaseKey.json")
firebase_admin.initialize_app(cred)
app = Flask(__name__)

@app.route('/')
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        print(username, password)
        return render_template('home.html')
    return render_template('login.html')

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

@app.route('/home')
def home():
    return render_template('home.html')

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
   init_db()
