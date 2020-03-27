from typing import Tuple, Optional

from app.models import Vehicle


def extract_twin_data(twin_data: dict) -> dict:
    return {
        'brakes': twin_data['brakes']['properties'],
        'engine': twin_data['engine']['properties'],
        'fuel': twin_data['fuel']['properties'],
        'tyres': twin_data['tyres']['properties']
    }


def map_vehicle_data_to_role(role: str, twin_data: dict, vehicle: Vehicle) -> dict:
    twin_system_data = extract_twin_data(twin_data)
    vehicle.calculate_health(twin_system_data)

    twin_system_data['brakes']['health'] = vehicle.brakes_health
    twin_system_data['engine']['health'] = vehicle.engine_health
    twin_system_data['fuel']['health'] = vehicle.fuel_health
    twin_system_data['tyres']['health'] = vehicle.tyres_health

    if role == 'INSURANCE':
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
        }
    elif role == 'ADMIN':
        return {
            **vehicle.to_dict(),
            **twin_system_data
        }
    elif role == 'MAINTENANCE':
        # noinspection PyDictCreation
        ret_val = {
            **vehicle.to_dict(),
            **twin_system_data
        }
        ret_val['vin'] = None
        ret_val['license_plate'] = None
        ret_val['driver'] = None
        ret_val['type'] = None

        return ret_val
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
        }


def get_alert_type_and_msg(delta_brakes: float,
                           delta_engine: float,
                           delta_fuel: float,
                           delta_tyre: float,
                           delta_overall: float) -> Tuple[Optional[str], Optional[str]]:
    if 5 <= delta_overall < 10 or \
            5 <= delta_brakes < 10 or \
            5 <= delta_engine < 10 or \
            5 <= delta_fuel < 10 or \
            5 <= delta_tyre < 10:
        alert_type = 'WARNING'
    elif delta_overall >= 10 or \
            delta_brakes >= 10 or \
            delta_engine >= 10 or \
            delta_fuel >= 10 or \
            delta_tyre >= 10:
        alert_type = 'SEVERE'
    else:
        return None, None

    warning_msg = 'Issues identified with: '
    if delta_brakes >= 5:
        warning_msg = warning_msg + 'Braking system, '
    if delta_engine >= 5:
        warning_msg = warning_msg + 'Engine and Transmission, '
    if delta_fuel >= 5:
        warning_msg = warning_msg + 'Fuel system, '
    if delta_tyre >= 5:
        warning_msg = warning_msg + 'Tyre system, '
    if delta_overall >= 5:
        warning_msg = warning_msg + 'Overall health'
    else:
        warning_msg = warning_msg[:-2]

    return alert_type, warning_msg
