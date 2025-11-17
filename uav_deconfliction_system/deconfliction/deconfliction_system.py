"""
Production-grade UAV Deconfliction System.

Integrates all three stages:
1. Multi-Tier Filtering (Stage 1)
2. 4D Occupancy Grid (Stage 2)
3. Risk Scoring (Stage 3)

Provides single interface for mission conflict checking.
"""

import time
from typing import Dict, List, Tuple
from .models import Mission, Conflict, Severity
from .filters import Stage1MultiTierFilter
from .occupancy_grid import Stage2OccupancyGrid
from .risk_scoring import Stage3RiskScoring


class ProductionDeconflictionSystem:
    """
    Production-grade UAV deconfliction system.

    Handles 10,000+ drone scenarios efficiently through staged filtering.
    """

    def __init__(self,
                 base_safety_buffer: float = 50.0,
                 reaction_time: float = 2.5,
                 max_accel: float = 5.0,
                 gps_uncertainty: float = 10.0):
        """
        Initialize deconfliction system.

        Args:
            base_safety_buffer: Minimum safe distance (meters)
            reaction_time: Pilot/system reaction time (seconds)
            max_accel: Maximum acceleration capability (m/s²)
            gps_uncertainty: GPS positioning error (meters)
        """
        # Stage 1: Multi-Tier Filtering
        self.stage1 = Stage1MultiTierFilter(
            time_margin=30.0, 
            spatial_margin=500.0
        )

        # Stage 2: 4D Occupancy Grid
        self.stage2 = Stage2OccupancyGrid(
            cell_size=100.0, 
            time_resolution=1.0
        )

        # Stage 3: Risk Scoring
        self.stage3 = Stage3RiskScoring(
            base_safety_buffer=base_safety_buffer,
            reaction_time=reaction_time,
            max_accel=max_accel,
            gps_uncertainty=gps_uncertainty
        )

        self.all_missions: Dict[str, Mission] = {}
        self.performance_metrics = {}

    def register_mission(self, mission: Mission):
        """
        Register a mission in the airspace.

        Args:
            mission: Mission object to register
        """
        self.all_missions[mission.drone_id] = mission

    def check_mission(self, 
                     primary_mission: Mission) -> Tuple[bool, List[Conflict], Dict]:
        """
        Execute 3-stage conflict detection pipeline.

        Args:
            primary_mission: Mission to check for conflicts

        Returns:
            Tuple of (is_clear, conflicts, metrics)
            - is_clear: True if no HIGH/CRITICAL conflicts
            - conflicts: List of detected conflicts
            - metrics: Performance metrics dictionary
        """
        start_time = time.time()
        metrics = {}

        # Get all other missions
        other_missions = [m for m in self.all_missions.values()
                         if m.drone_id != primary_mission.drone_id]

        # STAGE 1: Multi-Tier Filtering
        stage1_start = time.time()
        candidates = self.stage1.filter(primary_mission, other_missions)
        metrics['stage1_time'] = time.time() - stage1_start
        metrics['stage1_reduction'] = f"{len(other_missions)} → {len(candidates)}"

        if len(candidates) == 0:
            metrics['total_time'] = time.time() - start_time
            return True, [], metrics

        # STAGE 2: 4D Occupancy Grid
        stage2_start = time.time()
        self.stage2.build_grid(candidates)

        # Compute dynamic safety buffer
        dynamic_buffer = self.stage3.compute_dynamic_safety_buffer(
            primary_mission.cruise_speed
        )

        raw_conflicts = self.stage2.query_trajectory(primary_mission, dynamic_buffer)
        metrics['stage2_time'] = time.time() - stage2_start
        metrics['raw_conflicts'] = len(raw_conflicts)

        if len(raw_conflicts) == 0:
            metrics['stage3_time'] = 0.0
            metrics['total_time'] = time.time() - start_time
            return True, [], metrics

        # STAGE 3: Risk Scoring
        stage3_start = time.time()
        candidate_dict = {m.drone_id: m for m in candidates}
        assessed_conflicts = self.stage3.assess_conflicts(
            primary_mission, raw_conflicts, candidate_dict
        )
        metrics['stage3_time'] = time.time() - stage3_start
        metrics['assessed_conflicts'] = len(assessed_conflicts)
        metrics['total_time'] = time.time() - start_time

        # Determine if mission is clear (no HIGH or CRITICAL conflicts)
        critical_conflicts = [c for c in assessed_conflicts
                            if c.severity in [Severity.CRITICAL, Severity.HIGH]]
        is_clear = len(critical_conflicts) == 0

        self.performance_metrics = metrics
        return is_clear, assessed_conflicts, metrics

    def generate_report(self, 
                       primary_mission: Mission,
                       is_clear: bool, 
                       conflicts: List[Conflict],
                       metrics: Dict) -> str:
        """
        Generate comprehensive mission analysis report.

        Args:
            primary_mission: Mission that was checked
            is_clear: Whether mission is clear for takeoff
            conflicts: List of detected conflicts
            metrics: Performance metrics

        Returns:
            Formatted report string
        """
        report = "\n" + "█" * 80 + "\n"
        report += "█" + " UAV DECONFLICTION SYSTEM - ANALYSIS REPORT ".center(78) + "█\n"
        report += "█" * 80 + "\n\n"

        # Mission Info
        report += f"Primary Mission: {primary_mission.drone_id}\n"
        report += f"Time Window: {primary_mission.start_time:.1f}s - {primary_mission.end_time:.1f}s\n"
        report += f"Cruise Speed: {primary_mission.cruise_speed:.2f} m/s\n"
        report += f"Total Distance: {primary_mission.total_distance():.1f}m\n"

        # Dynamic Safety Buffer
        dynamic_buffer = self.stage3.compute_dynamic_safety_buffer(
            primary_mission.cruise_speed
        )
        report += f"\nDynamic Safety Buffer: {dynamic_buffer:.1f}m\n"

        # Stage 1 Filtering
        report += self.stage1.get_filtering_report()

        # Performance Metrics
        report += "\n" + "="*70 + "\n"
        report += "PERFORMANCE METRICS\n"
        report += "="*70 + "\n"
        report += f"Stage 1 (Filtering):     {metrics.get('stage1_time', 0)*1000:6.2f}ms\n"
        report += f"Stage 2 (Occupancy Grid): {metrics.get('stage2_time', 0)*1000:6.2f}ms\n"
        report += f"Stage 3 (Risk Scoring):   {metrics.get('stage3_time', 0)*1000:6.2f}ms\n"
        report += f"Total Processing Time:    {metrics.get('total_time', 0)*1000:6.2f}ms\n"
        report += "="*70 + "\n"

        # Conflict Analysis
        report += "\n" + "="*70 + "\n"
        if is_clear:
            report += "STATUS: ✓ CLEAR FOR TAKEOFF\n"
        else:
            report += "STATUS: ✗ CONFLICT DETECTED\n"
        report += "="*70 + "\n"

        if len(conflicts) > 0:
            # Severity breakdown
            severity_counts = {}
            for sev in Severity:
                count = len([c for c in conflicts if c.severity == sev])
                if count > 0:
                    severity_counts[sev.name] = count

            report += "\nConflict Breakdown:\n"
            for sev, count in sorted(severity_counts.items(),
                                    key=lambda x: Severity[x[0]].value, 
                                    reverse=True):
                report += f"  {sev}: {count}\n"

            # Top conflicts
            report += "\n" + "-"*70 + "\n"
            report += "TOP CONFLICTS (Ranked by Risk):\n"
            report += "-"*70 + "\n"

            for i, conflict in enumerate(conflicts[:5], 1):
                report += f"\n{i}. {conflict}\n"
                report += f"   → {conflict.recommendation}\n"

            if len(conflicts) > 5:
                report += f"\n... and {len(conflicts) - 5} more conflicts\n"

        # Final recommendation
        critical_count = len([c for c in conflicts if c.severity == Severity.CRITICAL])
        high_count = len([c for c in conflicts if c.severity == Severity.HIGH])

        report += "\n" + "="*70 + "\n"
        report += "FINAL RECOMMENDATION:\n"
        report += "="*70 + "\n"

        if critical_count > 0:
            report += f"✗ REJECT MISSION - {critical_count} CRITICAL conflict(s).\n"
            report += "  Action: Reroute or delay mission by at least 60 seconds.\n"
        elif high_count > 0:
            report += f"⚠ HIGH RISK - {high_count} HIGH severity conflict(s).\n"
            report += "  Recommended: Adjust altitude by ±50m or delay by 30s.\n"
        else:
            report += "✓ CLEAR - No critical conflicts detected.\n"

        report += "\n" + "█" * 80 + "\n"
        return report
