from datetime import datetime
from booker import db, login_manager
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))


class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    admin = db.Column(db.Boolean, nullable=False, default=False)
    bookings = db.relationship(
        'Bookings', backref='requester', lazy=True)

    def __repr__(self):
        return f"User('{self.email}')"


class Bookings(db.Model):
    """
    Potential statuses should be pending/completed/timeout/error/cancelled
    """
    id = db.Column(db.Integer, primary_key=True)
    requester_id = db.Column(
        db.Integer, db.ForeignKey('users.id'), nullable=False)

    query = db.Column(db.String(100), nullable=False)
    human_readable_address = db.Column(db.String(200))
    latitude = db.Column(db.Float(precision=5))
    longitude = db.Column(db.Float(precision=5))
    matched_bike_address = db.Column(db.String(200))

    status = db.Column(db.String(50), nullable=False, default='pending')

    created_at = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow
    )
    is_deleted = db.Column(db.Boolean, nullable=False, default=False)

    def __repr__(self):
        return (
            f"Booking({self.id}, {self.requester_id}, '{self.created_at}',"
            f"'{self.query}')")
