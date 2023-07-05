from __future__ import unicode_literals, print_function, division
from flask import Flask, render_template, request, redirect, url_for,session
from requests.exceptions import HTTPError
import re
import pyrebase as db
import FrenchToEngModel as En
import EngToFrenchModel as Fr

config = {
       'apiKey': "AIzaSyCpd8DgcbgF49ZaZAkeGAZp40hHQrLh1bo",
       'authDomain': "babelbot-9969d.firebaseapp.com",
       'databaseURL': "https://babelbot-9969d-default-rtdb.asia-southeast1.firebasedatabase.app/",
       'projectId': "babelbot-9969d",
       'storageBucket': "babelbot-9969d.appspot.com",
       'messagingSenderId': "889837798586",
       'appId': "1:889837798586:web:1a5488c0b58ec752e4ee83",
       'measurementId': "G-5K2G1RGTT6"

}


firebase = db.initialize_app(config)
auth = firebase.auth()

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

def islogged_in():
    if 'user_id' in session:
        return True
    else:
        return False


@app.route('/')
def home():
    logged_in = islogged_in()
    return render_template('index.html', logged_in = logged_in)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        try:
            login = auth.sign_in_with_email_and_password(email, password)
            session['user_id'] = login['idToken']
            return redirect(url_for('home'))
        except:
            error = "Invalid email or Password"        
            return render_template('login.html', error = error)
            

    return render_template('login.html')

@app.route('/register', methods = ['GET','POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')
        c_password = request.form.get('confirm password')
    
        
        if not username:
            error = "please fill in all the required fields."
            return render_template('register.html', error = error)         
        email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'

        if not re.match(email_pattern, email):
            error = 'Invalid email format.'
            return render_template('register.html', error=error)
            

        password_pattern = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{6,}$"

        if not re.match(password_pattern, password):
            error = 'Password should contain at least 1 uppercase letter, 1 lowercase letter, 1 special character, and 1 number.'
            return render_template('register', error=error)
            
        try:
            user = auth.create_user_with_email_and_password(email, password)
        except HTTPError as e:
            if e.response is not None and e.response.content:
                error = e.response.json()['error']['message']
            else:
                error = 'An error occurred during registration.'
            return render_template('register.htm', error=error)

    return render_template('register.html')


@app.route('/translate')
def translate():
    logged_in = islogged_in()
    return render_template('translate.html', logged_in = logged_in)


@app.route('/translator', methods=['GET', 'POST'])
def translator():   
    try:
        sentence = request.form['text']
        opt = request.form['options']
        if opt == 'French':
            sentence = Fr.normalizeStringFra(sentence)
            output_words, _ = Fr.evaluateToFra(Fr.encoderEng, Fr.decoderFra, sentence, Fr.input_lang_eng, Fr.output_lang_fra)
        elif opt == 'English':
            sentence = En.normalizeString(sentence)
            output_words, _ = En.evaluateEng(En.encoder, En.decoder, sentence, En.input_lang, En.output_lang)
        output_sentence = ' '.join(output_words)
        return render_template('translate.html', in_sentence = sentence, translated_text = output_sentence)
    except KeyError:
       # Edit this and make it as a pop up form 
       return render_template('translate.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('home'))

@app.route('/MyAccount')
def MyAccount():
    return render_template('myAccount.html')

if __name__ == '__main__':
    app.run(debug=True)
    