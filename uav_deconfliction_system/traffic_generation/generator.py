"""
TrafficGenerator class orchestrates drone missions creation.
"""
import numpy as np
import random
from typing import List
from deconfliction import Mission, Waypoint
from .simple_patterns import generate_flyby, generate_circular_surveillance, generate_triangular, generate_star, generate_random_waypoints
from .complex_patterns import generate_grid_surveillance, generate_mapping, generate_figure_eight
from .inspection_patterns import generate_highrise_inspection, generate_lowrise_inspection, generate_holding_pattern

class TrafficGenerator:
    def __init__(self, airspace_x=5000, airspace_y=5000, airspace_z=1000, velocity=12, flight_duration=600):
        self.airspace_x = airspace_x
        self.airspace_y = airspace_y
        self.airspace_z = airspace_z
        self.velocity = velocity
        self.flight_duration = flight_duration
        self.missions: List[Mission] = []

    def generate_traffic(self, num_drones=50):
        self.missions.clear()
        for i in range(num_drones):
            drone_id = f"TRAFFIC-{i:03d}"
            pattern_choice = random.choice([
                'flyby', 'circular', 'triangular', 'star', 'random',
                'grid', 'mapping', 'figure_eight',
                'highrise', 'lowrise', 'holding'
            ])
            method = getattr(self, f'_generate_{pattern_choice}_mission', None)
            if method:
                mission = method(drone_id)
                if mission:
                    self.missions.append(mission)

    def _generate_flyby_mission(self, drone_id):
        waypoints = generate_flyby(self.airspace_x, self.airspace_y)
        return self.create_mission_from_waypoints(waypoints, drone_id)

    def _generate_circular_mission(self, drone_id):
        center_x = self.airspace_x / 2
        center_y = self.airspace_y / 2
        altitude = np.random.uniform(100, 300)
        waypoints = generate_circular_surveillance(center_x, center_y, altitude, radius=500)
        return self.create_mission_from_waypoints(waypoints, drone_id)

    def _generate_triangular_mission(self, drone_id):
        center_x = self.airspace_x / 2
        center_y = self.airspace_y / 2
        altitude = np.random.uniform(100, 300)
        waypoints = generate_triangular(center_x, center_y, altitude, side_length=1000)
        return self.create_mission_from_waypoints(waypoints, drone_id)

    def _generate_star_mission(self, drone_id):
        center_x = self.airspace_x / 2
        center_y = self.airspace_y / 2
        altitude = np.random.uniform(100, 300)
        waypoints = generate_star(center_x, center_y, altitude, outer_radius=600)
        return self.create_mission_from_waypoints(waypoints, drone_id)

    def _generate_random_mission(self, drone_id):
        num_points = random.randint(5, 10)
        waypoints = generate_random_waypoints(num_points, self.airspace_x, self.airspace_y)
        return self.create_mission_from_waypoints(waypoints, drone_id)

    def _generate_grid_mission(self, drone_id):
        origin_x = 0
        origin_y = 0
        altitude = np.random.uniform(100, 300)
        waypoints = generate_grid_surveillance(origin_x, origin_y, altitude, grid_width=2000, grid_height=2000, num_rows=5)
        return self.create_mission_from_waypoints(waypoints, drone_id)

    def _generate_mapping_mission(self, drone_id):
        center_x = self.airspace_x / 2
        center_y = self.airspace_y / 2
        altitude = np.random.uniform(100, 300)
        waypoints = generate_mapping(center_x, center_y, altitude, size=500)
        return self.create_mission_from_waypoints(waypoints, drone_id)

    def _generate_figure_eight_mission(self, drone_id):
        center_x = self.airspace_x / 2
        center_y = self.airspace_y / 2
        altitude = np.random.uniform(100, 300)
        waypoints = generate_figure_eight(center_x, center_y, altitude, size=500)
        return self.create_mission_from_waypoints(waypoints, drone_id)

    def _generate_highrise_mission(self, drone_id):
        base_x = self.airspace_x / 2
        base_y = self.airspace_y / 2
        base_z = 0
        radius = 300
        height = 500
        waypoints = generate_highrise_inspection(base_x, base_y, base_z, radius, height)
        return self.create_mission_from_waypoints(waypoints, drone_id)

    def _generate_lowrise_mission(self, drone_id):
        origin_x = 0
        origin_y = 0
        altitude = np.random.uniform(50, 100)
        waypoints = generate_lowrise_inspection(origin_x, origin_y, altitude)
        return self.create_mission_from_waypoints(waypoints, drone_id)

    def _generate_holding_mission(self, drone_id):
        center_x = self.airspace_x / 2
        center_y = self.airspace_y / 2
        altitude = np.random.uniform(100, 300)
        waypoints = generate_holding_pattern(center_x, center_y, altitude, width=1000, height=500)
        return self.create_mission_from_waypoints(waypoints, drone_id)

    def create_mission_from_waypoints(self, waypoints, drone_id):
        from deconfliction import Mission
        start_time = 0
        cruise_speed = 12.0
        distance = 0
        for i in range(len(waypoints) - 1):
            distance += waypoints[i].distance_to(waypoints[i + 1])
        duration = distance / cruise_speed if cruise_speed > 0 else 600
        end_time = start_time + duration
        return Mission(waypoints=waypoints, start_time=start_time, end_time=end_time, drone_id=drone_id, cruise_speed=cruise_speed)
