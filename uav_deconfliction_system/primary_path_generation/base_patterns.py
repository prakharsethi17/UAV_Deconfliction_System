import numpy as np
from deconfliction import Mission, Waypoint

def generate_straight_line_mission(start_pos, end_pos, start_time=0.0, velocity=12.0, drone_id="PRIMARY"):
    waypoints = [Waypoint(*start_pos), Waypoint(*end_pos)]
    temp_mission = Mission(waypoints=waypoints, start_time=0, end_time=1, drone_id="TEMP")
    duration = temp_mission.total_distance() / velocity if velocity > 0 else 0.0
    end_time = start_time + duration
    return Mission(waypoints=waypoints, start_time=start_time, end_time=end_time, drone_id=drone_id, cruise_speed=velocity)

def generate_multi_waypoint_mission(num_waypoints, airspace_x, airspace_y, altitude_range, start_time=0.0, velocity=12.0, drone_id="PRIMARY", seed=None):
    if seed is not None:
        np.random.seed(seed)
    waypoints = [
        Waypoint(
            np.random.uniform(0, airspace_x),
            np.random.uniform(0, airspace_y),
            np.random.uniform(*altitude_range)
        )
        for _ in range(num_waypoints)
    ]
    temp_mission = Mission(waypoints=waypoints, start_time=0, end_time=1, drone_id="TEMP")
    duration = temp_mission.total_distance() / velocity if velocity > 0 else 0.0
    end_time = start_time + duration
    return Mission(waypoints=waypoints, start_time=start_time, end_time=end_time, drone_id=drone_id, cruise_speed=velocity)
