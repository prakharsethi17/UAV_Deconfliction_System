"""
Traffic drone simple pattern generators:
- Flyby
- Circular Surveillance
- Triangular
- Star
- Random
"""
import numpy as np
from deconfliction import Waypoint

def generate_flyby(airspace_x, airspace_y, altitude_range=(100, 300)):
    start_x = np.random.uniform(0, airspace_x * 0.2)
    start_y = np.random.uniform(0, airspace_y)
    end_x = np.random.uniform(airspace_x * 0.8, airspace_x)
    end_y = np.random.uniform(0, airspace_y)
    altitude = np.random.uniform(*altitude_range)
    return [Waypoint(start_x, start_y, altitude), Waypoint(end_x, end_y, altitude)]

def generate_circular_surveillance(center_x, center_y, altitude, radius, num_points=8):
    waypoints = []
    for i in range(num_points + 1):
        angle = 2 * np.pi * i / num_points
        x = center_x + radius * np.cos(angle)
        y = center_y + radius * np.sin(angle)
        waypoints.append(Waypoint(x, y, altitude))
    return waypoints

def generate_triangular(center_x, center_y, altitude, side_length):
    height = side_length * (3 ** 0.5) / 2
    waypoints = [
        Waypoint(center_x, center_y + 2*height/3, altitude),
        Waypoint(center_x - side_length/2, center_y - height/3, altitude),
        Waypoint(center_x + side_length/2, center_y - height/3, altitude),
        Waypoint(center_x, center_y + 2*height/3, altitude),
    ]
    return waypoints

def generate_star(center_x, center_y, altitude, outer_radius, num_points=5):
    waypoints = []
    for i in range(2*num_points + 1):
        r = outer_radius if i % 2 == 0 else outer_radius / 2
        angle = np.pi * i / num_points
        x = center_x + r * np.cos(angle)
        y = center_y + r * np.sin(angle)
        waypoints.append(Waypoint(x, y, altitude))
    return waypoints

def generate_random_waypoints(num_points, airspace_x, airspace_y, altitude_range=(100, 300)):
    waypoints = []
    for _ in range(num_points):
        x = np.random.uniform(0, airspace_x)
        y = np.random.uniform(0, airspace_y)
        z = np.random.uniform(*altitude_range)
        waypoints.append(Waypoint(x, y, z))
    return waypoints
