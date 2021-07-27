import numpy as np


# Function to solve for the centroid of an aruco marker given 4 corners
def find_aruco_centroid(corners):
    x_vals = []
    y_vals = []

    for corner in corners:
        x_vals.append(int(corner[0]))
        y_vals.append(int(corner[1]))

    x = int(sum(x_vals) / 4)
    y = int(sum(y_vals) / 4)

    centroid = (x, y)

    return centroid


# Function to return the average side length of an aruco marker given 4 corners
# TODO convert to side lenght!!
def get_aruco_area(corners):
    t1x = [corners[0][0], corners[1][0], corners[2][0]]
    t1y = [corners[0][1], corners[1][1], corners[2][1]]
    t2x = [corners[0][0], corners[2][0], corners[3][0]]
    t2y = [corners[0][1], corners[2][1], corners[3][1]]

    area = 0.5 * ((t1x[0] * (t1y[1] - t1y[2])) + (t1x[1] * (t1y[2] - t1y[0])) + (t1x[2] * (t1y[0] - t1y[1])))
    area += 0.5 * ((t2x[0] * (t2y[1] - t2y[2])) + (t2x[1] * (t2y[2] - t2y[0])) + (t2x[2] * (t2y[0] - t2y[1])))

    return area


# Function to solve the slope of any line given the x and y coords of any 2 points
def slope(x1, y1, x2, y2):

    m = (y2-y1)/(x2-x1)

    return m


# Function to help us by converting corners to points
def aruco_corners_to_points(corners):

    point_0 = (corners[0][0], corners[0][1])
    point_1 = (corners[1][0], corners[1][1])

    point_2 = (corners[2][0], corners[2][1])
    point_3 = (corners[3][0], corners[3][1])

    return point_0, point_1, point_2, point_3


# Function to solve the slope of the bottom two points of an aruco marker
def find_aruco_slope(corners):

    point_2 = np.array([corners[2][0], corners[2][1]])
    point_3 = np.array([corners[3][0], corners[3][1]])

    bottom = slope(point_2[0], point_2[1], point_3[0], point_3[1])

    return bottom


class Marker:

    def __init__(self, aruco_id, corners):

        self.aruco_id = aruco_id
        self.centroid = find_aruco_centroid(corners)
        self.x = self.centroid[0]
        self.y = self.centroid[1]
        self.area = get_aruco_area(corners)

        self.bottom = find_aruco_slope(corners)

        self.point_0 = aruco_corners_to_points(corners)[0]
        self.point_1 = aruco_corners_to_points(corners)[1]
        self.point_2 = aruco_corners_to_points(corners)[2]
        self.point_3 = aruco_corners_to_points(corners)[3]
