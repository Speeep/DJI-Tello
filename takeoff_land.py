import djitellopy as tello
from time import sleep

# Initialize and connect to my_drone
my_drone = tello.Tello()
my_drone.connect(True)

# Command the drone to takeoff
my_drone.takeoff()

# Wait three seconds
sleep(3)

# Command the drone to land
my_drone.land()
