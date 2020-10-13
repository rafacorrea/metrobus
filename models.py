from sqlalchemy.dialects.postgresql import JSON
from flask_sqlalchemy import SQLAlchemy
from geoalchemy2 import Geometry

db = SQLAlchemy()

class Zone(db.Model):
    __tablename__ = 'zone'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String())
    shape = db.Column(Geometry(geometry_type='POLYGON', srid=4326))

    def as_dict(self):
        return {'id': self.id, 'name': self.name}
        # return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def __init__(self, name, shape):
        self.name = name
        self.shape = shape

    def __repr__(self):
        return '<id {}>'.format(self.id)

class Vehicle(db.Model):
    __tablename__ = 'vehicle'

    id = db.Column(db.Integer, primary_key=True)
    label = db.Column(db.String())
    api_id= db.Column(db.Integer, index=True)
    positions = db.relationship('Position', backref='vehicle', lazy=True)

    def as_dict(self):
        return {'id': self.id, 'api_id': self.api_id}
        # return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def __init__(self, api_id, label):
        self.api_id = api_id
        self.label = label

    def __repr__(self):
        return '<id {}>'.format(self.id)

class Position(db.Model):
    __tablename__ = 'position'

    id = db.Column(db.Integer, primary_key=True)
    last_updated=db.Column(db.DateTime)
    location = db.Column(Geometry(geometry_type='POINT', srid=4326))
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicle.id'),
        nullable=False)

    def as_dict(self):
        return {'id': self.id, 'api_id': self.api_id}
        # return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def __init__(self, last_updated, location, vehicle_id):
        self.last_updated = last_updated
        self.location = location
        self.vehicle_id = vehicle_id

    def __repr__(self):
        return '<id {}>'.format(self.id)
