from datetime import datetime
from booker import db, login_manager
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    bookings = db.relationship(
        'BookingStatus', backref='requester', lazy=True)

    def __repr__(self):
        return f"User('{self.email}'')"


class BookingStatus(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    requester_id = db.Column(
        db.Integer, db.ForeignKey('user.id'), nullable=False)
    complete = db.Column(db.Boolean, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"Booking({self.id}, {self.requester_id}, '{self.timestamp})'"
