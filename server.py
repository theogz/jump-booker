from flask import Flask, request, Response, render_template
from dotenv import load_dotenv
import os
from functools import wraps
from concurrent.futures import ThreadPoolExecutor
import book_bike

# Environment variables
dotenv_path = os.path.join(os.path.dirname(__file__), './.env')
load_dotenv(dotenv_path)

executor = ThreadPoolExecutor(max_workers=4)
app = Flask(__name__)


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
    return Response('Yay', 200)


@app.route('/fetch_bike_from_address', methods=['POST'])
def schedule_booking():
    address = request.form['address']
    return executor.submit(book_bike.schedule_booking(address))


if __name__ == '__main__':
    app.run(host='localhost', port='5000')
