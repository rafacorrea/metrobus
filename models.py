from sqlalchemy.dialects.postgresql import JSON
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Zone(db.Model):
    __tablename__ = 'zone'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String())
    shape = db.Column(JSON)

    def __init__(self, name, shape):
        self.name = name
        self.shape = shape

    def __repr__(self):
        return '<id {}>'.format(self.id)
