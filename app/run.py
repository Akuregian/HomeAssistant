from api import app, socketio

socketio.run(app, host='0.0.0.0', port=5001, debug=True)
