import os
from typing import Union

import requests

DITTO_BASE_URL: str = 'http://localhost:8080/api/2/'
DITTO_USERNAME: str = os.environ.get('DITTO_USERNAME')
DITTO_PASSWORD: str = os.environ.get('DITTO_PASSWORD')
DITTO_NAMESPACE: str = os.environ.get('DITTO_NAMESPACE')

VINS = ['12345678912345678', '12344862397345673', '41654199297345675', '41654199297345679', '98716931387431697',
        '32164894198433952', '87465413196846116', '74149874641316844', '74134941132143712', '54327932973250721']


def fetch_twin_by_vin(vin: str) -> Union[dict, str]:
    """
    Fetch data from the twin of vehicle by VIN (Twin ID)

    :param vin: Vehicle Identification Number (thingId of the twin)
    :return: returns error string if GET request fails, otherwise dict of twin's features
    """
    response = requests.get(f'{DITTO_BASE_URL}things/{DITTO_NAMESPACE}:{vin}/features',
                            auth=(DITTO_USERNAME, DITTO_PASSWORD))
    if response.status_code == 404:
        return f'Twin for vehicle with VIN: {vin} does not exist!'
    return response.json()


def fetch_twin_by_license_plate(license_plate: str) -> Union[dict, str]:
    """
    Fetch data from the twin of vehicle by VIN (Twin ID)

    :param license_plate: License plate number of the vehicle (stored as static attribute in the twin)
    :return: returns error string if GET request fails or no matching twin found, otherwise dict of twin's features
    """
    response = requests.get(f'{DITTO_BASE_URL}search/things/?filter=eq(attributes/license_plate,"{license_plate}")',
                            auth=(DITTO_USERNAME, DITTO_PASSWORD))
    if response.status_code != 200 or len(response.json()['items']) == 0:
        return f'Twin for vehicle with license plate: {license_plate} does not exist!'
    return response.json()['items'][0]['features']
