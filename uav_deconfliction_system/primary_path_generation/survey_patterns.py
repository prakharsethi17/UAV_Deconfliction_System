import numpy as np
from deconfliction import Mission, Waypoint

def generate_grid_survey_mission(grid_origin, grid_width, grid_height, num_rows, start_time=0.0, velocity=12.0, drone_id="PRIMARY"):
    x0, y0, z = grid_origin
    row_spacing = grid_height / (num_rows - 1) if num_rows > 1 else 0.0
    waypoints = []
    for i in range(num_rows):
        y = y0 + i * row_spacing
        if i % 2 == 0:
            waypoints.append(Waypoint(x0, y, z))
            waypoints.append(Waypoint(x0 + grid_width, y, z))
        else:
            waypoints.append(Waypoint(x0 + grid_width, y, z))
            waypoints.append(Waypoint(x0, y, z))
    temp_mission = Mission(waypoints=waypoints, start_time=0, end_time=1, drone_id="TEMP")
    duration = temp_mission.total_distance() / velocity if velocity > 0 else 0.0
    end_time = start_time + duration
    return Mission(waypoints=waypoints, start_time=start_time, end_time=end_time, drone_id=drone_id, cruise_speed=velocity)

def generate_circular_inspection_mission(center, radius, num_points=8, start_time=0.0, velocity=12.0, drone_id="PRIMARY"):
    cx, cy, cz = center
    waypoints = [
        Waypoint(
            cx + radius * np.cos(2 * np.pi * i / num_points),
            cy + radius * np.sin(2 * np.pi * i / num_points),
            cz
        ) for i in range(num_points+1)
    ]
    temp_mission = Mission(waypoints=waypoints, start_time=0, end_time=1, drone_id="TEMP")
    duration = temp_mission.total_distance() / velocity if velocity > 0 else 0.0
    end_time = start_time + duration
    return Mission(waypoints=waypoints, start_time=start_time, end_time=end_time, drone_id=drone_id, cruise_speed=velocity)
