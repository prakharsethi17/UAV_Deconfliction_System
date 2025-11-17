"""
Stage 2: 4D Occupancy Grid Conflict Detector.

High-precision conflict detection using spatial-temporal grid:
- 100×100×100m spatial cells
- 1-second temporal resolution
- Efficiently detects close approaches in 4D space
"""

import numpy as np
from typing import Dict, List, Tuple
from .models import Mission, Waypoint
from .trajectory import ConstantVelocityTrajectory


class Stage2OccupancyGrid:
    """4D occupancy grid for high-precision conflict detection."""

    def __init__(self, cell_size: float = 100.0, time_resolution: float = 1.0):
        """
        Initialize occupancy grid.

        Args:
            cell_size: Spatial cell size in meters (100m standard)
            time_resolution: Temporal resolution in seconds
        """
        self.cell_size = cell_size
        self.time_resolution = time_resolution
        self.grid: Dict[Tuple[int, int, int, int], List[Tuple[str, Waypoint]]] = {}

    def build_grid(self, missions: List[Mission]):
        """
        Build 4D occupancy grid from filtered candidate missions.

        Args:
            missions: List of candidate missions to populate grid
        """
        self.grid.clear()

        for mission in missions:
            traj = ConstantVelocityTrajectory(mission)

            # Sample trajectory at time_resolution intervals
            times = np.arange(mission.start_time, mission.end_time, 
                            self.time_resolution)

            for t in times:
                pos = traj.get_position(t)
                if pos:
                    # Convert to grid coordinates
                    cell = self._get_cell(pos, t)
                    if cell not in self.grid:
                        self.grid[cell] = []
                    self.grid[cell].append((mission.drone_id, pos))

    def _get_cell(self, pos: Waypoint, time: float) -> Tuple[int, int, int, int]:
        """
        Convert position and time to 4D grid cell coordinates.

        Args:
            pos: 3D position
            time: Time in seconds

        Returns:
            (x_cell, y_cell, z_cell, t_cell) tuple
        """
        x_cell = int(pos.x / self.cell_size)
        y_cell = int(pos.y / self.cell_size)
        z_cell = int(pos.z / self.cell_size)
        t_cell = int(time / self.time_resolution)
        return (x_cell, y_cell, z_cell, t_cell)

    def query_trajectory(self, primary_mission: Mission,
                        safety_buffer: float = 50.0) -> List[Tuple[float, Waypoint, str, float]]:
        """
        Query primary trajectory against occupancy grid.

        Args:
            primary_mission: Mission to check for conflicts
            safety_buffer: Minimum safe distance in meters

        Returns:
            List of (time, location, conflicting_drone_id, distance) tuples
        """
        conflicts = []
        traj = ConstantVelocityTrajectory(primary_mission)

        # Velocity-adaptive time sampling for precision
        dt = min(safety_buffer / (2 * traj.constant_speed), self.time_resolution)
        times = np.arange(primary_mission.start_time, primary_mission.end_time, dt)

        for t in times:
            pos = traj.get_position(t)
            if not pos:
                continue

            # Check current cell and 26 adjacent cells (3×3×3 neighborhood)
            primary_cell = self._get_cell(pos, t)

            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    for dz in [-1, 0, 1]:
                        for dt_cell in [-1, 0, 1]:
                            check_cell = (
                                primary_cell[0] + dx,
                                primary_cell[1] + dy,
                                primary_cell[2] + dz,
                                primary_cell[3] + dt_cell
                            )

                            if check_cell in self.grid:
                                for drone_id, drone_pos in self.grid[check_cell]:
                                    distance = pos.distance_to(drone_pos)
                                    if distance < safety_buffer:
                                        conflicts.append((t, pos, drone_id, distance))

        return conflicts
