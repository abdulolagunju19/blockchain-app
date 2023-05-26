#!/usr/bin/python
# -*- coding: utf-8 -*-

from flask import Flask, render_template, flash, redirect, url_for, session, request, logging
from passlib.hash import sha256_crypt
from flask_mysqldb import MySQL
from functools import wraps
import time
from dotenv import load_dotenv
import os

app = Flask(__name__)

load_dotenv()

app.config['MYSQL_HOST'] = os.environ['MYSQL_HOST']
app.config['MYSQL_USER'] = os.environ['MYSQL_USER']
app.config['MYSQL_PASSWORD'] = os.environ['MYSQL_PASSWORD']
app.config['MYSQL_DB'] = os.environ['MYSQL_DB']
app.config['MYSQL_CURSORCLASS'] = os.environ['MYSQL_CURSORCLASS']



mysql = MySQL(app)

from sqlhelpers import *
from forms import *

def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, please log in.', 'danger')
            return redirect(url_for('login'))
    return wrap

def log_in_user(username):
    users = Table("users", "name", "email", "username", "password")
    user = users.getone("username", username)

    session['logged_in'] = True
    session['username'] = username
    session['name'] = user.get('name')
    session['email'] = user.get('email')

@app.route("/register", methods = ['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    users = Table("users", "name", "email", "username", "password")

    #check that user has pressed submit, input is correct
    if request.method == 'POST' and form.validate():
        username = form.username.data
        email = form.email.data
        name = form.name.data

        if isnewuser(username):
            password = sha256_crypt.encrypt(form.password.data)
            users.insert(name, email, username, password)
            log_in_user(username)
            return redirect(url_for('dashboard'))
        else:
            flash('User already exists', 'danger')
            return redirect(url_for('register'))

    return render_template('register.html', form=form)

@app.route("/dashboard")
@is_logged_in
def dashboard():
    blockchain = get_blockchain().chain
    ct = time.strftime("%I:%M %p")
    return render_template("dashboard.html", session=session, ct=ct, blockchain=blockchain, page='dashboard')

@app.route("/login", methods = ['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        candidate = request.form['password']

        users = Table("users", "name", "email", "username", "password")
        user = users.getone("username", username)
        accPass = user.get('password')

        if accPass is None:
            flash("Username is not found", 'danger')
            return redirect(url_for('login'))
        else:
            if sha256_crypt.verify(candidate, accPass):
                log_in_user(username)
                flash("You are now logged in.", 'success')
                return redirect(url_for('dashboard'))

            else:
                flash("Invalid password", 'danger')
                return redirect(url_for('login'))

    return render_template("login.html")

@app.route("/transaction", methods = ['GET', 'POST'])
@is_logged_in
def transaction():
    form = SendMoneyForm(request.form)
    balance = get_balance(session.get('username'))

    if request.method == 'POST':
        try:
            send_money(session.get('username'), form.username.data, form.amount.data)
            flash("Money Sent!", 'success')

        except Exception as e:
            flash(str(e), 'danger')

        return redirect(url_for('transaction'))

    return render_template("transaction.html", balance=balance, form=form, page='transaction')

@app.route("/buy", methods = ['GET', 'POST'])
@is_logged_in
def buy():
    form = BuyForm(request.form)
    balance = get_balance(session.get('username'))

    if request.method == 'POST':
        try:
            send_money("BANK", session.get('username'), form.amount.data)
            flash("Purchase is successful", 'success')
        except Exception as e:
            flash(str(e), 'danger')
        return redirect(url_for('dashboard'))
    return render_template("buy.html", balance=balance, form=form, page='buy')

@app.route("/logout")
@is_logged_in
def logout():
    session.clear()
    flash("Logout success", "success")

    return render_template("login.html")

@app.route("/")
def index():
    return render_template("index.html")

if __name__ == '__main__':
    app.secret_key = os.environ['SECRET_KEY']
    app.run(debug = True)
