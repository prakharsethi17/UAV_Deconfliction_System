"""
Example usage of UAV Deconfliction System.

Demonstrates complete workflow with simulated traffic.
"""

import numpy as np
from .models import Mission, Waypoint
from .deconfliction_system import ProductionDeconflictionSystem


def main():
    """Run example deconfliction scenario."""
    print("UAV Deconfliction System - Example\n")
    print("="*70)

    # Initialize system
    system = ProductionDeconflictionSystem(
        base_safety_buffer=50.0,
        reaction_time=2.5,
        max_accel=5.0,
        gps_uncertainty=10.0
    )

    # Define primary mission
    primary = Mission(
        waypoints=[
            Waypoint(0, 0, 100),
            Waypoint(1000, 1000, 150),
            Waypoint(2000, 0, 100),
        ],
        start_time=0,
        end_time=300,
        drone_id="PRIMARY-ALPHA"
    )

    print(f"\nPrimary Mission: {primary.drone_id}")
    print(f"  Cruise Speed: {primary.cruise_speed:.2f} m/s")
    print(f"  Distance: {primary.total_distance():.1f}m")
    print(f"  Duration: {primary.duration():.1f}s\n")

    # Simulate 100 traffic drones
    print("Generating simulated traffic (100 drones)...")
    np.random.seed(42)

    for i in range(100):
        # Random waypoints in 3000×3000×200m airspace
        x1, y1 = np.random.rand(2) * 3000 - 500
        x2, y2 = np.random.rand(2) * 3000 - 500
        z = np.random.rand() * 200 + 50

        t_start = np.random.rand() * 200
        t_end = t_start + 200 + np.random.rand() * 200

        traffic = Mission(
            waypoints=[
                Waypoint(x1, y1, z),
                Waypoint(x2, y2, z + np.random.randn() * 20)
            ],
            start_time=t_start,
            end_time=t_end,
            drone_id=f"TRAFFIC-{i:03d}"
        )

        system.register_mission(traffic)

    print(f"✓ Registered {len(system.all_missions)} missions\n")

    # Execute deconfliction check
    print("Executing 3-Stage Deconfliction Analysis...")
    print("-" * 70)

    is_clear, conflicts, metrics = system.check_mission(primary)

    # Generate and print report
    report = system.generate_report(primary, is_clear, conflicts, metrics)
    print(report)

    # Summary
    if is_clear:
        print("\n✅ RESULT: Mission APPROVED for flight")
    else:
        print("\n❌ RESULT: Mission REJECTED - conflicts detected")

    print(f"\nTotal conflicts detected: {len(conflicts)}")
    print(f"Processing time: {metrics['total_time']*1000:.2f}ms")


if __name__ == "__main__":
    main()
