from flask import (
    Flask, request, Response, render_template, redirect, url_for,
    flash)
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os
from functools import wraps
from concurrent.futures import ThreadPoolExecutor
import book_bike
from forms import AddressForm, LoginForm, RegistrationForm

# Environment variables
dotenv_path = os.path.join(os.path.dirname(__file__), './.env')
load_dotenv(dotenv_path)

executor = ThreadPoolExecutor(max_workers=4)
SECRET_KEY = os.getenv('FLASK_SECRET')
app = Flask(__name__)
app.secret_key = SECRET_KEY
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dev.db'

# db = SQLAlchemy(app)


# Auth
def check_auth(username, password):
    return (
        username == os.getenv('USERNAME')
        and password == os.getenv('PASSWORD')
    )


def authenticate():
    return Response(
        'Invalid credentials :(', 401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'}
    )


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated


@app.route('/', methods=['GET', 'POST'])
def main_page():
    form = AddressForm()
    if form.validate_on_submit():
        # Todo: use the db to prevent multiple calls to google API
        flash(
            'Searching bikes around '
            f'{book_bike.get_coordinates(form.address.data)["human_address"]}'
            '...',
            'success')
        executor.submit(book_bike.schedule_booking(form.address.data))
        return redirect(url_for('main_page'))
    return render_template('index.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        if (
            form.email.data == 'teyo@teyo.com' and
            form.password.data == 'password'
        ):
            flash('You have been logged in!', 'success')
            return redirect(url_for('home'))
        else:
            flash(
                'Login Unsuccessful. Please check username and password',
                'danger')
    return render_template('login.html', title='Login', form=form)


@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        flash(f'Account created for {form.username.data}!', 'success')
        return redirect(url_for('main_page'))
    return render_template('register.html', title='Register', form=form)


@app.route('/authorized')
@requires_auth
def success_page():
    return Response(response='Yay', status=200)


if __name__ == '__main__':
    app.run(host='localhost', port='5000')
