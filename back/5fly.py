from dronekit import Vehicle, VehicleMode, connect, LocationGlobalRelative
import threading
import time

def arm_and_takeoff(vehicle, target_altitude):
    """
    Arms vehicle and fly to aTargetAltitude.
    """

    print("Basic pre-arm checks")
    # Don't try to arm until autopilot is ready
    while not vehicle.is_armable:
        print("Waiting for vehicle to initialise...")
        time.sleep(1)

    print("Arming motors")
    # Copter should arm in GUIDED mode
    vehicle.mode = VehicleMode("GUIDED")
    vehicle.armed = True

    # Confirm vehicle armed before attempting to take off
    while not vehicle.armed:
        print("Waiting for arming...")
        time.sleep(1)

    print("Taking off!")
    vehicle.simple_takeoff(target_altitude)  # Take off to target altitude

    # Wait until the vehicle reaches a safe height before processing the goto (otherwise the command
    #  after Vehicle.simple_takeoff will execute immediately).
    while True:
        print("Altitude: ", vehicle.location.global_relative_frame.alt)
        # Break and return from function just below target altitude.
        if vehicle.location.global_relative_frame.alt >= target_altitude * 0.95:
            print("Reached target altitude")
            break
        time.sleep(1)

    print("Setting mode to RTL (Return to Launch)")
    vehicle.mode = VehicleMode("RTL")

def return_to_launch_and_land(vehicle):
    print("Returning to Launch (RTL) and landing...")

    # Set the mode to RTL
    vehicle.mode = VehicleMode("RTL")

    # Wait for the vehicle to reach the RTL altitude
    while True:
        print("Altitude: ", vehicle.location.global_relative_frame.alt)
        if vehicle.location.global_relative_frame.alt <= 14:
            print("Reached RTL altitude, initiating landing")
            break
        time.sleep(1)

    # Set mode to LAND
    vehicle.mode = VehicleMode("LAND")

    # Wait for the vehicle to land
    while vehicle.armed:
        print("Altitude: ", vehicle.location.global_relative_frame.alt)
        time.sleep(1)
    print(vehicle.location.global_frame)
    print("Landed at home location")

def simulate_single_drone(connection_string, target_altitude):
    vehicle = connect(connection_string, wait_ready=True)
    arm_and_takeoff(vehicle, target_altitude)
    return_to_launch_and_land(vehicle)
    vehicle.close()

def simulate_all_drones():
    connection_strings = ['tcp:127.0.0.1:5760', 'tcp:127.0.0.1:5761', 'tcp:127.0.0.1:5762', 'tcp:127.0.0.1:5763', 'tcp:127.0.0.1:5764']
    target_altitude = 10

    # Create a thread for each drone
    threads = []
    for idx, connection_string in enumerate(connection_strings):
        thread = threading.Thread(target=simulate_single_drone, args=(connection_string, target_altitude))
        threads.append(thread)

    # Start all threads
    for thread in threads:
        thread.start()

    # Wait for all threads to finish
    for thread in threads:
        thread.join()

if __name__ == "__main__":
    simulate_all_drones()
