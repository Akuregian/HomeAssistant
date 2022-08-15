#__init__.py tells this is a package and not just a random folder

import os
import markdown
import shelve

#import RaspberryPi GPIO framework
from RaspberryPi_GPIO import GPIO_Commands

#import framework
from flask import Flask, g, render_template, make_response
from flask_restful import Resource, Api, reqparse

# Create instance of Flask
app = Flask(__name__, template_folder="../templates", static_folder="../static")
# Create instance of API
api = Api(app)

# Raspiberry Pi Class in RaspberryPi_GPIO
rpi = GPIO_Commands()

# --------------- Calls to the database ------------------
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = shelve.open("devices.db", writeback=True)
    return db

@app.teardown_appcontext
def teardown_db(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# -------------------- Display README.md at homepage ------------------------------
@app.route("/")
def HomePage():
    return render_template('Homepage.html')

# -------------------- Toggle State Of Device ------------------------------
@app.route('/devices/<string:identifier>/<int:status>')
def Toggle_Pin(identifier, status):
    shelf = get_db()

    # If the key does not exist in the data store, return a 404 error.
    if not (identifier in shelf):
        return {'message': 'Device not found', 'data': {}}, 404

    shelf[identifier]['status'] = status
    pipe_address = int(shelf[identifier]['writing_pipe_address'], 16)
    #pipe_address = int(pipe_address, 16)
    
    rpi.CommunicateWithArduino(pipe_address)

    headers = {'Content-Type': 'text/html'}
    return make_response(render_template("Homepage.html"), 200, headers)

# -------------------- Methods = [GET, POST] - On Devices ------------------------------
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
        parser.add_argument('identifier', required=True, help="Type must be a String")
        parser.add_argument('device_type', required=True, help="Type must be a String")
        parser.add_argument('writing_pipe_address', required=True, help="Type must be a Integer")
        parser.add_argument('reading_pipe_address', required=True, help="Type must be a Integer")
        parser.add_argument('GPIO_Pin', required=True, type=int, help="Type must be a Integer")
        parser.add_argument('status', required=True, type=int, help="Type must be a Integer and only a 0 or 1", choices=[0, 1])

        args = parser.parse_args()

        shelf = get_db()
        shelf[args['identifier']] = args

        return {'message' : 'Device Registered', 'data' : args }, 201

# -------------------- Methods = [GET, DELETE] - On Specific Devices ------------------------------
class Device(Resource):
    def get(self, identifier):
        shelf = get_db()

        # If the key does not exist in the data store, return a 404 error.
        if not (identifier in shelf):
            return {'message': 'Device not found', 'data': {}}, 404
        
        device_status = shelf[identifier]["status"]

        return { "status" : device_status }, 200

        #return {'message': 'Device found', 'data': shelf[identifier]}, 200

    def delete(self, identifier):
        shelf = get_db()

        # If the key does not exist in the data store, return a 404 error.
        if not (identifier in shelf):
            return {'message': 'Device not found', 'data': {}}, 404

        del shelf[identifier]
        return '', 204


api.add_resource(DeviceList, '/devices')
api.add_resource(Device, '/devices/<string:identifier>')