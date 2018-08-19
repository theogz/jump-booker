import requests
import os
from dotenv import load_dotenv
import geocoder
from time import sleep
import pprint
import json
from custom_logger import logger

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

# We retry 30 times (aka 15 minutes).
MAX_ATTEMPTS = 30


def get_coordinates():
    """
    Ask for current address, establish closest place interpreted.
    Return latitude/longitude.
    """

    print('Please enter your current address:')
    g = geocoder.google(
        f'{input()} San Francisco'
    )
    logger.info(
        f'Searching bikes around {g.address}'
    )
    return {
        'latitude': g.latlng[0],
        'longitude': g.latlng[1]
    }


def list_closest_bikes(coordinates):
    """ Fetches the 10 closest bikes of the provided coordinates """

    r = requests.get(
        f'{BASE_URL}/bikes.json?'
        'per_page=10&sort=distance_asc'
        f'&latitude={coordinates["latitude"]}'
        f'&longitude={coordinates["longitude"]}',
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
        bike['ebike_battery_level'] >= 30 and
        bike['distance'] <= 400
    )


def find_best_bike(coordinates, attempt):
    """
    Try MAX_ATTEMPTS time (spaced by 30 seconds) to find a close match.
    Return False if eventually no match.
    Return the closest bike available otherwise.
    """

    bike_list = list_closest_bikes(coordinates)
    if bike_list is None:
        return None

    valid_bike_list = [
        bike for bike in bike_list
        if is_valid(bike)
    ]

    if not valid_bike_list:
        if attempt >= MAX_ATTEMPTS:
            logger.warn(f'No bikes found after {attempt} attempts')
            return False
        logger.warn('No bikes found nearby yet.')
        attempt = attempt + 1
        sleep(30)
        return find_best_bike(coordinates, attempt)

    logger.info(
        f'Found {len(valid_bike_list)} bikes matching criteria, '
        'selecting the closest one.'
    )

    best_bike = min(valid_bike_list, key=lambda bike: bike['distance'])
    logger.info(f'Closest bike located at {best_bike["address"]}. Booking...')

    return best_bike


def book_bike(bike):
    """
    Attempt to book a bike.
    Return True or False depending on the success.
    """

    try:
        r = requests.post(
            f'{BASE_URL}/{bike["id"]}/book_bike.json',
            headers=HEADERS
        )
        if r.status_code >= 200 and r.status_code < 400:
            logger.info(f'Succesfully booked bike {bike["name"]}')
            return True
        else:
            logger.error(
                f'{r.status_code} - {json.loads(r.text).get("error")}'
            )
            return False
    except Exception as e:
        logger.exception(e)
    return False


def cancel_rental():
    """ Cancel the current active rental. """

    try:
        r = requests.delete(
            f'{BASE_URL}/rentals/cancel.json',
            headers=HEADERS
        )
        if r.status_code >= 200 and r.status_code < 400:
            logger.info(f'Succesfully cancelled rental.')
            return True
        else:
            logger.error(
                f'{r.status_code} - {json.loads(r.text).get("error")}'
            )
            return False
    except Exception as e:
        logger.exception(e)
    return False


def main():
    logger.error(get_coordinates.__doc__)
    my_coordinates = get_coordinates()
    candidate_bike = find_best_bike(coordinates=my_coordinates, attempt=1)

    if not candidate_bike:
        return None

    if ENV != 'dev':
        book_bike(candidate_bike)
        return

    logger.warn(
        f'Would have booked bike {candidate_bike["name"]} in production'
    )


if __name__ == '__main__':
    main()