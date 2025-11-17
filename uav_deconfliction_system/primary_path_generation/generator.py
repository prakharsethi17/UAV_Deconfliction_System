import numpy as np
from .base_patterns import generate_straight_line_mission, generate_multi_waypoint_mission
from .survey_patterns import generate_grid_survey_mission, generate_circular_inspection_mission

class PrimaryDroneGenerator:
    def __init__(self, airspace_x=5000.0, airspace_y=5000.0, airspace_z=1000.0, default_velocity=12.0):
        self.airspace_x = airspace_x
        self.airspace_y = airspace_y
        self.airspace_z = airspace_z
        self.default_velocity = default_velocity

    def straight_line(self, start_pos, end_pos, start_time=0.0, velocity=None, drone_id="PRIMARY"):
        velocity = velocity if velocity is not None else self.default_velocity
        return generate_straight_line_mission(start_pos, end_pos, start_time, velocity, drone_id)

    def multi_waypoint(self, num_waypoints=5, altitude_range=(100.0, 300.0), start_time=0.0, velocity=None, drone_id="PRIMARY", seed=None):
        velocity = velocity if velocity is not None else self.default_velocity
        return generate_multi_waypoint_mission(num_waypoints, self.airspace_x, self.airspace_y, altitude_range, start_time, velocity, drone_id, seed)

    def grid_survey(self, grid_origin, grid_width, grid_height, num_rows, start_time=0.0, velocity=None, drone_id="PRIMARY"):
        velocity = velocity if velocity is not None else self.default_velocity
        return generate_grid_survey_mission(grid_origin, grid_width, grid_height, num_rows, start_time, velocity, drone_id)

    def circular_inspection(self, center, radius, num_points=8, start_time=0.0, velocity=None, drone_id="PRIMARY"):
        velocity = velocity if velocity is not None else self.default_velocity
        return generate_circular_inspection_mission(center, radius, num_points, start_time, velocity, drone_id)

    def custom(self, waypoint_coords, start_time=0.0, velocity=None, drone_id="PRIMARY"):
        velocity = velocity if velocity is not None else self.default_velocity
        from deconfliction import Mission, Waypoint
        waypoints = [Waypoint(x, y, z) for x, y, z in waypoint_coords]
        temp_mission = Mission(waypoints=waypoints, start_time=0, end_time=1, drone_id="TEMP")
        duration = temp_mission.total_distance() / velocity if velocity > 0 else 0.0
        end_time = start_time + duration
        return Mission(waypoints=waypoints, start_time=start_time, end_time=end_time, drone_id=drone_id, cruise_speed=velocity)

    def random_mission(self, start_time=0.0, velocity=None, drone_id="PRIMARY", seed=None):
        import random
        if seed is not None:
            np.random.seed(seed)
            random.seed(seed)
        velocity = velocity if velocity is not None else self.default_velocity
        mission_type = random.choice(['straight_line', 'multi_waypoint', 'grid_survey', 'circular_inspection'])
        if mission_type == 'straight_line':
            start_pos = (np.random.uniform(0, self.airspace_x * 0.3), np.random.uniform(0, self.airspace_y * 0.3), np.random.uniform(50, 200))
            end_pos = (np.random.uniform(self.airspace_x * 0.7, self.airspace_x), np.random.uniform(self.airspace_y * 0.7, self.airspace_y), np.random.uniform(50, 200))
            return self.straight_line(start_pos, end_pos, start_time, velocity, drone_id)
        elif mission_type == 'multi_waypoint':
            num_waypoints = random.randint(3, 8)
            altitude_range = (np.random.uniform(50, 100), np.random.uniform(150, 250))
            return self.multi_waypoint(num_waypoints, altitude_range, start_time, velocity, drone_id)
        elif mission_type == 'grid_survey':
            grid_origin = (np.random.uniform(0, self.airspace_x * 0.5), np.random.uniform(0, self.airspace_y * 0.5), np.random.uniform(80, 150))
            grid_width = np.random.uniform(500, 1500)
            grid_height = np.random.uniform(500, 1500)
            num_rows = random.randint(3, 7)
            return self.grid_survey(grid_origin, grid_width, grid_height, num_rows, start_time, velocity, drone_id)
        else: # circular_inspection
            center = (np.random.uniform(self.airspace_x * 0.3, self.airspace_x * 0.7), np.random.uniform(self.airspace_y * 0.3, self.airspace_y * 0.7), np.random.uniform(80, 150))
            radius = np.random.uniform(300, 800)
            num_points = random.randint(6, 12)
            return self.circular_inspection(center, radius, num_points, start_time, velocity, drone_id)
