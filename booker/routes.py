from booker import app, db, bcrypt
from flask_login import login_user, logout_user, current_user, login_required
from booker.models import User
from booker.book_bike import create_booking
from booker.init_db import remake_db
from booker.forms import (
    AddressForm, LoginForm, RegistrationForm, UpdateAccountForm)
from flask import (
    request, Response, render_template, redirect, url_for,
    flash)
from concurrent.futures import ThreadPoolExecutor

executor = ThreadPoolExecutor(max_workers=4)


@app.route('/', methods=['GET', 'POST'])
@login_required
def main_page():
    form = AddressForm()
    if form.validate_on_submit():
        booking = create_booking(form.address.data)
        flash(
            'Searching bikes around '
            f'{booking.human_readable_address}'
            '...',
            'success')
        # executor.submit(BookingHandler(booking.id, form.address.data))
        return redirect(url_for('main_page'))
    return render_template('index.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main_page'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if (
            user and
            bcrypt.
            check_password_hash(user.password, form.password.data)
        ):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return (
                redirect(next_page) if next_page
                else (url_for('main_page')))
        flash(
            'Login Unsuccessful. Please check username and password',
            'danger')
    return render_template('login.html', title='Login', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main_page'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_pw = (
            bcrypt
            .generate_password_hash(form.password.data).decode('utf-8'))
        user = User(
            email=form.email.data, username=form.username.data,
            password=hashed_pw)
        db.session.add(user)
        db.session.commit()
        if user.id == 1:
            user.admin = True
            db.session.commit()
        flash(f'Account created.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    return render_template(
        'account.html', title='Account', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main_page'))


@app.route('/authorized')
@login_required
def success_page():
    # Edit this later to generate auth tokens per user
    return Response(response='Yay', status=200)


@app.route('/remake-db')
@login_required
def nuke_db():
    if not current_user.admin:
        return Response('Only for admins', 403)
    remake_db()
    return redirect(url_for('register'))
