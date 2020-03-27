import logging
import os
from copy import deepcopy
from logging.handlers import RotatingFileHandler
from pathlib import Path
from random import randrange
from typing import List

import requests
from flask import Flask
from flask_apscheduler import APScheduler
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from app.config import Config
from app.ditto import DITTO_BASE_URL, DITTO_NAMESPACE, DITTO_PASSWORD, DITTO_USERNAME, VINS, fetch_twin_by_vin

app = Flask(__name__)
app.config.from_object(Config())
db = SQLAlchemy(app)
migrate = Migrate(app, db)

scheduler = APScheduler()

from app import routes, models, errors, util


@scheduler.task('interval', id='update_twins_job', seconds=30, misfire_grace_time=900)
def update_twins():
    """
    Due to lack of live data, this method generates random data and updates all twins every 30 seconds
    """
    for vin in VINS:
        humidity = randrange(10, 100)
        temp = randrange(30, 55)
        fuel_level = randrange(40, 80)
        engine_temp = randrange(60, 130)
        battery_capacity = randrange(40, 80)
        current_level = randrange(60, 90)
        tyre_pressure = randrange(25, 40)
        tyre_temp = randrange(20, 80)
        brake_fluid_level = randrange(40, 80)
        brake_temp = randrange(50, 100)

        payload = {
            'environment': {
                'properties': {
                    'humidity': humidity,
                    'temp': temp
                }
            },
            'fuel': {
                'properties': {
                    'type': 'Leaded',
                    'capacity': 70,
                    'level': fuel_level,
                    'rating': 'A'
                }
            },
            'engine': {
                'properties': {
                    'temp': engine_temp,
                    'battery_capacity': battery_capacity,
                    'current_level': current_level
                }
            },
            'tyres': {
                'properties': {
                    'pressure': tyre_pressure,
                    'wear': 20.5,
                    'rating': 'B',
                    'temp': tyre_temp
                }
            },
            'brakes': {
                'properties': {
                    'type': 'CarbonCeramic',
                    'temp': brake_temp,
                    'fluid_level': brake_fluid_level
                }
            }
        }
        response = requests.put(f'{DITTO_BASE_URL}things/{DITTO_NAMESPACE}:{vin}/features',
                                json=payload,
                                auth=(DITTO_USERNAME, DITTO_PASSWORD))
        if not response.ok:
            app.logger.info(f'Unable to update twin for vehicle with VIN: {vin}')
        else:
            vehicle: models.Vehicle = models.Vehicle.query.filter_by(vin=vin).first()
            if vehicle is None:
                app.logger.warn(f'Vehicle with VIN: {vin} does not exist in DB!')
            else:
                vehicle.calculate_health(util.extract_twin_data(payload))
                db.session.commit()


@scheduler.task('interval', id='update_twins_job', seconds=30, misfire_grace_time=900)
def send_alerts():
    users: List[models.User] = models.User.query.filter_by(logged_in=True)
    vehicles: List[models.Vehicle] = models.Vehicle.query.all()

    for user in users:
        for vehicle in vehicles:
            if vehicle.overall_health is None:  # First run through => database yet to be updated
                return
            twin = fetch_twin_by_vin(vehicle.vin)
            new_vehicle = deepcopy(vehicle)
            new_vehicle.calculate_health(util.extract_twin_data(twin))

            delta_overall = abs(
                (new_vehicle.overall_health - vehicle.overall_health) * (100 / new_vehicle.overall_health))
            delta_brakes = abs((new_vehicle.brakes_health - vehicle.brakes_health) * (100 / new_vehicle.brakes_health))
            delta_engine = abs((new_vehicle.engine_health - vehicle.engine_health) * (100 / new_vehicle.engine_health))
            delta_fuel = abs((new_vehicle.fuel_health - vehicle.fuel_health) * (100 / new_vehicle.fuel_health))
            delta_tyre = abs((new_vehicle.tyres_health - vehicle.tyres_health) * (100 / new_vehicle.tyres_health))

            alert_type, warning_msg = util.get_alert_type_and_msg(delta_brakes, delta_engine, delta_fuel, delta_tyre,
                                                                  delta_overall)

            payload = {
                'data': {
                    'vin': vehicle.vin,
                    'license_plate': vehicle.license_plate,
                    'text': warning_msg,
                    'type': alert_type,
                    'email_id': user.email_id,
                    'role': user.role,
                },
                'registration_ids': [user.firebase_token.token]
            }

            response = requests.post('https://fcm.googleapis.com/fcm/send',
                                     json=payload,
                                     headers={
                                         'Content-Type': 'application/json',
                                         'Authorization': 'key=' + os.environ.get('FCM_KEY')
                                     })

            if not response.ok:
                app.logger.info(f'Unable to send alert')


scheduler.init_app(app)
scheduler.start()

if not app.debug:
    p = Path('logs')
    if not p.exists():
        p.mkdir()
    file_handler = RotatingFileHandler('logs/api_server.log', maxBytes=10240, backupCount=5)
    file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)

    app.logger.setLevel(logging.INFO)
    app.logger.info('API Server started')
