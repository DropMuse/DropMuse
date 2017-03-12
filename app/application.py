from flask import Flask, render_template, request, redirect, url_for, flash
import pymysql
from settings import (MYSQL_USER, MYSQL_PASS, MYSQL_HOST, MYSQL_PORT, MYSQL_DB,
                      SECRET_KEY)
from forms import RegistrationForm, LoginForm

app = Flask(__name__)
app.secret_key = SECRET_KEY

conn = pymysql.connect(host=MYSQL_HOST,
                       user=MYSQL_USER,
                       password=MYSQL_PASS,
                       port=int(MYSQL_PORT),
                       db=MYSQL_DB,
                       charset='utf8mb4',
                       cursorclass=pymysql.cursors.DictCursor)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm(request.form)
    if request.method == 'POST' and form.validate():
        # TODO: Create user
        flash('Thanks for registering', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        # TODO: Validate user login
        flash('You have been logged in.')
        return redirect(url_for('profile'))
    return render_template('login.html', form=form)


@app.route('/profile')
def profile():
    return render_template('profile.html')
