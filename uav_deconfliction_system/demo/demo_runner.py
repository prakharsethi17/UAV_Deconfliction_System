"""
UAV Deconfliction Demo Runner

Orchestrates complete demo workflow:
1. Generate primary drone mission
2. Generate traffic drones
3. Run deconfliction analysis  
4. Export results
"""

import json
import time
import os
import numpy as np
import random
from typing import List, Dict, Tuple
from datetime import datetime

from primary_path_generation import PrimaryDroneGenerator
from traffic_generation import TrafficGenerator
from deconfliction import ProductionDeconflictionSystem, Mission, Waypoint, Conflict, Severity
from .reporting import generate_summary_report, export_results_to_files


class UAVDeconflictionDemo:
    """
    Integration demo for UAV Strategic Deconfliction System.
    
    Orchestrates the complete workflow:
    1. Generate primary drone mission
    2. Generate traffic drones (50-100)
    3. Run deconfliction analysis
    4. Export results for visualization
    """
    
    def __init__(self,
                 airspace_x: float = 5000.0,
                 airspace_y: float = 5000.0,
                 airspace_z: float = 1000.0,
                 num_traffic_drones: int = None,
                 seed: int = None):
        """
        Initialize demo environment.
        
        Args:
            airspace_x: X-axis dimension (meters)
            airspace_y: Y-axis dimension (meters)
            airspace_z: Z-axis dimension (meters)
            num_traffic_drones: Number of traffic drones (None = random 50-100)
            seed: Random seed for reproducibility
        """
        self.airspace_x = airspace_x
        self.airspace_y = airspace_y
        self.airspace_z = airspace_z
        self.num_traffic_drones = num_traffic_drones
        self.seed = seed
        
        print("\n" + "="*80)
        print("UAV STRATEGIC DECONFLICTION SYSTEM - INITIALIZATION")
        print("="*80)
        
        # Set random seeds if provided
        if self.seed is not None:
            random.seed(self.seed)
            np.random.seed(self.seed)
        
        # Initialize generators
        self.primary_gen = PrimaryDroneGenerator(
            airspace_x=airspace_x,
            airspace_y=airspace_y,
            airspace_z=airspace_z,
            default_velocity=12.0
        )
        
        self.traffic_gen = TrafficGenerator(
            airspace_x=airspace_x,
            airspace_y=airspace_y,
            airspace_z=airspace_z,
            velocity=12.0,
            flight_duration=600.0
        )
        
        self.deconfliction_system = ProductionDeconflictionSystem(
            base_safety_buffer=50.0,
            reaction_time=2.5,
            max_accel=5.0,
            gps_uncertainty=10.0
        )
        
        self.primary_mission: Mission = None
        self.traffic_missions: List[Mission] = []
        self.results: Dict = {}
        
        print(f"✓ Airspace: {self.airspace_x}m × {self.airspace_y}m × {self.airspace_z}m")
        print(f"✓ Target traffic drones: {self.num_traffic_drones or 'Random (50-100)'}")
        print(f"✓ Random seed: {self.seed or 'None (random)'}")
        print("="*80)
    
    def generate_primary_mission(self, mission_type: str = "random", **kwargs) -> Mission:
        """
        Generate primary drone mission.
        
        Args:
            mission_type: Type of mission ('straight_line', 'multi_waypoint', 
                         'grid_survey', 'circular_inspection', 'custom', 'random')
            **kwargs: Mission-specific parameters
            
        Returns:
            Generated Mission object
        """
        print("\n" + "-"*80)
        print("STEP 1: GENERATING PRIMARY DRONE MISSION")
        print("-"*80)
        
        if mission_type == "straight_line":
            self.primary_mission = self.primary_gen.straight_line(
                kwargs.get('start_pos', (0, 0, 100)),
                kwargs.get('end_pos', (4000, 4000, 100)),
                kwargs.get('start_time', 0.0),
                kwargs.get('velocity', None),
                drone_id="PRIMARY_DRONE"
            )
            print("✓ Generated straight-line mission")
        
        elif mission_type == "multi_waypoint":
            self.primary_mission = self.primary_gen.multi_waypoint(
                kwargs.get('num_waypoints', 5),
                kwargs.get('altitude_range', (100, 300)),
                kwargs.get('start_time', 0.0),
                kwargs.get('velocity', None),
                drone_id="PRIMARY_DRONE",
                seed=self.seed
            )
            print(f"✓ Generated multi-waypoint mission ({len(self.primary_mission.waypoints)} waypoints)")
        
        elif mission_type == "grid_survey":
            self.primary_mission = self.primary_gen.grid_survey(
                kwargs.get('grid_origin', (500, 500, 120)),
                kwargs.get('grid_width', 2000),
                kwargs.get('grid_height', 2000),
                kwargs.get('num_rows', 5),
                kwargs.get('start_time', 300.0),
                kwargs.get('velocity', None),
                drone_id="PRIMARY_DRONE"
            )
            print(f"✓ Generated grid survey mission ({kwargs.get('num_rows', 5)} rows)")
        
        elif mission_type == "circular_inspection":
            self.primary_mission = self.primary_gen.circular_inspection(
                kwargs.get('center', (2500, 2500, 150)),
                kwargs.get('radius', 800),
                kwargs.get('num_points', 12),
                kwargs.get('start_time', 600.0),
                kwargs.get('velocity', None),
                drone_id="PRIMARY_DRONE"
            )
            print(f"✓ Generated circular inspection mission ({kwargs.get('num_points', 12)} points)")
        
        elif mission_type == "custom":
            waypoint_coords = kwargs.get('waypoint_coords')
            if waypoint_coords is None:
                raise ValueError("custom mission requires 'waypoint_coords' parameter")
            
            self.primary_mission = self.primary_gen.custom(
                waypoint_coords=waypoint_coords,
                start_time=kwargs.get('start_time', 0.0),
                velocity=kwargs.get('velocity', None),
                drone_id="PRIMARY_DRONE"
            )
            print(f"✓ Generated custom mission ({len(waypoint_coords)} waypoints)")
        
        else:  # random
            self.primary_mission = self.primary_gen.random_mission(
                kwargs.get('start_time', 300.0),
                kwargs.get('velocity', None),
                drone_id="PRIMARY_DRONE",
                seed=self.seed
            )
            print("✓ Generated random mission type")
        
        print(f"  - Waypoints: {len(self.primary_mission.waypoints)}")
        print(f"  - Start Time: {self.primary_mission.start_time:.1f}s")
        print(f"  - End Time: {self.primary_mission.end_time:.1f}s")
        print(f"  - Duration: {self.primary_mission.duration():.1f}s")
        print(f"  - Distance: {self.primary_mission.total_distance():.1f}m")
        print(f"  - Cruise Speed: {self.primary_mission.cruise_speed:.2f} m/s")
        print("-"*80)
        
        return self.primary_mission
    
    def generate_traffic(self) -> List[Mission]:
        """
        Generate traffic drone missions.
        
        Returns:
            List of traffic Mission objects
        """
        print("\n" + "-"*80)
        print("STEP 2: GENERATING TRAFFIC DRONES")
        print("-"*80)
        
        num_drones = self.num_traffic_drones or random.randint(50, 100)
        self.traffic_gen.generate_traffic(num_drones=num_drones)
        self.traffic_missions = self.traffic_gen.missions
        
        print(f"✓ Generated {len(self.traffic_missions)} traffic drones")
        print(f"  - Flight duration: 600s (10 minutes) each")
        print(f"  - Cruise speed: 12 m/s (constant)")
        print(f"  - Simulation window: 0-3600s (1 hour)")
        
        if self.traffic_missions:
            start_times = [m.start_time for m in self.traffic_missions]
            distances = [m.total_distance() for m in self.traffic_missions]
            print(f"  - Start time range: {min(start_times):.1f}s - {max(start_times):.1f}s")
            print(f"  - Distance range: {min(distances):.1f}m - {max(distances):.1f}m")
            print(f"  - Average distance: {np.mean(distances):.1f}m")
        
        print("-"*80)
        return self.traffic_missions
    
    def run_deconfliction_analysis(self) -> Tuple[bool, List[Conflict], Dict]:
        """
        Execute 3-stage deconfliction analysis.
        
        Returns:
            Tuple of (is_clear, conflicts, metrics)
        """
        print("\n" + "-"*80)
        print("STEP 3: RUNNING DECONFLICTION ANALYSIS")
        print("-"*80)
        print("Executing 3-stage pipeline:")
        print("  Stage 1: Multi-Tier Filtering (Temporal → BBox → Coarse Spatial)")
        print("  Stage 2: 4D Occupancy Grid (High-precision detection)")
        print("  Stage 3: Risk Scoring & Prioritization")
        print()
        
        # Register all traffic missions
        for mission in self.traffic_missions:
            self.deconfliction_system.register_mission(mission)
        print(f"✓ Registered {len(self.traffic_missions)} traffic drones")
        
        # Run analysis
        analysis_start = time.time()
        is_clear, conflicts, metrics = self.deconfliction_system.check_mission(self.primary_mission)
        analysis_time = time.time() - analysis_start
        
        print(f"✓ Analysis completed in {analysis_time*1000:.2f}ms")
        print()
        
        # Print stage performance
        print("Stage Performance:")
        print(f"  Stage 1 (Filtering):    {metrics.get('stage1_time', 0)*1000:.2f}ms")
        print(f"  Reduction: {metrics.get('stage1_reduction', 0)}")
        print(f"  Stage 2 (Grid):         {metrics.get('stage2_time', 0)*1000:.2f}ms")
        print(f"  Raw conflicts: {metrics.get('raw_conflicts', 0)}")
        print(f"  Stage 3 (Risk):         {metrics.get('stage3_time', 0)*1000:.2f}ms")
        print(f"  Assessed conflicts: {metrics.get('assessed_conflicts', 0)}")
        print()
        
        # Decision summary
        if is_clear:
            print("✓ MISSION CLEARED - No critical conflicts detected")
        else:
            critical_count = len([c for c in conflicts if c.severity == Severity.CRITICAL])
            high_count = len([c for c in conflicts if c.severity == Severity.HIGH])
            warning_count = len([c for c in conflicts if c.severity == Severity.WARNING])
            print(f"✗ MISSION REJECTED - {len(conflicts)} conflicts detected:")
            print(f"  CRITICAL: {critical_count}")
            print(f"  HIGH: {high_count}")
            print(f"  WARNING: {warning_count}")
        
        print("-"*80)
        
        self.results = {
            'is_clear': is_clear,
            'conflicts': conflicts,
            'metrics': metrics,
            'analysis_time': analysis_time
        }
        
        return is_clear, conflicts, metrics
    
    def print_conflict_details(self, max_conflicts: int = 10):
        """
        Print detailed conflict information.
        
        Args:
            max_conflicts: Maximum number of conflicts to display
        """
        conflicts = self.results.get('conflicts', [])
        if not conflicts:
            print("\nNo conflicts to display.")
            return
        
        print("\n" + "="*80)
        print("DETAILED CONFLICT REPORT")
        print("="*80)
        
        top_conflicts = sorted(conflicts, key=lambda c: c.risk_score, reverse=True)[:max_conflicts]
        
        for i, conflict in enumerate(top_conflicts, 1):
            print(f"\nConflict #{i}:")
            print(f"  Severity: {conflict.severity.name}")
            print(f"  Risk Score: {conflict.risk_score:.3f}")
            print(f"  Time: {conflict.time:.1f}s")
            print(f"  Location: ({conflict.location.x:.1f}, {conflict.location.y:.1f}, {conflict.location.z:.1f})")
            print(f"  Conflicting Drone: {conflict.conflicting_drone}")
            print(f"  Separation: {conflict.separation_distance:.1f}m")
            print(f"  Relative Velocity: {conflict.relative_velocity:.1f} m/s")
            print(f"  Time to Collision: {conflict.time_to_collision:.1f}s")
            print(f"  Conflict Duration: {conflict.conflict_duration:.1f}s")
            print(f"  Recommendation: {conflict.recommendation}")
        
        if len(conflicts) > max_conflicts:
            print(f"\n... and {len(conflicts) - max_conflicts} more conflicts")
        
        print("="*80)
    
    def export_results(self, output_dir: str = "./output"):
        """
        Export all results to JSON files and summary report.
        
        Args:
            output_dir: Directory to save output files
        """
        print("\n" + "-"*80)
        print("STEP 4: EXPORTING RESULTS")
        print("-"*80)
        
        os.makedirs(output_dir, exist_ok=True)
        
        # Export using reporting module
        export_results_to_files(
            self.primary_mission,
            self.traffic_missions,
            self.results,
            self.airspace_x,
            self.airspace_y,
            self.airspace_z,
            output_dir
        )
        
        print(f"\n✓ All results exported to: {output_dir}")
        print("-"*80)
    
    def run_complete_demo(self, mission_type: str = "random", 
                         output_dir: str = "./output", **mission_kwargs):
        """
        Execute complete demo workflow.
        
        Args:
            mission_type: Type of primary mission
            output_dir: Output directory for results
            **mission_kwargs: Mission-specific parameters
            
        Returns:
            Tuple of (is_clear, conflicts, metrics)
        """
        print("\n" + "█" * 80)
        print("█" + " UAV STRATEGIC DECONFLICTION SYSTEM - COMPLETE DEMO ".center(78) + "█")
        print("█" * 80)
        
        # Run all steps
        self.generate_primary_mission(mission_type, **mission_kwargs)
        self.generate_traffic()
        is_clear, conflicts, metrics = self.run_deconfliction_analysis()
        
        if conflicts:
            self.print_conflict_details(max_conflicts=5)
        
        self.export_results(output_dir)
        
        # Final summary
        print("\n" + "█" * 80)
        if is_clear:
            print("█" + " ✓ DEMO COMPLETED: MISSION CLEARED ".center(78) + "█")
        else:
            print("█" + f" ✗ DEMO COMPLETED: {len(conflicts)} CONFLICTS DETECTED ".center(78) + "█")
        print("█" * 80)
        
        return is_clear, conflicts, metrics


def main():
    """
    Main demo execution with multiple scenarios.
    """
    print("""
╔════════════════════════════════════════════════════════════════════════════╗
║                                                                            ║
║         UAV STRATEGIC DECONFLICTION SYSTEM - INTEGRATION DEMO              ║
║                                                                            ║
║                    FlytBase Robotics Assignment 2025                       ║
║                 Integrated System Demo (No Visualization)                  ║
║                                                                            ║
╚════════════════════════════════════════════════════════════════════════════╝
""")
    
    # Scenario 1: Random Mission
    print("\n" + "=" * 80)
    print("SCENARIO 1: RANDOM MISSION TYPE")
    print("=" * 80)
    demo1 = UAVDeconflictionDemo(
        airspace_x=5000.0,
        airspace_y=5000.0,
        airspace_z=1000.0,
        num_traffic_drones=75,
        seed=42
    )
    demo1.run_complete_demo(
        mission_type="random",
        start_time=300.0,
        output_dir="./output/scenario1_random"
    )
    
    # Scenario 2: Grid Survey
    print("\n" + "=" * 80)
    print("SCENARIO 2: GRID SURVEY MISSION")
    print("=" * 80)
    demo2 = UAVDeconflictionDemo(
        airspace_x=5000.0,
        airspace_y=5000.0,
        airspace_z=1000.0,
        num_traffic_drones=80,
        seed=123
    )
    demo2.run_complete_demo(
        mission_type="grid_survey",
        grid_origin=(1000, 1000, 120),
        grid_width=2000,
        grid_height=2000,
        num_rows=6,
        start_time=500.0,
        output_dir="./output/scenario2_grid"
    )
    
    # Scenario 3: Circular Inspection
    print("\n" + "=" * 80)
    print("SCENARIO 3: CIRCULAR INSPECTION MISSION")
    print("=" * 80)
    demo3 = UAVDeconflictionDemo(
        airspace_x=5000.0,
        airspace_y=5000.0,
        airspace_z=1000.0,
        num_traffic_drones=60,
        seed=456
    )
    demo3.run_complete_demo(
        mission_type="circular_inspection",
        center=(2500, 2500, 200),
        radius=600,
        num_points=16,
        start_time=800.0,
        output_dir="./output/scenario3_circular"
    )
    
    # Scenario 4: Straight Line
    print("\n" + "=" * 80)
    print("SCENARIO 4: STRAIGHT LINE MISSION")
    print("=" * 80)
    demo4 = UAVDeconflictionDemo(
        airspace_x=5000.0,
        airspace_y=5000.0,
        airspace_z=1000.0,
        num_traffic_drones=50,
        seed=789
    )
    demo4.run_complete_demo(
        mission_type="straight_line",
        start_pos=(0, 0, 100),
        end_pos=(5000, 5000, 150),
        start_time=1200.0,
        output_dir="./output/scenario4_straight"
    )
    
    print("\n" + "█" * 80)
    print("█" + " ALL SCENARIOS COMPLETED ".center(78) + "█")
    print("█" * 80)
    
    print("\nOutput files generated in ./output/ directory:")
    print("  - scenario1_random/")
    print("  - scenario2_grid/")
    print("  - scenario3_circular/")
    print("  - scenario4_straight/")
    print("\nEach scenario directory contains:")
    print("  - primary_mission.json")
    print("  - traffic_missions.json")
    print("  - deconfliction_results.json")
    print("  - summary_report.txt")
    print("\nThese files are ready for visualization processing.")
    print("=" * 80)


if __name__ == "__main__":
    main()
