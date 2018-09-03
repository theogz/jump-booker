from booker import db, bcrypt
from booker.models import User
import os
from dotenv import load_dotenv

# Environment variables.
dotenv_path = os.path.join(os.path.dirname(__file__), './.env')
load_dotenv(dotenv_path)


def remake_db():
    db.drop_all()
    db.create_all()
    print('OK')
    first_admin = User(
        username='admin',
        email='a@b.com',
        password=(
            bcrypt
            .generate_password_hash(os.getenv('ADMIN_PW')).decode('utf-8')),
        admin=True)
    db.session.add(first_admin)
    db.session.commit()
    print(first_admin.id)
