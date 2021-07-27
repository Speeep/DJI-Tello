import djitellopy as tello
from time import sleep

# Initialize and connect to my_drone
my_drone = tello.Tello()
my_drone.connect(True)

# Command the drone to takeoff
my_drone.takeoff()

# Command the drone to fly forward at 40% speed for 3 seconds
sleep(0.5)
my_drone.send_rc_control(0, 40, 0, 0)
sleep(3)
my_drone.send_rc_control(0, 0, 0, 0)
sleep(0.5)


# Command the drone to land
my_drone.land()
