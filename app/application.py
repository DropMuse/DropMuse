from flask import Flask, render_template, request, redirect, url_for, flash
import sqlalchemy
from sqlalchemy import create_engine
from settings import (DB_USER, DB_PASS, DB_HOST, DB_PORT, DB_DBNAME,
                      DB_PREFIX, SECRET_KEY)
from forms import RegistrationForm, LoginForm
import db_utils

app = Flask(__name__)
app.secret_key = SECRET_KEY
conn_str = "{}{}:{}@{}:{}/{}".format(DB_PREFIX,
                                     DB_USER,
                                     DB_PASS,
                                     DB_HOST,
                                     DB_PORT,
                                     DB_DBNAME)
print("Connecting to {}".format(conn_str))
engine = create_engine(conn_str)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm(request.form)
    if form.validate_on_submit():
        # Check to make sure username not taken
        if db_utils.user_exists(engine, form.username.data):
            flash('Username already taken.', 'error')
            return redirect(url_for('register'))
        # Create user
        else:
            db_utils.create_user(engine,
                                 form.username.data,
                                 form.password.data,
                                 form.email.data)
            flash('Thanks for registering', 'success')
            return redirect(url_for('login'))
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if form.validate_on_submit():
        # Validate user login
        if db_utils.validate_password(engine,
                                      form.username.data,
                                      form.password.data):
            flash('You have been logged in.', 'success')
            return redirect(url_for('profile'))
        else:
            flash('Invalid password', 'warning')
            return redirect(url_for('login'))
    return render_template('login.html', form=form)


@app.route('/profile')
def profile():
    return render_template('profile.html')
