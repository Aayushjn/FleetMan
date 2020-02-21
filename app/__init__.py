import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from random import randrange

import requests
from flask import Flask
from flask_apscheduler import APScheduler
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from app.config import Config
from app.ditto import DITTO_BASE_URL, DITTO_NAMESPACE, DITTO_PASSWORD, DITTO_USERNAME, VINS

app = Flask(__name__)
app.config.from_object(Config())
db = SQLAlchemy(app)
migrate = Migrate(app, db)

scheduler = APScheduler()


@scheduler.task('interval', id='update_twins_job', seconds=30, misfire_grace_time=900)
def update_twins():
    """
    Due to lack of live data, this method generates random data and updates all twins every 30 seconds
    """
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

    for vin in VINS:
        payload = {
            "environment": {
                "properties": {
                    "humidity": humidity,
                    "temp": temp
                }
            },
            "fuel": {
                "properties": {
                    "type": "Leaded",
                    "capacity": 70,
                    "level": fuel_level,
                    "rating": "A"
                }
            },
            "engine": {
                "properties": {
                    "temp": engine_temp,
                    "battery_capacity": battery_capacity,
                    "current_level": current_level
                }
            },
            "tyres": {
                "properties": {
                    "pressure": tyre_pressure,
                    "wear": 20.5,
                    "rating": "B",
                    "temp": tyre_temp
                }
            },
            "brakes": {
                "properties": {
                    "type": "CarbonCeramic",
                    "temp": brake_temp,
                    "fluid_level": brake_fluid_level
                }
            }
        }
        response = requests.put(f'{DITTO_BASE_URL}things/{DITTO_NAMESPACE}:{vin}/features',
                                json=payload,
                                auth=(DITTO_USERNAME, DITTO_PASSWORD))
        if not response.ok:
            app.logger.info(f'Unable to update twin for vehicle with VIN: {vin}')


scheduler.init_app(app)
scheduler.start()

from app import routes, models, errors

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
