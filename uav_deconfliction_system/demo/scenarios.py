"""
Scenario definitions for UAV Deconfliction System demos.

Contains pre-configured test scenarios with varying mission types,
traffic densities, and airspace conditions.

Each scenario is a dictionary with:
- name: Scenario identifier
- description: What the scenario tests
- airspace: Airspace dimensions
- num_traffic_drones: Number of traffic drones
- seed: Random seed for reproducibility
- mission_config: Mission type and parameters
- output_dir: Where to save results
"""

# Scenario 1: Random Mission Type with Medium Traffic
SCENARIO_1_RANDOM = {
    "name": "scenario1_random",
    "description": "Random mission type with 75 traffic drones",
    "airspace": {
        "x": 5000.0,
        "y": 5000.0,
        "z": 1000.0
    },
    "num_traffic_drones": 75,
    "seed": 42,
    "mission_config": {
        "mission_type": "random",
        "start_time": 300.0,
        "velocity": None  # Use default
    },
    "output_dir": "./output/scenario1_random"
}

# Scenario 2: Grid Survey Mission with High Traffic
SCENARIO_2_GRID = {
    "name": "scenario2_grid",
    "description": "Grid survey mission with 80 traffic drones",
    "airspace": {
        "x": 5000.0,
        "y": 5000.0,
        "z": 1000.0
    },
    "num_traffic_drones": 80,
    "seed": 123,
    "mission_config": {
        "mission_type": "grid_survey",
        "grid_origin": (1000, 1000, 120),
        "grid_width": 2000,
        "grid_height": 2000,
        "num_rows": 6,
        "start_time": 500.0,
        "velocity": None
    },
    "output_dir": "./output/scenario2_grid"
}

# Scenario 3: Circular Inspection Mission with Moderate Traffic
SCENARIO_3_CIRCULAR = {
    "name": "scenario3_circular",
    "description": "Circular inspection mission with 60 traffic drones",
    "airspace": {
        "x": 5000.0,
        "y": 5000.0,
        "z": 1000.0
    },
    "num_traffic_drones": 60,
    "seed": 456,
    "mission_config": {
        "mission_type": "circular_inspection",
        "center": (2500, 2500, 200),
        "radius": 600,
        "num_points": 16,
        "start_time": 800.0,
        "velocity": None
    },
    "output_dir": "./output/scenario3_circular"
}

# Scenario 4: Straight Line Mission with Low Traffic
SCENARIO_4_STRAIGHT = {
    "name": "scenario4_straight",
    "description": "Straight line mission with 50 traffic drones",
    "airspace": {
        "x": 5000.0,
        "y": 5000.0,
        "z": 1000.0
    },
    "num_traffic_drones": 50,
    "seed": 789,
    "mission_config": {
        "mission_type": "straight_line",
        "start_pos": (0, 0, 100),
        "end_pos": (5000, 5000, 150),
        "start_time": 1200.0,
        "velocity": None
    },
    "output_dir": "./output/scenario4_straight"
}

# Scenario 5: Multi-Waypoint Mission with Heavy Traffic
SCENARIO_5_MULTIWAYPOINT = {
    "name": "scenario5_multiwaypoint",
    "description": "Multi-waypoint mission with 100 traffic drones",
    "airspace": {
        "x": 5000.0,
        "y": 5000.0,
        "z": 1000.0
    },
    "num_traffic_drones": 100,
    "seed": 999,
    "mission_config": {
        "mission_type": "multi_waypoint",
        "num_waypoints": 7,
        "altitude_range": (100, 300),
        "start_time": 200.0,
        "velocity": None
    },
    "output_dir": "./output/scenario5_multiwaypoint"
}

# Scenario 6: Custom Waypoint Mission
SCENARIO_6_CUSTOM = {
    "name": "scenario6_custom",
    "description": "Custom waypoint path with 65 traffic drones",
    "airspace": {
        "x": 5000.0,
        "y": 5000.0,
        "z": 1000.0
    },
    "num_traffic_drones": 65,
    "seed": 111,
    "mission_config": {
        "mission_type": "custom",
        "waypoint_coords": [
            (0, 0, 100),
            (1000, 500, 120),
            (2000, 1500, 140),
            (3000, 1000, 130),
            (4000, 2000, 150),
            (5000, 2500, 120)
        ],
        "start_time": 600.0,
        "velocity": 15.0  # Slightly faster
    },
    "output_dir": "./output/scenario6_custom"
}

# List of all scenarios for batch execution
ALL_SCENARIOS = [
    SCENARIO_1_RANDOM,
    SCENARIO_2_GRID,
    SCENARIO_3_CIRCULAR,
    SCENARIO_4_STRAIGHT,
    SCENARIO_5_MULTIWAYPOINT,
    SCENARIO_6_CUSTOM
]

# Default scenarios for quick testing (subset)
DEFAULT_SCENARIOS = [
    SCENARIO_1_RANDOM,
    SCENARIO_2_GRID,
    SCENARIO_3_CIRCULAR,
    SCENARIO_4_STRAIGHT
]


def get_scenario_by_name(scenario_name: str):
    """
    Retrieve a scenario configuration by name.
    
    Args:
        scenario_name: Name of the scenario
        
    Returns:
        Scenario dictionary or None if not found
    """
    for scenario in ALL_SCENARIOS:
        if scenario["name"] == scenario_name:
            return scenario
    return None


def list_available_scenarios():
    """Print all available scenario names and descriptions."""
    print("\n" + "="*70)
    print("AVAILABLE DEMO SCENARIOS")
    print("="*70)
    for i, scenario in enumerate(ALL_SCENARIOS, 1):
        print(f"{i}. {scenario['name']}")
        print(f"   {scenario['description']}")
        print(f"   Traffic: {scenario['num_traffic_drones']} drones | Seed: {scenario['seed']}")
        print()
    print("="*70)


if __name__ == "__main__":
    # When run directly, list all scenarios
    list_available_scenarios()
