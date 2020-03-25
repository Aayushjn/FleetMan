from typing import List, Tuple

from flask import request
from passlib.hash import argon2

from app import app, db
from app.ditto import fetch_twin_by_vin, fetch_twin_by_license_plate
from app.errors import bad_request_error, unauthorized_error, not_found_error, request_timeout_error
from app.models import User, Vehicle, FirebaseToken
from app.util import map_vehicle_data_to_role


@app.route('/users/create', methods=['PUT'])
def create_user() -> Tuple[dict, int]:
    email_id: str = request.form.get('email_id')
    name: str = request.form.get('name')
    password: str = request.form.get('password')
    role: str = request.form.get('role')

    if email_id is None or name is None or password is None or role is None:
        return bad_request_error('Request parameters are missing!')

    user: User = User.query.filter_by(email_id=email_id).first()
    if user is not None:
        return bad_request_error(f'User with {email_id} already exists!')

    user: User = User(email_id=email_id, name=name, password=argon2.hash(password), role=role, logged_in=True)
    db.session.add(user)
    db.session.commit()

    return {}, 201


@app.route('/users/login', methods=['POST'])
def login_user() -> Tuple[dict, int]:
    email_id: str = request.form.get('email_id')
    password: str = request.form.get('password')

    if email_id is None or password is None:
        return bad_request_error('Request parameters are missing!')

    user: User = User.query.filter_by(email_id=email_id).first()
    if user is not None:
        if argon2.verify(password, user.password):
            user.logged_in = True
            db.session.commit()
            return user.to_dict(), 200
        else:
            return unauthorized_error(f'Password for {email_id} is incorrect!')
    else:
        return not_found_error(f'User with {email_id} does not exist!')


@app.route('/users/logout', methods=['POST'])
def logout_user() -> Tuple[dict, int]:
    email_id: str = request.form.get('email_id')

    if email_id is None:
        return bad_request_error('Request parameters are missing!')

    user: User = User.query.filter_by(email_id=email_id).first()
    if user is not None:
        user.logged_in = False
        db.session.commit()
        return {}, 204
    else:
        return not_found_error(f'User with {email_id} does not exist!')


@app.route('/vehicles', methods=['GET'])
def get_all_vehicles() -> Tuple[dict, int]:
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
def get_vehicle() -> Tuple[dict, int]:
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

    if user is None:
        return not_found_error(f'Wrong user')

    return map_vehicle_data_to_role(user.role, twin_data, vehicle), 200


@app.route('/vehicles/count', methods=['GET'])
def get_vehicle_count() -> Tuple[dict, int]:
    hatchback_count, sedan_count, suv_count = 0, 0, 0

    vehicles: List[Vehicle] = Vehicle.query.all()

    for v in vehicles:
        if v.type == 'Hatchback':
            hatchback_count += 1
        elif v.type == 'Sedan':
            sedan_count += 1
        else:
            suv_count += 1

    return {
               'hatchbacks': hatchback_count,
               'sedans': sedan_count,
               'suvs': suv_count
           }, 200


@app.route('/token/register', methods=['POST'])
def register_token() -> Tuple[dict, int]:
    email_id: str = request.form.get('email_id')
    token: str = request.form.get('token')

    if token is None or id is None:
        return bad_request_error('Request parameters are missing!')

    firebase_token: FirebaseToken = FirebaseToken.query.filter_by(user_email=email_id).first()
    if firebase_token is not None:
        firebase_token.token = token
    else:
        firebase_token: FirebaseToken = FirebaseToken(user_email=email_id, token=token)
        db.session.add(firebase_token)
    db.session.commit()

    return {}, 204
