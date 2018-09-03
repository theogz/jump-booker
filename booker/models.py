from datetime import datetime
from booker import db, login_manager
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    admin = db.Column(db.Boolean, nullable=False, default=False)
    bookings = db.relationship(
        'Booking', backref='requester', lazy=True)

    def __repr__(self):
        return f"User('{self.email}')"


class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    requester_id = db.Column(
        db.Integer, db.ForeignKey('user.id'), nullable=False)
    query = db.Column(db.String(100), nullable=False)
    human_readable_address = db.Column(db.String(300))
    latitude = db.Column(db.Float(precision=5))
    longitude = db.Column(db.Float(precision=5))
    created_at = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow)
    status = db.Column(db.String(50), nullable=False, default='pending')
    # booking_status = db.relationship(
    #     'BookingStatus',
    #     backref='booking', lazy=True)

    def __repr__(self):
        return (
            f"Booking({self.id}, {self.requester_id}, '{self.created_at}',"
            f"'{self.query}')")


# class BookingStatus(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     booking_id = db.Column(
#         db.Integer, db.ForeignKey('booking.id'), nullable=False)
#     complete = db.Column(db.Boolean, nullable=False)
#     timestamp = db.Column(
#         db.DateTime, nullable=False, default=datetime.utcnow)

#     def __repr__(self):
#         return f"Status({self.id}, {self.booking_id}, '{self.timestamp})'"
