from flask import Flask, request, Response
from dotenv import load_dotenv
import os
from functools import wraps

# Environment variables
dotenv_path = os.path.join(os.path.dirname(__file__), './.env')
load_dotenv(dotenv_path)

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
@requires_auth
def main_page():
    return 'Hello world!'


@app.route('/authorized')
@requires_auth
def success_page():
    return Response('Yay', 200)


if __name__ == '__main__':
    app.run(host='localhost', port='5000')
