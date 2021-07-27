import cv2
import cv2.aruco as aruco
import marker as mk


# Define which camera we will access
cap = cv2.VideoCapture(0)

while True:
    # Read camera feed
    _, img = cap.read()

    # Detect aruco markers
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    key = getattr(aruco, f'DICT_5X5_100')
    aruco_dict = aruco.Dictionary_get(key)
    aruco_param = aruco.DetectorParameters_create()
    marker_corners, ids, rejected = aruco.detectMarkers(img_gray, aruco_dict, parameters=aruco_param)

    # If markers are detected, create marker objects, draw outlines and centroids, find biggest marker, etc.
    if ids is not None:

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

        # Figure out which marker is the biggest/closest marker
        biggest_marker = aruco_markers[0]
        for marker in aruco_markers:
            if marker.area > biggest_marker.area:
                biggest_marker = marker

        # Print ID of the biggest aruco marker
        print(biggest_marker.aruco_id)

    # Display video in cv2 window
    cv2.imshow("Image", img)
    cv2.waitKey(1)
