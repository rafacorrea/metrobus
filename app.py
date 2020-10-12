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

from models import db  # <-- this needs to be placed after app is created
migrate = Migrate(app, db)

db.init_app(app)
migrate = Migrate(app, db)

# celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
# celery.conf.update(app.config)

@app.route("/")
def hello():
    return "Hello World!!!"

@app.route("/api/alcaldias")
def alcaldias():
    res = Zone.query.all()

    return jsonify(res)

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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int("5000"), debug=True)
