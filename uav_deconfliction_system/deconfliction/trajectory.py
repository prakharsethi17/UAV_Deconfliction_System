"""
Trajectory interpolation for constant-velocity drone missions.

Converts static Mission (waypoints + time window) into dynamic 4D trajectory
that can answer: "Where is the drone at time t?"

Uses constant cruise velocity physics model.
"""

import numpy as np
from typing import Optional, List, Dict
from .models import Mission, Waypoint


class ConstantVelocityTrajectory:
    """
    Constant cruise velocity trajectory model.

    Physics:
    - Single constant speed for entire mission
    - Segment times computed from: time = distance / speed
    - Linear interpolation between waypoints
    """

    def __init__(self, mission: Mission):
        """
        Initialize trajectory from mission.

        Args:
            mission: Mission object with waypoints and timing
        """
        self.mission = mission
        self.constant_speed = mission.cruise_speed
        self.segments: List[Dict] = []
        self._build_trajectory()

    def _build_trajectory(self):
        """Build trajectory segments with constant velocity."""
        waypoints = self.mission.waypoints
        current_time = self.mission.start_time

        for i in range(len(waypoints) - 1):
            start = waypoints[i]
            end = waypoints[i + 1]
            segment_distance = start.distance_to(end)

            # Constant velocity: time = distance / speed
            segment_time = (segment_distance / self.constant_speed 
                          if self.constant_speed > 0 else 0)

            velocity_vec = ((end.to_array() - start.to_array()) / segment_distance 
                          if segment_distance > 0 else np.zeros(3))

            self.segments.append({
                'start': start,
                'end': end,
                'start_time': current_time,
                'end_time': current_time + segment_time,
                'distance': segment_distance,
                'duration': segment_time,
                'velocity_vector': velocity_vec
            })

            current_time += segment_time

    def get_position(self, time: float) -> Optional[Waypoint]:
        """
        Get position at specified time using linear interpolation.

        Args:
            time: Query time in seconds

        Returns:
            Waypoint at the given time, or None if outside mission window
        """
        if time < self.mission.start_time or time > self.mission.end_time:
            return None

        for segment in self.segments:
            if segment['start_time'] <= time <= segment['end_time']:
                t_elapsed = time - segment['start_time']
                progress = (t_elapsed / segment['duration'] 
                          if segment['duration'] > 0 else 0)

                start = segment['start'].to_array()
                end = segment['end'].to_array()
                position = start + progress * (end - start)

                return Waypoint(position[0], position[1], position[2])

        return self.mission.waypoints[-1]

    def get_velocity(self, time: float) -> Optional[np.ndarray]:
        """
        Get velocity vector at specified time.

        Args:
            time: Query time in seconds

        Returns:
            Velocity vector [vx, vy, vz], or None if outside mission window
        """
        if time < self.mission.start_time or time > self.mission.end_time:
            return None

        for segment in self.segments:
            if segment['start_time'] <= time <= segment['end_time']:
                return segment['velocity_vector'] * self.constant_speed

        return np.zeros(3)
