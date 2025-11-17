"""
Traffic drone complex pattern generators:
- Grid Surveillance
- Mapping
- Figure Eight
"""
import numpy as np
from deconfliction import Waypoint

def generate_grid_surveillance(origin_x, origin_y, altitude, grid_width, grid_height, num_rows):
    x_step = grid_width / (num_rows - 1) if num_rows > 1 else 0
    y_step = grid_height / (num_rows - 1) if num_rows > 1 else 0
    waypoints = []
    for i in range(num_rows):
        y = origin_y + i * y_step
        if i % 2 == 0:
            waypoints.append(Waypoint(origin_x, y, altitude))
            waypoints.append(Waypoint(origin_x + grid_width, y, altitude))
        else:
            waypoints.append(Waypoint(origin_x + grid_width, y, altitude))
            waypoints.append(Waypoint(origin_x, y, altitude))
    return waypoints

def generate_mapping(center_x, center_y, altitude, size, num_points=8):
    waypoints = []
    for i in range(num_points):
        angle = 2 * np.pi * i / num_points
        r = size * np.random.uniform(0.8, 1.2)
        x = center_x + r * np.cos(angle)
        y = center_y + r * np.sin(angle)
        waypoints.append(Waypoint(x, y, altitude))
    return waypoints

def generate_figure_eight(center_x, center_y, altitude, size):
    waypoints = []
    for t in np.linspace(0, 2 * np.pi, num=20):
        x = center_x + size * np.sin(t)
        y = center_y + size * np.sin(t) * np.cos(t)
        waypoints.append(Waypoint(x, y, altitude))
    return waypoints
