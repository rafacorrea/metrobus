from flask import Flask
from flask import request, jsonify
from celery import Celery
from flask_migrate import Migrate
import requests
import json
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
def add_together(a, b):
    return a + b

@app.route("/")
def hello():
    return "Hello World!!!"

@app.route("/api/alcaldias")
def alcaldias():
    res = Zone.query.all()

    return jsonify([zone.as_dict() for zone in res])

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
        shape = json.loads(row[5])
        newZone = Zone(name = row[0],
                    shape = shape,
                    )

        db.session.add(newZone)
        db.session.commit()
        db.session.flush()

# @app.cli.command("test_celery")
# def test_celery():
#     result = add_together.delay(23, 42)
#     result.wait()  # 65

if __name__ == "__main__":
    aplication.run(host="0.0.0.0", port=int("5000"), debug=True)
