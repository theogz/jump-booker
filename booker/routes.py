from booker import app, db, bcrypt
from flask_login import login_user, logout_user, current_user, login_required
from booker.models import Users, Bookings
from booker.book_bike import create_booking, schedule_trip, cancel_rental
from booker.init_db import remake_db
from booker.forms import (
    AddressForm, LoginForm, RegistrationForm, UpdateAccountForm)
from flask import (
    request, Response, render_template, redirect, url_for,
    flash)
import eventlet


@app.route('/', methods=['GET'])
@login_required
def index():
    form = AddressForm()
    return render_template('index.html', form=form)


@app.route('/book', methods=['POST'])
@login_required
def book():
    form = AddressForm()

    if not form.validate_on_submit():
        return Response('Problem with form', 403)

    booking = create_booking(form.address.data, True)

    eventlet.spawn(
        schedule_trip, booking_id=booking.id, email=current_user.email)

    init_data = (
        {
            'message': (
                'Searching bikes around '
                f'{booking.human_readable_address}'
                '...'),
            'category': 'info'
        } if booking.status == 'pending'
        else ({
            'message': 'Google address API limit exceeded',
            'category': 'warning'
        }))
    flash(init_data['message'], init_data['category'])

    return redirect(url_for('booking_id', id=booking.id))


@app.route('/booking/<id>', methods=['GET', 'PUT'])
@login_required
def booking_id(id):
    booking = db.session.query(Bookings).get(id)
    return render_template('booking.html', booking=booking)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if (
            user and
            bcrypt.
            check_password_hash(user.password, form.password.data)
        ):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return (
                redirect(next_page) if next_page
                else (url_for('index')))
        flash(
            'Login Unsuccessful. Please check username and password',
            'danger')
    return render_template('login.html', title='Login', form=form)


@app.route('/register', methods=['GET', 'POST'])
@login_required
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_pw = (
            bcrypt
            .generate_password_hash(form.password.data).decode('utf-8'))
        user = Users(
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


@app.route('/bookings/<username>', methods=['GET'])
@login_required
def bookings(username):
    page = request.args.get('page', 1, type=int)
    user = db.session.query(Users).filter_by(username=username).first_or_404()
    booking_list = (
        db.session.query(Bookings).filter_by(requester=user)
        .order_by(Bookings.created_at.desc())
        .paginate(page=page, per_page=10))
    return render_template('bookings.html', bookings=booking_list)


@app.route('/cancel', methods=['GET'])
@login_required
def cancel():
    is_cancelled = cancel_rental()
    flash(is_cancelled['message'], is_cancelled['category'])
    return redirect(url_for('index'))


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


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
