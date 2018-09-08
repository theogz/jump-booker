import eventlet
eventlet.monkey_patch()
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_socketio import SocketIO
from dotenv import load_dotenv
import os
import pytz
from datetime import datetime

# Environment variables
dotenv_path = os.path.join(os.path.dirname(__file__), './.env')
load_dotenv(dotenv_path)
SECRET_KEY = os.getenv('FLASK_SECRET')
REDIS_URL = os.getenv('REDIS_URL')

app = Flask(__name__)
app.secret_key = SECRET_KEY
app.config['REDIS_URL'] = REDIS_URL
app.templates_auto_reload = True


# Time zone formatting
def suffix(d):
    return (
        'th'
        if 11 <= d <= 13
        else {1: 'st', 2: 'nd', 3: 'rd'}.get(d % 10, 'th'))


def custom_strftime(format, t):
    return (
        t.strftime(format)
        .replace('{S}', str(t.day) + suffix(t.day))
        .replace('{Y}', '' if datetime.now().year == t.year else f' {t.year}'))


def datetimefilter(value):
    tz = pytz.timezone('America/Los_Angeles')
    utc = pytz.timezone('UTC')
    value = utc.localize(value, is_dst=None).astimezone(pytz.utc)
    local_dt = value.astimezone(tz)
    return custom_strftime('%A, %b {S}{Y} %H:%M %p', local_dt)


app.jinja_env.filters['datetimefilter'] = datetimefilter

# Security
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

# Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dev.db'
db = SQLAlchemy(app)
socket = SocketIO(app, logger=True, engineio_logger=True)

from booker import routes  # noqa
