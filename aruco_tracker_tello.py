import matplotlib.pyplot as plt
import time as t
import numpy as np
import djitellopy as tello
import cv2
import cv2.aruco as aruco
import keyboard as kb
import marker as mk


# Function for plotting error vs time for each of throttle, yaw, pitch, and roll
def plot_flight(time, throttle_e, yaw_e, pitch_e, roll_e):
    throttle_e = throttle_e
    yaw_e = yaw_e
    pitch_e = pitch_e
    roll_e = roll_e

    t_fig, t_ax = plt.subplots()
    t_ax.plot(time, throttle_e)
    t_ax.set(xlabel='time (ms)', ylabel='throttle_error (pixels)', title='Throttle Error')
    t_ax.grid()
    t_fig.savefig("error_plots/throttle_error_plot.png")

    y_fig, y_ax = plt.subplots()
    y_ax.plot(time, yaw_e)
    y_ax.set(xlabel='time (ms)', ylabel='yaw_error (pixels)', title='Yaw Error')
    y_ax.grid()
    y_fig.savefig("error_plots/yaw_error_plot.png")

    p_fig, p_ax = plt.subplots()
    p_ax.plot(time, pitch_e)
    p_ax.set(xlabel='time (ms)', ylabel='pitch_error (pixels)', title='Pitch Error')
    p_ax.grid()
    p_fig.savefig("error_plots/pitch_error_plot.png")

    r_fig, r_ax = plt.subplots()
    r_ax.plot(time, roll_e)
    r_ax.set(xlabel='time (ms)', ylabel='roll_error (pixels)', title='Roll Error')
    r_ax.grid()
    r_fig.savefig("error_plots/roll_error_plot.png")


# Function for receiving keyboard inputs for controlling the drone and entering autonomous mode
def get_keyboard_input(autonomous_control):
    plot_data = True
    auto = autonomous_control
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
        plot_data = True

    if kb.is_pressed('e'):
        my_drone.takeoff()

    if kb.is_pressed('z'):
        auto = True

    elif kb.is_pressed('p'):
        auto = False

    return [lr, fb, ud, yv], auto, plot_data


# Initialize and connect to my_drone
my_drone = tello.Tello()
my_drone.connect()

# Print battery percentage to confirm connection
print(my_drone.get_battery())

# Turn on video streaming
my_drone.streamon()

# TODO WARNING PID GAINS VARY! MAKE SURE TO TUNE YOUR OWN VALUES IF YOU USE THIS CODE!
# PID Gains
TP = 0.5
TI = 0.0
TD = 1.7

RP = 70
RI = 0.0
RD = 120

PP = 0.0008
PI = 0.0
PD = 0.06

YP = 0.4
YI = 0.0
YD = 1.7

# Define Constants
SCREEN_WIDTH = 720
SCREEN_HEIGHT = 480
TARGET_SIZE = 16000
MAX_EFFORT = 100
MAX_PITCH_EFFORT = 30
DT = 1

# Initialize some variables for later use
prev_yaw_error = 0
prev_throttle_error = 0
prev_pitch_error = 0
prev_roll_error = 0
throttle_integral = 0
yaw_integral = 0
pitch_integral = 0
roll_integral = 0
autonomous_control = False
then = t.time()
time = []
throttle_error_arr = []
yaw_error_arr = []
pitch_error_arr = []
roll_error_arr = []

# Display live feed from front facing camera
while True:

    # Get current time
    now = t.time()

    # Get and resize image from my_drone
    img = my_drone.get_frame_read().frame
    img = cv2.resize(img, (SCREEN_WIDTH, SCREEN_HEIGHT))

    # Detect aruco markers
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    key = getattr(aruco, f'DICT_5X5_100')
    aruco_dict = aruco.Dictionary_get(key)
    aruco_param = aruco.DetectorParameters_create()
    marker_corners, ids, rejected = aruco.detectMarkers(img_gray, aruco_dict, parameters=aruco_param)

    # Assume there are no markers being detected until proven otherwise
    markers_detected = False

    # If markers are detected, create marker objects, draw outlines and centroids, find biggest marker, etc.
    if ids is not None:
        markers_detected = True

        # List to hold all aruco markers that are currently detected
        aruco_markers = []

        # For each ID detected, create a marker object and add it to aruco_markers
        for i in range(len(ids)):
            aruco_markers.append(mk.Marker(ids[i][0], marker_corners[i][0]))

        for marker in aruco_markers:
            # Draw centroids on detected markers
            cv2.circle(img, (marker.x, marker.y), 3, (0, 0, 255), cv2.FILLED)

            # Draw slope of bottom line on detected markers
            cv2.line(img,
                     (int(marker.point_2[0]), int(marker.point_2[1])),
                     (int(marker.point_3[0]), int(marker.point_3[1])),
                     (255, 0, 255), 9)

        # Draw marker outlines on detected markers
        aruco.drawDetectedMarkers(img, marker_corners, ids)

        # Split screen in half width and length wise and draw lines to help with error visualization
        cv2.line(img, (0, (SCREEN_HEIGHT // 2)), (360, (SCREEN_HEIGHT // 2)), (255, 0, 255), 1)
        cv2.line(img, ((SCREEN_WIDTH // 2), 0), ((SCREEN_WIDTH // 2), 360), (255, 0, 255), 1)

        # Find biggest aruco marker
        biggest_marker = aruco_markers[0]
        for marker in aruco_markers:
            if marker.area > biggest_marker.area:
                biggest_marker = marker

    # Display video stream
    cv2.imshow("Image", img)
    cv2.waitKey(DT)

    # Update keyboard events to control drone or enter autonomous mode
    vals, autonomous_control, plot = get_keyboard_input(autonomous_control)

    # When autonomous control is not enabled, keyboard control is used
    if not autonomous_control:
        my_drone.send_rc_control(vals[0], vals[1], vals[2], vals[3])

    # PID to Align with aruco marker
    elif autonomous_control and markers_detected:

        # Definitions of error for each possible effort
        throttle_error = SCREEN_HEIGHT // 2 - biggest_marker.y
        yaw_error = biggest_marker.x - SCREEN_WIDTH // 2
        pitch_error = TARGET_SIZE - biggest_marker.area
        roll_error = 0 - biggest_marker.bottom

        # Keep track of time and error for plotting
        time.append(now - then)
        throttle_error_arr.append(throttle_error)
        yaw_error_arr.append(yaw_error)
        pitch_error_arr.append(pitch_error)
        roll_error_arr.append(roll_error)

        # Iterate integral term
        throttle_integral += throttle_error * DT
        yaw_integral += yaw_error * DT
        pitch_integral += pitch_error * DT
        roll_integral += roll_error * DT

        # Calculate difference in error since last time interval
        throttle_derivative = (throttle_error - prev_throttle_error) / DT
        yaw_derivative = (yaw_error - prev_yaw_error) / DT
        pitch_derivative = (pitch_error - prev_pitch_error) / DT
        roll_derivative = (roll_error - prev_roll_error) / DT

        # PID to update effort values
        throttle_effort = int((TP * throttle_error) + (TI * throttle_integral) - (TD * throttle_derivative))
        yaw_effort = int((YP * yaw_error) + (YI * yaw_integral) - (YD * yaw_derivative))
        pitch_effort = int((PP * pitch_error) + (PI * pitch_integral) - (PD * pitch_derivative))
        roll_effort = int((RP * roll_error) + (RI * roll_integral) - (RD * roll_derivative))
        print(roll_effort)

        # Restrict possible effort values to defined value.
        throttle_effort = int(np.clip(throttle_effort, -MAX_EFFORT, MAX_EFFORT))
        yaw_effort = int(np.clip(yaw_effort, -MAX_EFFORT, MAX_EFFORT))
        pitch_effort = int(np.clip(pitch_effort, -MAX_PITCH_EFFORT, MAX_PITCH_EFFORT))
        roll_effort = int(np.clip(roll_effort, -MAX_EFFORT, MAX_EFFORT))

        # Send effort values to my_drone
        my_drone.send_rc_control(roll_effort, pitch_effort, throttle_effort, yaw_effort)

        # Update prev error values for next loop
        prev_throttle_error = throttle_error
        prev_yaw_error = yaw_error
        prev_pitch_error = pitch_error
        prev_roll_error = roll_error

        if plot:
            plot_flight(time, throttle_error_arr, yaw_error_arr, pitch_error_arr, roll_error_arr)
