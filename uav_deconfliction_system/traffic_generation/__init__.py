"""
Traffic Generation Package

Generates diverse traffic drone missions with 11 different pattern types.

Usage:
    from traffic_generation import TrafficGenerator
    
    gen = TrafficGenerator()
    gen.generate_traffic(num_drones=100)
    missions = gen.missions
"""

from .generator import TrafficGenerator
from .simple_patterns import (
    generate_flyby,
    generate_circular_surveillance,
    generate_triangular,
    generate_star,
    generate_random_waypoints
)
from .complex_patterns import (
    generate_grid_surveillance,
    generate_mapping,
    generate_figure_eight
)
from .inspection_patterns import (
    generate_highrise_inspection,
    generate_lowrise_inspection,
    generate_holding_pattern
)

__all__ = [
    'TrafficGenerator',
    # Simple patterns
    'generate_flyby',
    'generate_circular_surveillance',
    'generate_triangular',
    'generate_star',
    'generate_random_waypoints',
    # Complex patterns
    'generate_grid_surveillance',
    'generate_mapping',
    'generate_figure_eight',
    # Inspection patterns
    'generate_highrise_inspection',
    'generate_lowrise_inspection',
    'generate_holding_pattern'
]

__version__ = '1.0.0'
__author__ = 'FlytBase Robotics Team'
