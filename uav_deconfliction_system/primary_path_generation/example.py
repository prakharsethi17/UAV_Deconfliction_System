from .generator import PrimaryDroneGenerator
from .utilities import print_mission_summary

def test_all_patterns():
    gen = PrimaryDroneGenerator()
    print("\n1. Straight Line Mission:")
    m1 = gen.straight_line((0,0,50), (1000,1000,100), drone_id="PRIMARY-001")
    print_mission_summary(m1)

    print("\n2. Multi-Waypoint Mission:")
    m2 = gen.multi_waypoint(num_waypoints=5, altitude_range=(100,200), drone_id="PRIMARY-002", seed=42)
    print_mission_summary(m2)

    print("\n3. Grid Survey Mission:")
    m3 = gen.grid_survey((0,0,100), 1000, 800, 4, drone_id="SURVEY-001")
    print_mission_summary(m3)

    print("\n4. Circular Inspection Mission:")
    m4 = gen.circular_inspection((2500,2500,120), 500, num_points=8, drone_id="INSPECT-001")
    print_mission_summary(m4)

    print("\n5. Custom Mission:")
    custom_waypoints = [(0,0,50), (500,500,75), (1000,500,100), (1000,1000,75), (0,0,50)]
    m5 = gen.custom(custom_waypoints, drone_id="CUSTOM-001")
    print_mission_summary(m5)

    print("\n6. Random Mission Type:")
    m6 = gen.random_mission(drone_id="RANDOM-001", seed=123)
    print_mission_summary(m6)
    print("\nAll mission generation patterns tested!")

if __name__ == "__main__":
    test_all_patterns()
