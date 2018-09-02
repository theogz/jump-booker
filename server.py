from flask import (
    Flask, request, Response, render_template, redirect, url_for,
    flash)
from dotenv import load_dotenv
import os
from functools import wraps
from concurrent.futures import ThreadPoolExecutor
import book_bike
from forms import AddressForm

# Environment variables
dotenv_path = os.path.join(os.path.dirname(__file__), './.env')
load_dotenv(dotenv_path)

executor = ThreadPoolExecutor(max_workers=4)
SECRET_KEY = os.getenv('FLASK_SECRET')
app = Flask(__name__)
app.secret_key = SECRET_KEY


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
    address_form = AddressForm()
    if address_form.validate_on_submit():
        flash(f'Requesting bikes for: {address_form.address.data}', 'success')
        executor.submit(book_bike.schedule_booking(address_form.address))
        return redirect(url_for('main_page'))
    return render_template('index.html', form=address_form)


@app.route('/authorized')
@requires_auth
def success_page():
    return Response(response='Yay', status=200)


if __name__ == '__main__':
    app.run(host='localhost', port='5000')
