import json

def save_mission_to_json(mission, filename):
    data = {
        'drone_id': mission.drone_id,
        'start_time': mission.start_time,
        'end_time': mission.end_time,
        'cruise_speed': mission.cruise_speed,
        'waypoints': [{'x': wp.x, 'y': wp.y, 'z': wp.z} for wp in mission.waypoints],
        'computed_metrics': {
            'total_distance': mission.total_distance(),
            'duration': mission.duration(),
            'num_waypoints': len(mission.waypoints)
        }
    }
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"✓ Mission saved to {filename}")

def print_mission_summary(mission):
    print("\n" + "="*60)
    print(f"MISSION SUMMARY: {mission.drone_id}")
    print("="*60)
    print(f"Waypoints: {len(mission.waypoints)}")
    print(f"Start Time: {mission.start_time:.1f}s")
    print(f"End Time: {mission.end_time:.1f}s")
    print(f"Duration: {mission.duration():.1f}s")
    print(f"Total Distance: {mission.total_distance():.1f}m")
    print(f"Cruise Speed: {mission.cruise_speed:.2f} m/s\n")
    print("Waypoint Path:")
    for i, wp in enumerate(mission.waypoints, 1):
        print(f" {i:2d}. ({wp.x:7.1f}, {wp.y:7.1f}, {wp.z:6.1f})")
    print("="*60 + "\n")
