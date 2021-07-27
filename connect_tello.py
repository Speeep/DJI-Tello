import djitellopy as tello
from time import sleep

# Initialize my_drone
my_drone = tello.Tello()

# Connect to my_drone
my_drone.connect(True)

# Print battery percentage to confirm connection
while True:
    print(my_drone.get_battery())
    sleep(3)
