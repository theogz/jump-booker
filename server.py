from flask import Flask, request, Response, render_template, redirect
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


@app.route('/')
def main_page():
    return render_template('index.html')


@app.route('/authorized')
@requires_auth
def success_page():
    return Response(response='Yay', status=200)


@app.route('/booking', methods=['POST'])
def schedule_booking():
    address = AddressForm()
    executor.submit(book_bike.schedule_booking(address))
    return redirect('/waiting', code=302)


@app.route('/waiting', methods=['GET'])
def wait_status():
    return Response(response='Looking for bikes around..', status=200)


if __name__ == '__main__':
    app.run(host='localhost', port='5000')
