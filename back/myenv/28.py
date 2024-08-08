from __future__ import print_function
from dronekit import connect, VehicleMode, LocationGlobalRelative, LocationGlobal, Command
import time
import math
from pymavlink import mavutil
import argparse

from Way import adds_square_mission, get_distance_metres

# Set up option parsing to get connection string
parser = argparse.ArgumentParser(description='Demonstrates basic swarm mission operations.')
parser.add_argument('--num_drones', type=int, default=5, help='Number of drones in the swarm')
parser.add_argument('--connect', help="Vehicle connection target string. If not specified, SITL automatically started and used.")
args = parser.parse_args()

num_drones = args.num_drones
connection_string = args.connect
sitl = None

# Start SITL if no connection string specified
if not connection_string:
    import dronekit_sitl
    sitl = dronekit_sitl.start_default()
    connection_string = sitl.connection_string()

# Connect to the Vehicles
vehicles = [connect(f'tcp:127.0.0.1:{5760 + i}', wait_ready=True) for i in range(num_drones)]

# Function to calculate distance between two points
def distance_between_points(point1, point2):
    dlat = point2.lat - point1.lat
    dlon = point2.lon - point1.lon
    return math.sqrt((dlat * dlat) + (dlon * dlon)) * 1.113195e5

# Function to avoid collisions between two drones
def avoid_collision(vehicle, other_vehicle, safe_distance=5):
    current_location = vehicle.location.global_relative_frame
    other_location = other_vehicle.location.global_relative_frame
    distance = distance_between_points(current_location, other_location)
    if distance < safe_distance:
        new_heading = current_location.bearing_to(other_location) + 90.0
        vehicle.simple_goto(LocationGlobalRelative(
            current_location.lat + 0.00001 * distance * (vehicle.heading - new_heading),
            current_location.lon + 0.00001 * distance * (new_heading - vehicle.heading),
            current_location.alt
        ))

# Function to perform swarm takeoff
def swarm_takeoff(vehicles, target_altitude):
    for vehicle in vehicles:
        vehicle.mode = VehicleMode("GUIDED")
        vehicle.armed = True
        while not vehicle.armed:
            time.sleep(1)
        vehicle.simple_takeoff(target_altitude)

# Function to perform swarm mission
def swarm_mission(vehicles):
    for vehicle in vehicles:
        vehicle.commands.next = 0
        vehicle.mode = VehicleMode("AUTO")

    while not all(vehicle.location.global_relative_frame.alt >= 10 * 0.95 for vehicle in vehicles):
        print("Waiting for vehicles to reach target altitude")
        time.sleep(1)

    while True:
        for i, vehicle in enumerate(vehicles):
            for j, other_vehicle in enumerate(vehicles):
                if i != j:
                    avoid_collision(vehicle, other_vehicle)

        next_waypoints = [vehicle.commands.next for vehicle in vehicles]
        print('Distance to waypoints:', [distance_to_current_waypoint(vehicle) for vehicle in vehicles])

        if all(waypoint == 5 for waypoint in next_waypoints):
            print("Exit 'standard' mission when start heading to final waypoint (5)")
            break
        time.sleep(1)

    print('Return to launch')
    for vehicle in vehicles:
        vehicle.mode = VehicleMode("RTL")

    time.sleep(5)  # Allow time for vehicles to land

# Function to get distance to current waypoint for a specific vehicle
def distance_to_current_waypoint(vehicle):
    next_waypoint = vehicle.commands.next
    if next_waypoint == 0:
        return None
    mission_item = vehicle.commands[next_waypoint - 1]
    lat, lon, alt = mission_item.x, mission_item.y, mission_item.z
    target_waypoint_location = LocationGlobalRelative(lat, lon, alt)
    distance_to_point = get_distance_metres(vehicle.location.global_frame, target_waypoint_location)
    return distance_to_point

try:
    # Swarm takeoff
    swarm_takeoff(vehicles, 10)

    # Create a new mission for each drone
    for i, vehicle in enumerate(vehicles):
        print(f'Create a new mission for drone {i + 1}')
        adds_square_mission(vehicle.location.global_frame, 50)

    # Execute swarm mission
    swarm_mission(vehicles)

finally:
    # Close connections
    for vehicle in vehicles:
        vehicle.close()

    # Shut down simulator if it was started.
    if sitl is not None:
        sitl.stop()
