from app import db


class User(db.Model):
    email_id = db.Column(db.String(254), primary_key=True)
    name = db.Column(db.String(70), nullable=False)
    password = db.Column(db.String(80), nullable=False)
    role = db.Column(db.String(11), nullable=False)

    def __repr__(self) -> str:
        return f'User(email_id={self.email_id}, name={self.name}, role={self.role})'

    def to_dict(self) -> dict:
        return {
            'email_id': self.email_id,
            'name': self.name,
            'role': self.role
        }


class Vehicle(db.Model):
    vin = db.Column(db.String(17), primary_key=True)
    license_plate = db.Column(db.String(11), unique=True, nullable=False)
    driver = db.Column(db.String(70), nullable=False)
    model = db.Column(db.String(40), nullable=False)
    type = db.Column(db.String(9), nullable=False)
    brakes_health = db.Column(db.Float(3))
    engine_health = db.Column(db.Float(3))
    fuel_health = db.Column(db.Float(3))
    tyres_health = db.Column(db.Float(3))
    overall_health = db.Column(db.Float(3))

    def __repr__(self) -> str:
        return f'Vehicle(vin={self.vin}, license_plate={self.license_plate}, driver={self.driver}, model={self.model}' \
               f', type={self.type}, brakes_health={self.brakes_health}, engine_health={self.engine_health}, ' \
               f'fuel_health={self.fuel_health}, tyres_health={self.tyres_health}, ' \
               f'overall_health={self.overall_health})'

    def calculate_health(self, twin_system_data: dict):
        self.fuel_health = 1 - ((twin_system_data['fuel']['level'] - 50) / 100)
        self.tyres_health = 1 - ((twin_system_data['tyres']['pressure'] - 32.5) / 100)

        r1 = 1 - ((twin_system_data['engine']['temp'] - 95) / 100)
        r2 = 1 - ((twin_system_data['engine']['battery_capacity'] - 95) / 100)
        self.engine_health = (r1 + r2) / 2

        r1 = 1 - ((twin_system_data['brakes']['temp'] - 140) / 100)
        r2 = 1 - (twin_system_data['brakes']['fluid_level'] / 100)
        self.brakes_health = (r1 + r2) / 2

        self.overall_health = (self.fuel_health + self.tyres_health + self.engine_health + self.tyres_health) / 4

    def to_dict(self) -> dict:
        return {
            'vin': self.vin,
            'license_plate': self.license_plate,
            'driver': self.driver,
            'model': self.model,
            'type': self.type,
            'overall_health': self.overall_health
        }

    def to_minimal_model(self) -> dict:
        return {
            'vin': self.vin,
            'license_plate': self.license_plate,
            'model': self.model
        }
