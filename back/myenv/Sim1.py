from dronekit import Vehicle,VehicleMode,connect,LocationGlobalRelative
import time
import json

def simulate():
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
            if vehicle.location.global_relative_frame.alt <=14:
                print("Reached RTL altitude, initiating landing")
                break
            time.sleep(1)

        # Set mode to LAND
        vehicle.mode = VehicleMode("LAND")

        # Wait for the vehicle to land
        while vehicle.armed:
            print("Altitude: ", vehicle.location.global_relative_frame.alt)
            time.sleep(1)
        print( vehicle.location.global_frame)
        print("Landed at home location")

    # Connect to the Vehicle (in this case a simulator running on the same computer)
    vehicle = connect('tcp:127.0.0.1:5760', wait_ready=True)

    # Read home location from JSON file
    # with open('data.json', 'r') as f:
    #     data = json.load(f)

    
    # formations = data.get("droneMarkers", {}).get("formations", {})
    # home_location = None

    # if formations:
    #     formation_1 = formations.get("1", [])
    #     if formation_1:
    #         first_location = formation_1[0]
    #         home_location = LocationGlobalRelative(float(first_location["lat"]), float(first_location["lng"]), 0)
    #         print(home_location)
    # Set the home location
    # if home_location:
    #     vehicle.home_location = home_location
    #     vehicle.location.global_frame = home_location
    # else:
    #     print("Warning: Home location not set. Make sure the JSON data is correctly formatted.")


    # Define target altitude
    target_altitude = 10

    # Call the modified arm_and_takeoff function
    arm_and_takeoff(vehicle, target_altitude)

    # Call the return_to_launch_and_land function
    return_to_launch_and_land(vehicle)