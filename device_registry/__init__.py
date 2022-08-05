#__init__.py tells this is a package and not just a random folder

import os
import markdown
import shelve

#import framework
from flask import Flask, g
from flask_restful import Resource, Api, reqparse

# Create instance of Flask
app = Flask(__name__)


# Create instance of API
api = Api(app)

# --------------- Calls to the database ------------------
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = shelve.open("devices.db")
    return db

@app.teardown_appcontext
def teardown_db(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# -------------------------------------------------------

# route is used on the webpage and allows us to run this function
@app.route("/")
def index():
    with open(os.path.dirname(app.root_path) + '/README.md', 'r') as markdown:
        content = markdown.read()
        return markdown.markdown(content)

# GET, POST DELETE
class DeviceList(Resource):
    # GET's all the devices stores in the database
    def get(self):
        shelf = get_db()
        keys = list(shelf.keys())

        devices = []

        for key in keys:
            devices.append(shelf[key])

        return { 'message': 'Success', 'data': devices }

    # Post a new device to the database
    def post(self):
        parser = reqparse.RequestParser()

        # Arguments for database, basically the table structure
        parser.add_argument('identifier', required=True)
        parser.add_argument('device_type', required=True)
        parser.add_argument('address', required=True)
        parser.add_argument('GPIO_Pin', required=True)
        parser.add_argument('status', required=True)

        args = parser.parse_args()

        shelf = get_db()
        shelf[args['identifier']] = args

        return {'message' : 'Device Registered', 'data' : args }, 201

# Grabs a specific devices in the database
class Device(Resource):
    def get(self, identifier):
        shelf = get_db()

        # If the key does not exist in the data store, return a 404 error.
        if not (identifier in shelf):
            return {'message': 'Device not found', 'data': {}}, 404

        return {'message': 'Device found', 'data': shelf[identifier]}, 200

    def delete(self, identifier):
        shelf = get_db()

        # If the key does not exist in the data store, return a 404 error.
        if not (identifier in shelf):
            return {'message': 'Device not found', 'data': {}}, 404

        del shelf[identifier]
        return '', 204

api.add_resource(DeviceList, '/devices')
api.add_resource(Device, '/devices/<string:identifier>')