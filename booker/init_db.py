from booker import db, bcrypt
from booker.models import Users, Bookings
import os
from dotenv import load_dotenv
from custom_logger import logger

# Environment variables.
dotenv_path = os.path.join(os.path.dirname(__file__), './.env')
load_dotenv(dotenv_path)


def remake_db():
    db.drop_all()
    db.create_all()
    first_admin = Users(
        username='admin',
        email='a@b.com',
        password=(
            bcrypt
            .generate_password_hash(os.getenv('ADMIN_PW')).decode('utf-8')),
        admin=True)
    mock_booking = Bookings(
        requester=first_admin,
        query='345 spear',
        human_readable_address='345 Spear St, San Francisco, CA 94105, USA',
        latitude=37.79005,
        longitude=-122.39019,
        status='completed')
    db.session.add(first_admin)
    db.session.add(mock_booking)
    db.session.commit()
    logger.info('Succesfully recreated the database.')
