from flask import Flask, abort, request, jsonify, render_template
from celery import Celery
from celery.decorators import periodic_task
from flask_migrate import Migrate
from geoalchemy2.shape import from_shape, to_shape
from shapely.geometry import asShape, Point
import requests
import json
import geojson
import csv
import os

from models import Zone, Vehicle, Position

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

@app.errorhandler(404)
def page_not_found(error):
   return render_template('404.html', title = '404'), 404

@app.route("/")
def hello():
    return render_template('index.html', title = 'metrobus'), 200

@app.route("/api/alcaldias")
def alcaldia_list():
    # Get all zones
    res = Zone.query.all()

    return jsonify([zone.as_dict() for zone in res])

@app.route("/api/alcaldias/<alc_id>")
def alcaldia_show(alc_id):
    # Get specific record for Zone
    res = Zone.query.get(alc_id)
    if res is None:
        abort(404)
    return jsonify(res.as_dict())


@app.route("/api/metrobuses/<mb_id>/historial")
def mb_show(mb_id):
    # Get specific record for Vehicle and its history of positions
    res = Vehicle.query.get(mb_id)
    if res is None:
        abort(404)
    return jsonify([pos.as_dict() for pos in res.positions])

@app.route("/api/metrobuses")
def mb_list():
    res = Vehicle.query.all()

    # If request params contains filter by zone_id...
    if request.args.get('zone_id'):
        zone = Zone.query.get(int(request.args.get('zone_id')))
        if zone is None:
            abort(404)
        res = Vehicle.query.join(Vehicle.positions).filter(Position.location.ST_Within(zone.shape))
    else:
        res = Vehicle.query.all()
    return jsonify([mb.as_dict() for mb in res])

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

@celery.task(name='periodic_task')
# @app.cli.command("fetch_locations")
def periodic_task():
    with app.app_context():
        # Request data about zones
        url = 'https://datos.cdmx.gob.mx/api/records/1.0/download/?dataset=prueba_fetchdata_metrobus'
        r = requests.get(url, allow_redirects=True)

        decoded_content = r.content.decode('utf-8')

        cr = csv.reader(decoded_content.splitlines(), delimiter=';')

        # Skips headers
        next(cr)

        # Insert all records
        for row in cr:
            exists = Vehicle.query.filter(Vehicle.api_id == row[1]).scalar() is not None

            # Create vehicle if doesnt exist (lookup by api_id)
            if not exists:
                newVehicle = Vehicle(api_id = row[1],
                            label = row[2],
                            )

                db.session.add(newVehicle)
                db.session.commit()

            veh_id = Vehicle.query.filter(Vehicle.api_id == row[1]).first().id

            # Create shapely shape to and convert to geoalchemy2 shape
            geom = from_shape(Point(float(row[5]), float(row[4])), srid=4326)
            newPosition = Position(last_updated=row[0], location=geom, vehicle_id=veh_id)

            db.session.add(newPosition)
            db.session.commit()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int("5000"), debug=True)
