from booker import db, bcrypt
from booker.models import Users, Bookings
import os
from dotenv import load_dotenv
from custom_logger import logger
from datetime import datetime, timedelta

# Environment variables.
dotenv_path = os.path.join(os.path.dirname(__file__), './.env')
load_dotenv(dotenv_path)


def remake_db():
    db.drop_all()
    db.create_all()

    first_admin = Users(
        username='admin',
        email=os.getenv('ADMIN_EMAIL'),
        password=(
            bcrypt
            .generate_password_hash(os.getenv('ADMIN_PW')).decode('utf-8')),
        admin=True)

    mock_booking_1 = Bookings(
        requester=first_admin,
        query='jump bikes',
        human_readable_address=(
            '2200 Jerrold Ave, San Francisco, CA 94124, USA'),
        matched_bike_address='2218 Jerrold Ave, San Francisco, CA',
        latitude=37.7458634,
        longitude=-122.4021239,
        status='booked',
        created_at=datetime.utcnow() - timedelta(days=370, minutes=1300))
    mock_booking_2 = Bookings(
        requester=first_admin,
        query='google hq',
        human_readable_address='345 Spear St, San Francisco, CA 94105, USA',
        latitude=37.79005,
        longitude=-122.39019,
        status='error',
        created_at=datetime.utcnow() - timedelta(minutes=5))

    db.session.add(first_admin)
    db.session.add(mock_booking_1)
    db.session.add(mock_booking_2)
    db.session.commit()
    logger.info('Succesfully recreated the database.')
