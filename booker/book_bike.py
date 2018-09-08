import requests
import os
from dotenv import load_dotenv
import geocoder
from time import sleep
import pprint
from custom_logger import logger
from flask import Response
from flask_login import current_user
from booker import db, socket
from booker.models import Bookings

# Environment variables.
dotenv_path = os.path.join(os.path.dirname(__file__), './.env')
load_dotenv(dotenv_path)

# Constants.
BASE_URL = 'https://app.socialbicycles.com/api'
HEADERS = {
    'Authorization': f'Bearer {os.getenv("SOCIAL_BICYCLES_ACCESS_TOKEN")}'
}
pp = pprint.PrettyPrinter(indent=4).pprint
ENV = os.getenv('ENV')
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
# We retry 30 times (aka 15 minutes).
MAX_ATTEMPTS = 3


def create_booking(raw_query, auto_book=True):
    g = geocoder.google(
        f'{raw_query} San Francisco',
        key=GOOGLE_API_KEY
    )

    booking = Bookings(
        requester=current_user,
        query=raw_query,
        auto_book=auto_book
    )

    if g.status == 'OVER_QUERY_LIMIT':
        booking.status = 'error'
        db.session.add(booking)
        db.session.commit()
        return booking

    booking.human_readable_address = g.address
    booking.latitude = g.latlng[0]
    booking.longitude = g.latlng[1]

    db.session.add(booking)
    db.session.commit()
    return booking


def list_closest_bikes(latitude, longitude):
    """ Fetches the 10 closest bikes of the provided coordinates """

    list_url = (
        f'{BASE_URL}/bikes.json?'
        'per_page=10&sort=distance_asc'
        f'&latitude={latitude}'
        f'&longitude={longitude}')
    logger.info(f'GET - {list_url}')

    r = requests.get(
        list_url,
        headers=HEADERS
    )

    if r.status_code < 400 and r.status_code >= 200:
        return r.json().get('items')
    logger.error(
        f'Request did not go through (code {r.status_code}):\n'
        f'{r.text}'
    )
    return None


def is_valid(bike):
    """
    Asserts if the bikes meets certain criteria of distance and battery.
    Will later be customizable.
    """

    return (
        bike['ebike_battery_level'] >= 25 and
        bike['distance'] <= 400
    )


def find_best_bike(booking, attempt):
    """
    Try MAX_ATTEMPTS time (spaced by 30 seconds) to find a close match.
    Return False if eventually no match.
    Return the closest bike available otherwise.
    """

    bike_list = list_closest_bikes(booking.latitude, booking.longitude)
    if bike_list is None:
        return None

    valid_bike_list = [
        bike for bike in bike_list
        if is_valid(bike)
    ]

    if not valid_bike_list:
        if attempt >= MAX_ATTEMPTS:
            logger.warn(f'No bikes found after {attempt} attempts')
            booking.status = 'timeout'
            db.session.commit()
            return False
        logger.warn('No bikes found nearby yet.')
        sleep(2)
        return find_best_bike(booking, attempt + 1)

    logger.info(
        f'Found {len(valid_bike_list)} bikes matching criteria, '
        'selecting the closest one.'
    )

    best_bike = min(valid_bike_list, key=lambda bike: bike['distance'])
    logger.info(f'Closest bike located at {best_bike["address"]}.')
    booking.matched_bike_address = best_bike['address']
    booking.matched_bike_name = best_bike['name']
    booking.status = 'match found'

    db.session.commit()

    return best_bike


def book_bike(bike):
    """
    Attempt to book a bike.
    Return True or False depending on the success.
    """

    try:
        book_url = f'{BASE_URL}/bikes/{bike["id"]}/book_bike.json'
        logger.info(f'POST - {book_url}')

        r = requests.post(
            book_url,
            headers=HEADERS
        )

        if r.status_code >= 200 and r.status_code < 400:
            logger.info(f'Succesfully booked bike {bike["name"]}')
            return True
        else:
            logger.error(
                f'{r.status_code} - {r.text}'
            )
            return False
    except Exception as e:
        logger.exception(e)
    return False


def cancel_rental():
    """ Cancel the current active rental. """

    try:
        cancel_url = f'{BASE_URL}/rentals/cancel.json'
        r = requests.delete(
            cancel_url,
            headers=HEADERS
        )
        if r.status_code >= 200 and r.status_code < 400:
            logger.info(f'Succesfully cancelled rental.')
            return True
        else:
            logger.error(
                f'{r.status_code} - {r.text}'
            )
            return False
    except Exception as e:
        logger.exception(e)
    return False


def schedule_trip(booking):
    # Todo: handle auto-booking
    if booking.status == 'error':
        return Response(response='Error', status=429)

    logger.info(
        f'Searching bikes around {booking.human_readable_address}')

    candidate_bike = find_best_bike(booking, attempt=1)

    if not candidate_bike:
        return Response(response='No bike around', status=404)

    logger.warn(booking.id)
    logger.warn(booking.matched_bike_address)
    sleep(1)
    logger.warn('PRE PUBLISHING')

    socket.emit('my test event', {'data': booking.matched_bike_address})

    logger.info('POST PUBLISHING')

    if ENV != 'dev':
        book_bike(candidate_bike)
        booking.status = 'completed'
        db.session.commit()
        return Response(response='Booked', status=200)

    logger.warn(
        f'Would have booked bike {candidate_bike["name"]} in production'
    )

    return Response(response='Gotem', status=200)
