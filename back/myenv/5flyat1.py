import json
from dronekit_sitl import SITL
from dronekit import connect, VehicleMode
import time

# Function to create a vehicle at a specific location
def create_vehicle(lat, lon, altitude, connection_string):
    sitl = SITL()
    sitl.download('copter', '3.3', verbose=True)
    sitl_args = ['-I0', '--model', 'quad', '--home', f'{lat},{lon},{altitude},180']
    sitl.launch(sitl_args, await_ready=True)
    connection_string = connection_string.replace('tcp:', f'tcp:127.0.0.1:')
    vehicle = connect(connection_string, wait_ready=True)
    return vehicle

# Function to fly the drone to a specific waypoint
def fly_to_waypoint(vehicle, waypoint):
    location = waypoint['lat'], waypoint['lng'], waypoint['altitude']
    target_location = vehicle.location.global_relative_frame
    target_location.lat, target_location.lon, target_location.alt = location
    vehicle.simple_goto(target_location)

# Main simulation function
def simulate_drones(geofence, drone_markers, connection_strings):
    vehicles = []
    for i, connection_string in enumerate(connection_strings):
        formation = str(i + 1)
        for j, waypoint in enumerate(drone_markers['formations'][formation]):
            lat, lon, altitude = waypoint['lat'], waypoint['lng'], waypoint['altitude']
            vehicle = create_vehicle(lat, lon, altitude, connection_string)
            vehicles.append(vehicle)

    # Fly drones to waypoints simultaneously
    for i, waypoint in enumerate(drone_markers['formations']['1']):
        for j, connection_string in enumerate(connection_strings):
            formation = str(j + 1)
            fly_to_waypoint(vehicles[i * len(connection_strings) + j], drone_markers['formations'][formation][i])

    # Simulate RTL (Return to Launch)
    time.sleep(5)  # Simulate drones flying to waypoints for 5 seconds
    for vehicle in vehicles:
        vehicle.mode = VehicleMode("RTL")
        while vehicle.mode.name != 'RTL':
            time.sleep(1)

    # Close connections
    for vehicle in vehicles:
        vehicle.close()

if __name__ == "__main__":
    # Read configuration from JSON file
    with open('data.json', 'r') as file:
        config = json.load(file)

    geofence = config["geofence"]
    drone_markers = config["droneMarkers"]
    connection_strings = ['tcp:127.0.0.1:5760', 'tcp:127.0.0.1:5761', 'tcp:127.0.0.1:5762', 'tcp:127.0.0.1:5763', 'tcp:127.0.0.1:5764']

    simulate_drones(geofence, drone_markers, connection_strings)
