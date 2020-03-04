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
