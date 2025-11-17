"""
UAV Deconfliction System Package.

Provides clean interface to all deconfliction functionality.

Example usage:
    from uav_deconfliction import (
        ProductionDeconflictionSystem,
        Mission,
        Waypoint,
        Severity
    )

    system = ProductionDeconflictionSystem()
    mission = Mission(waypoints=[...], start_time=0, end_time=300)
    is_clear, conflicts, metrics = system.check_mission(mission)
"""

# Core models
from .models import Waypoint, Mission, Conflict, Severity

# Trajectory computation
from .trajectory import ConstantVelocityTrajectory

# Stage components
from .filters import Stage1MultiTierFilter
from .occupancy_grid import Stage2OccupancyGrid
from .risk_scoring import Stage3RiskScoring

# Main system
from .deconfliction_system import ProductionDeconflictionSystem

__all__ = [
    # Data models
    'Waypoint',
    'Mission',
    'Conflict',
    'Severity',

    # Trajectory
    'ConstantVelocityTrajectory',

    # Stage components (for advanced users)
    'Stage1MultiTierFilter',
    'Stage2OccupancyGrid',
    'Stage3RiskScoring',

    # Main interface
    'ProductionDeconflictionSystem',
]

__version__ = '1.0.0'
__author__ = 'FlytBase Robotics Team'
