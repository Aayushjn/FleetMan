from typing import List

from flask import request
from passlib.hash import argon2

from app import app, db
from app.ditto import fetch_twin_by_vin, fetch_twin_by_license_plate
from app.errors import bad_request_error, unauthorized_error, not_found_error, request_timeout_error
from app.models import User, Vehicle
from app.util import extract_twin_data


@app.route('/users/create', methods=['PUT'])
def create_user():
    email_id: str = request.form.get('email_id')
    name: str = request.form.get('name')
    password: str = request.form.get('password')
    role: str = request.form.get('role')

    if email_id is None or name is None or password is None or role is None:
        return bad_request_error('Request parameters are missing!')

    user: User = User.query.filter_by(email_id=email_id).first()
    if user is not None:
        return bad_request_error(f'User with {email_id} already exists!')

    user: User = User(email_id=email_id, name=name, password=argon2.hash(password), role=role)
    db.session.add(user)
    db.session.commit()

    return user.to_dict(), 201


@app.route('/users/login', methods=['POST'])
def login_user():
    email_id: str = request.form.get('email_id')
    password: str = request.form.get('password')

    if email_id is None or password is None:
        return bad_request_error('Request parameters are missing!')

    user: User = User.query.filter_by(email_id=email_id).first()
    if user is not None:
        if argon2.verify(password, user.password):
            return user.to_dict(), 200
        else:
            return unauthorized_error(f'Password for {email_id} is incorrect!')
    else:
        return not_found_error(f'User with {email_id} does not exist!')


@app.route('/vehicles', methods=['GET'])
def get_all_vehicles():
    hatchbacks, sedans, suvs = [], [], []
    vehicles: List[Vehicle] = Vehicle.query.all()

    for v in vehicles:
        if v.type == 'Hatchback':
            hatchbacks.append(v.to_minimal_model())
        elif v.type == 'Sedan':
            sedans.append(v.to_minimal_model())
        else:
            suvs.append(v.to_minimal_model())

    return {
               'Hatchbacks': hatchbacks,
               'Sedans': sedans,
               'SUVs': suvs
           }, 200


@app.route('/vehicles', methods=['POST'])
def get_vehicle():
    vin = request.form.get('vin')
    license_plate = request.form.get('license_plate')
    email_id = request.form.get('email_id')

    if email_id is None or (vin is None and license_plate is None):
        return bad_request_error('Request parameters are missing!')

    if vin is not None:
        vehicle: Vehicle = Vehicle.query.filter_by(vin=vin).first()
        if vehicle is None:
            return not_found_error(f'Could not find vehicle with VIN: {vin}!')
        twin_data = fetch_twin_by_vin(vin)
    else:
        vehicle: Vehicle = Vehicle.query.filter_by(license_plate=license_plate).first()
        if vehicle is None:
            return not_found_error(f'Could not find vehicle with license plate: {license_plate}!')
        twin_data = fetch_twin_by_license_plate(license_plate)

    if isinstance(twin_data, str):
        if twin_data.startswith('Cannot'):
            return request_timeout_error(twin_data)
        else:
            return not_found_error(twin_data)

    user: User = User.query.filter_by(email_id=email_id).first()

    twin_system_data = extract_twin_data(twin_data)
    vehicle.calculate_health(twin_system_data)

    twin_system_data['brakes']['health'] = vehicle.brakes_health
    twin_system_data['engine']['health'] = vehicle.engine_health
    twin_system_data['fuel']['health'] = vehicle.fuel_health
    twin_system_data['tyres']['health'] = vehicle.tyres_health

    if user.role == 'INSURANCE':
        return {
                   "brakes": None,
                   "driver": None,
                   "engine": None,
                   "fuel": None,
                   "license_plate": vehicle.license_plate,
                   "model": vehicle.model,
                   "overall_health": None,
                   "type": None,
                   "tyres": None,
                   "vin": vehicle.vin
               }, 200
    elif user.role == 'ADMIN':
        return {
                   **vehicle.to_dict(),
                   **twin_system_data
               }, 200
    elif user.role == 'MAINTENANCE':
        ret_val = {
            **vehicle.to_dict(),
            **twin_system_data
        }
        ret_val['vin'] = None
        ret_val['license_plate'] = None
        ret_val['driver'] = None
        ret_val['type'] = None

        return ret_val, 200
    else:
        return {
                   "brakes": None,
                   "driver": None,
                   "engine": None,
                   "fuel": None,
                   "license_plate": None,
                   "model": None,
                   "overall_health": None,
                   "type": None,
                   "tyres": None,
                   "vin": None
               }, 200
