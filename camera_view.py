import djitellopy as tello
import cv2

# Initialize and connect to my_drone
my_drone = tello.Tello()
my_drone.connect()

# Print battery percentage to confirm connection
print(my_drone.get_battery())

# Turn on video streaming
my_drone.streamon()

# Display live feed from front facing camera
while True:

    # Get and resize image from my_drone
    img = my_drone.get_frame_read().frame
    img = cv2.resize(img, (360, 240))

    # Display video stream
    cv2.imshow("Image", img)
    cv2.waitKey(1)

