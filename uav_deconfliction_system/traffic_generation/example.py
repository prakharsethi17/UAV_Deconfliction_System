"""
Example usage of Traffic Generation System.

Demonstrates generating diverse traffic missions with all 11 pattern types.
"""

from .generator import TrafficGenerator
import random
import numpy as np


def main():
    print("="*70)
    print("TRAFFIC GENERATION SYSTEM - EXAMPLE")
    print("="*70)
    
    # Initialize generator
    gen = TrafficGenerator(
        airspace_x=5000,
        airspace_y=5000,
        airspace_z=1000,
        velocity=12,
        flight_duration=600
    )
    
    print("\nGenerating 50 diverse traffic drones...")
    print("-"*70)
    
    # Set seed for reproducibility
    random.seed(42)
    np.random.seed(42)
    
    # Generate traffic
    gen.generate_traffic(num_drones=50)
    
    print(f"\n✓ Generated {len(gen.missions)} traffic missions")
    
    # Pattern statistics
    pattern_counts = {}
    for mission in gen.missions:
        # Infer pattern from waypoint count and structure
        num_waypoints = len(mission.waypoints)
        if num_waypoints == 2:
            pattern = "Flyby"
        elif num_waypoints == 4:
            pattern = "Triangular"
        elif num_waypoints == 5:
            pattern = "Holding Pattern"
        elif num_waypoints == 9:
            pattern = "Circular"
        elif num_waypoints == 11:
            pattern = "Star"
        elif num_waypoints == 20:
            pattern = "Figure-8 / Lowrise"
        elif num_waypoints == 40:
            pattern = "Highrise Inspection"
        elif num_waypoints >= 10:
            pattern = "Grid / Mapping"
        else:
            pattern = "Random"
        
        pattern_counts[pattern] = pattern_counts.get(pattern, 0) + 1
    
    print("\n" + "="*70)
    print("PATTERN DISTRIBUTION")
    print("="*70)
    for pattern, count in sorted(pattern_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {pattern:20s}: {count:2d} drones")
    
    # Display sample missions
    print("\n" + "="*70)
    print("SAMPLE MISSIONS (First 5)")
    print("="*70)
    
    for i, mission in enumerate(gen.missions[:5], 1):
        print(f"\n{i}. {mission.drone_id}")
        print(f"   Waypoints: {len(mission.waypoints)}")
        print(f"   Duration: {mission.duration():.1f}s")
        print(f"   Distance: {mission.total_distance():.1f}m")
        print(f"   Speed: {mission.cruise_speed:.2f} m/s")
        print(f"   Start: ({mission.waypoints[0].x:.0f}, {mission.waypoints[0].y:.0f}, {mission.waypoints[0].z:.0f})")
        print(f"   End: ({mission.waypoints[-1].x:.0f}, {mission.waypoints[-1].y:.0f}, {mission.waypoints[-1].z:.0f})")
    
    # Statistics
    print("\n" + "="*70)
    print("OVERALL STATISTICS")
    print("="*70)
    
    total_distance = sum(m.total_distance() for m in gen.missions)
    avg_distance = total_distance / len(gen.missions) if gen.missions else 0
    
    total_duration = sum(m.duration() for m in gen.missions)
    avg_duration = total_duration / len(gen.missions) if gen.missions else 0
    
    altitudes = [wp.z for m in gen.missions for wp in m.waypoints]
    min_alt = min(altitudes) if altitudes else 0
    max_alt = max(altitudes) if altitudes else 0
    avg_alt = sum(altitudes) / len(altitudes) if altitudes else 0
    
    print(f"  Total Missions: {len(gen.missions)}")
    print(f"  Average Distance: {avg_distance:.1f}m")
    print(f"  Average Duration: {avg_duration:.1f}s")
    print(f"  Altitude Range: {min_alt:.1f}m - {max_alt:.1f}m (avg: {avg_alt:.1f}m)")
    print(f"  Total Waypoints: {sum(len(m.waypoints) for m in gen.missions)}")
    
    print("\n" + "="*70)
    print("✓ Traffic generation complete!")
    print("="*70)


if __name__ == "__main__":
    main()
