from flask import Flask, request, jsonify
from flask_cors import CORS
import json
from Sim1 import simulate

app = Flask(__name__)
CORS(app)

@app.route('/receive_data', methods=['POST'])
def receive_data():
    data = request.json
    geofence = data.get("geofence", [])
    droneMarkers = data.get("droneMarkers", [])
    events = data.get("events", {})
    with open('data.json', 'w') as f:
        json.dump(data, f, indent=4)
    print(data)
    print("Geofence:", geofence)
    print("Drone Markers:", droneMarkers)
    print("Events:", events)

    # Process the data as needed...

    
    return jsonify({"message": "Data received!"})
   
@app.route('/launch', methods=['POST'])
def send_message():
    # Assuming the data is sent as JSON
    data = request.json
    message = data.get("message", "")
    if message=="yes":
        try:
            simulate()
            return jsonify({"message": "Simulation successful!"})
        except Exception as e:
            return jsonify({"message": f"Error during simulation: {str(e)}"})
        
        
    # Process the message as needed...

    return jsonify({"message": f"Message received: {message}"})


if __name__ == "__main__":
    app.run(debug=True)
