#__init__.py tells this is a package and not just a random folder

import os
import markdown
import shelve

# Raspberry Pi GPIO framework
import RPi.GPIO as GPIO

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

# -------------------- Display README.md at homepage ------------------------------
@app.route("/")
def HomePage():
    # Open the README file
    with open(os.path.dirname(app.root_path) + '/README.md', 'r') as markdown_file:

        # Read the content of the file
        content = markdown_file.read()

        # Convert to HTML
        return markdown.markdown(content)

# -------------------- GET, POST Devices ------------------------------
class DeviceList(Resource):
    # GET's all the devices stores in the database
    def get(self):
        shelf = get_db()
        keys = list(shelf.keys())

        devices = []

        for key in keys:
            devices.append(shelf[key])

        return { 'message': 'Success', 'data': devices }

    def post(self):
        # Request Parser
        parser = reqparse.RequestParser()

        # Arguments for database, basically the table structure
        parser.add_argument('identifier', required=True)
        parser.add_argument('device_type', required=True)
        parser.add_argument('pipe_address', required=True)
        parser.add_argument('GPIO_Pin', required=True)
        parser.add_argument('status', required=True)

        args = parser.parse_args()

        shelf = get_db()
        shelf[args['identifier']] = args

        return {'message' : 'Device Registered', 'data' : args }, 201

# -------------------- GET, DELETE Specific Device ------------------------------
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
        
class ToggleDeviceStatus(Resource):
    def get(self, identifier, status):
        shelf = get_db()

        # If the key does not exist in the data store, return a 404 error.
        if not (identifier in shelf):
            return {'message': 'Device not found', 'data': {}}, 404

        shelf[identifier]["status"] = status

        return { "message" : "Changed Device Status", "data" : shelf[identifier] }, 200




api.add_resource(DeviceList, '/devices')
api.add_resource(Device, '/devices/<string:identifier>')
api.add_resource(ToggleDeviceStatus, '/devices/<string:identifier>/<string:status>')