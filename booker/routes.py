from booker import app
from booker.book_bike import schedule_booking, get_coordinates
from booker.forms import AddressForm, LoginForm, RegistrationForm
from flask import (
    request, Response, render_template, redirect, url_for,
    flash)
from functools import wraps
from concurrent.futures import ThreadPoolExecutor
import os

executor = ThreadPoolExecutor(max_workers=4)


# Auth, remove this later with login logic
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
            f'{get_coordinates(form.address.data)["human_address"]}'
            '...',
            'success')
        executor.submit(schedule_booking(form.address.data))
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
