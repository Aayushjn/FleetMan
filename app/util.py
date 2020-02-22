def extract_twin_data(twin_data: dict) -> dict:
    return {
        'brakes': twin_data['brakes']['properties'],
        'engine': twin_data['engine']['properties'],
        'fuel': twin_data['fuel']['properties'],
        'tyres': twin_data['tyres']['properties']
    }