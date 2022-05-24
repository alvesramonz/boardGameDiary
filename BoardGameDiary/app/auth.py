from re import template
from flask import Blueprint, render_template, redirect, url_for, request, flash, session
import requests
from bson import ObjectId
from werkzeug.local import LocalProxy
from app.main import login_required
from settings.db import get_db
import hashlib

auth = Blueprint('auth', __name__)

db = LocalProxy(get_db)

@auth.route('/login')
def login():
    return render_template('login.html')

@auth.route('/signup')
def signup():
    return render_template('signup.html')

@auth.route('/logout')
@login_required
def logout():
    response = requests.post('http://127.0.0.1:5000/logout', data={"token": session['token']})
    session.clear()

    return redirect(url_for('auth.login'))



""" Routes """
@auth.route('/login', methods=['POST'] )
def login_post():
    client_id = request.form.get('username')
    client_secret = request.form.get('password')

    response = start_session(client_id, client_secret)

    if response.get('token'):
        user = db.users.find_one({'_id': ObjectId(response.get('user_id'))}, {'_id': 1, 'email': 1, 'name': 1})
        user['_id'] = str(user.get('_id'))

        session['token'] = response.get('token')
        session['isAdmin'] = response.get('isAdmin')
        session['user'] = user

        return redirect(url_for('main.view_my_games'))
    else:
        flash('Email or password invalid')
        return redirect(url_for('auth.login'))

@auth.route('/signup', methods=['POST'])
def signup_post():
    email = request.form.get('email')
    name = request.form.get('name')
    password = request.form.get('password')

    user = db.users.find_one({'email': email})

    if user:
        flash('Email address already exists')
        return redirect(url_for('auth.signup'))

    hash_object = hashlib.sha1(bytes(password, 'utf-8'))
    hash_password = hash_object.hexdigest()

    new_user = {
        "email": email,
        "name": name,
        "password": hash_password
    }

    new_user = db.users.insert_one(new_user)
    if new_user:
        new_user_id = new_user.inserted_id
        create_client(name, password, new_user_id)
        return redirect(url_for('main.view_my_games'))


def create_client(client_id, client_secret, user_id):
    payload = {
        'client_id': client_id,
        'client_secret': client_secret,
        'mongo_client_id': user_id

    }

    response = requests.post('http://127.0.0.1:5000/client', data=payload)
    response = response.json()

    return response

def start_session(client_id, client_secret):
    payload = {
        'client_id': client_id,
        'client_secret': client_secret
    }

    response = requests.post('http://127.0.0.1:5000/auth', data=payload)
    response = response.json()

    return response
