"""
Core data models for UAV Deconfliction System.

Defines fundamental data structures used across all modules:
- Waypoint: 3D spatial coordinates
- Mission: Complete drone flight plan with physics
- Conflict: Detected collision with risk assessment
- Severity: Conflict severity enumeration
"""

import numpy as np
from dataclasses import dataclass
from typing import List, Tuple, Optional
from enum import Enum


class Severity(Enum):
    """Conflict severity levels."""
    SAFE = 0        # No Conflict
    LOW = 1         # Minor proximity, no immediate danger
    WARNING = 2     # Approaching safety threshold
    HIGH = 3        # Safety buffer violated
    CRITICAL = 4    # Imminent collision risk


@dataclass
class Waypoint:
    """3D waypoint with position."""
    x: float
    y: float
    z: float = 0.0

    def to_array(self) -> np.ndarray:
        """Convert to NumPy array."""
        return np.array([self.x, self.y, self.z])

    def distance_to(self, other: 'Waypoint') -> float:
        """Euclidean distance between waypoints."""
        return np.linalg.norm(self.to_array() - other.to_array())


@dataclass
class Mission:
    """Drone mission with constant velocity physics."""
    waypoints: List[Waypoint]
    start_time: float
    end_time: float
    drone_id: str = "UNKNOWN"

    # Physics parameters
    cruise_speed: Optional[float] = None  # m/s - computed if None
    accel_time: float = 2.0               # seconds
    max_accel: float = 5.0                # m/s²

    def __post_init__(self):
        """Compute cruise speed using constant-velocity physics."""
        if self.cruise_speed is None:
            total_distance = self.total_distance()
            duration = self.duration()
            self.cruise_speed = total_distance / duration if duration > 0 else 0.0

    def duration(self) -> float:
        """Mission duration in seconds."""
        return self.end_time - self.start_time

    def total_distance(self) -> float:
        """Calculate total path length."""
        distance = 0.0
        for i in range(len(self.waypoints) - 1):
            distance += self.waypoints[i].distance_to(self.waypoints[i + 1])
        return distance

    def get_bounding_box(self) -> Tuple[np.ndarray, np.ndarray]:
        """Get 3D bounding box for spatial filtering."""
        positions = np.array([wp.to_array() for wp in self.waypoints])
        return positions.min(axis=0), positions.max(axis=0)


@dataclass
class Conflict:
    """Detected conflict with risk assessment."""
    time: float
    location: Waypoint
    primary_drone: str
    conflicting_drone: str
    separation_distance: float
    relative_velocity: float
    conflict_duration: float
    altitude_risk_factor: float
    risk_score: float
    severity: Severity
    time_to_collision: float
    recommendation: str

    def __str__(self) -> str:
        return (f"[{self.severity.name}] Conflict at t={self.time:.1f}s: "
                f"{self.primary_drone} ↔ {self.conflicting_drone} | "
                f"Sep={self.separation_distance:.1f}m, "
                f"v_rel={self.relative_velocity:.1f}m/s, "
                f"Risk={self.risk_score:.2f}")
