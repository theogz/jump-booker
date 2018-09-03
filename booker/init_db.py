from booker import db, bcrypt
from booker.models import Users
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
    db.session.add(first_admin)
    db.session.commit()
    logger.info('Succesfully recreated the database.')
