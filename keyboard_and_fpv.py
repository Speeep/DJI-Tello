from djitellopy import tello
import cv2
import keyboard as kb


# Function to read keyboard input to allow the drone to be controlled
def get_keyboard_input():

    lr, fb, ud, yv = 0, 0, 0, 0
    speed = 50

    if kb.is_pressed('left'):
        lr = -speed

    elif kb.is_pressed('right'):
        lr = speed

    if kb.is_pressed('up'):
        fb = speed

    elif kb.is_pressed('down'):
        fb = -speed

    if kb.is_pressed('w'):
        ud = speed

    elif kb.is_pressed('s'):
        ud = -speed

    if kb.is_pressed('a'):
        yv = -speed

    elif kb.is_pressed('d'):
        yv = speed

    if kb.is_pressed('q'):
        my_drone.land()

    if kb.is_pressed('e'):
        my_drone.takeoff()

    return [lr, fb, ud, yv]


# Initialize and connect to my_drone
my_drone = tello.Tello()
my_drone.connect()

# Check battery to confirm connection
print(my_drone.get_battery())

# Turn on video streaming
my_drone.streamon()

while True:

    # Get and resize image from my_drone
    img = my_drone.get_frame_read().frame
    img = cv2.resize(img, (360, 240))

    # Display video in cv2 window
    cv2.imshow("Image", img)
    cv2.waitKey(1)

    # Send remote control to drone via keys pressed
    vals = get_keyboard_input()
    my_drone.send_rc_control(vals[0], vals[1], vals[2], vals[3])
