"""
Traffic drone inspection pattern generators:
- Highrise Inspection
- Lowrise Inspection
- Holding Pattern
"""
import numpy as np
from deconfliction import Waypoint

def generate_highrise_inspection(base_x, base_y, base_z, radius, height, levels=5, points_per_level=8):
    waypoints = []
    for level in range(levels):
        z = base_z + (height / levels) * level
        for i in range(points_per_level):
            angle = 2 * np.pi * i / points_per_level
            x = base_x + radius * np.cos(angle)
            y = base_y + radius * np.sin(angle)
            waypoints.append(Waypoint(x, y, z))
    return waypoints

def generate_lowrise_inspection(origin_x, origin_y, altitude, perimeter_length=1000, num_points=20):
    waypoints = []
    step = perimeter_length / num_points
    for i in range(num_points):
        x = origin_x + (i % 4) * step
        y = origin_y + ((i // 4) % 4) * step
        waypoints.append(Waypoint(x, y, altitude))
    return waypoints

def generate_holding_pattern(center_x, center_y, altitude, width, height):
    waypoints = [
        Waypoint(center_x - width / 2, center_y - height / 2, altitude),
        Waypoint(center_x + width / 2, center_y - height / 2, altitude),
        Waypoint(center_x + width / 2, center_y + height / 2, altitude),
        Waypoint(center_x - width / 2, center_y + height / 2, altitude),
        Waypoint(center_x - width / 2, center_y - height / 2, altitude),
    ]
    return waypoints
