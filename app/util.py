def extract_twin_data(twin_data: dict) -> dict:
    return {
        'brakes': {
            'fluid_level': twin_data['brakes']['properties']['fluid_level'],
            'temp': twin_data['brakes']['properties']['temp'],
            'type': twin_data['brakes']['properties']['type']
        },
        'engine': {
            'battery_capacity': twin_data['engine']['properties']['battery_capacity'],
            'current_level': twin_data['engine']['properties']['current_level'],
            'temp': twin_data['engine']['properties']['temp']
        },
        'fuel': {
            'capacity': twin_data['fuel']['properties']['capacity'],
            'level': twin_data['fuel']['properties']['level'],
            'rating': twin_data['fuel']['properties']['rating'],
            'type': twin_data['fuel']['properties']['type']
        },
        'tyres': {
            'pressure': twin_data['tyres']['properties']['pressure'],
            'rating': twin_data['tyres']['properties']['rating'],
            'temp': twin_data['tyres']['properties']['temp'],
            'wear': twin_data['tyres']['properties']['wear']
        }
    }