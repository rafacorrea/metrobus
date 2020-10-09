from flask import Flask
from flask import request, jsonify

app = Flask(__name__)
@app.route("/")
def hello():
    return "Hello World!!!"

@app.route("/api/alcaldias")
def alcaldias():
    alcaldias = [
        { 'id': 0,
          'name': 'Miguel Hidalgo'
        },
        { 'id': 1,
          'name': 'Miguel Hidalgo2'
        }
    ]

    return jsonify(alcaldias)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int("5000"), debug=True)
