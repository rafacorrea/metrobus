from flask import Flask
from flask import request, jsonify
from celery import Celery
from flask_migrate import Migrate
from geoalchemy2.shape import from_shape
from shapely.geometry import asShape
import requests
import json
import geojson
import csv
import os

from models import Zone

app = Flask(__name__)

if app.config["ENV"] == "production":
    app.config.from_object("config.ProductionConfig")
else:
    app.config.from_object("config.DevelopmentConfig")

from models import db
migrate = Migrate(app, db)

db.init_app(app)
migrate = Migrate(app, db)

celery = Celery(
    app.import_name,
    backend=app.config['CELERY_RESULT_BACKEND'],
    broker=app.config['CELERY_BROKER_URL']
)

celery.conf.update(app.config)

@celery.task()
def fetch_locations():
    # Request data about zones
    url = 'https://datos.cdmx.gob.mx/api/records/1.0/download/?dataset=prueba_fetchdata_metrobus'
    r = requests.get(url, allow_redirects=True)

    decoded_content = r.content.decode('utf-8')

    cr = csv.reader(decoded_content.splitlines(), delimiter=';')

    # Skips headers
    next(cr)

    # Insert all records
    for row in cr:
        shape = geojson.loads(row[5])
        geom = from_shape(asShape(shape), srid=4326)
        exists = Vehicle.query.filter(Vehicle.api_id == row[1]).scalar() is not None

        if not exists:
            newVehicle = Vehicle(api_id = row[1],
                        label = row[2],
                        )

        db.session.add(newvehicle)
        db.session.commit()
        db.session.flush()

        veh_id = Vehicle.query.filter(Vehicle.api_id == row[1]).first().id

        loc_str = 'POINT(' + row[4] + ',' + row[5] + ')'
        newPosition = Position(last_updated=row[0], location=loc_str)

        db.session.add(newPosition)
        db.session.commit()
        db.session.flush()

@app.route("/")
def hello():
    return "Hello World!!!"

@app.route("/api/alcaldias")
def alcaldias():
    res = Zone.query.all()

    return jsonify([zone.as_dict() for zone in res])

@app.route("/api/alcaldias/<alc_id>")
def alcaldias_show(alc_id):
    res = Zone.query.get(alc_id)

    return jsonify(res.as_dict())


@app.route("/api/metrobuses/<mb_id>")
def mb_show(mb_id):
    res = Vehicle.query.get(mb_id)
    return jsonify(res.as_dict())

@app.cli.command("update_zones")
def update_zones():
    # Request data about zones
    url = 'https://datos.cdmx.gob.mx/api/records/1.0/download/?dataset=alcaldias'
    r = requests.get(url, allow_redirects=True)

    decoded_content = r.content.decode('utf-8')

    cr = csv.reader(decoded_content.splitlines(), delimiter=';')

    # Skips headers
    next(cr)

    # Remove old data
    Zone.query.delete()

    # Insert all records
    for row in cr:
        shape = geojson.loads(row[5])
        geom = from_shape(asShape(shape), srid=4326)
        newZone = Zone(name = row[0],
                    shape = geom,
                    )

        db.session.add(newZone)
        db.session.commit()
        db.session.flush()

@app.cli.command("test_celery")
def test_celery():
    result = fetch_locations.delay()
    result.wait()  # 65

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int("5000"), debug=True)
