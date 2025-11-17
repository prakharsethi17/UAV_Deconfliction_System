"""
Reporting utilities for UAV Deconfliction demo.

Includes functions for creating detailed summary reports and exporting
deconfliction results, missions, and metrics to disk.
"""

import os
import json
from datetime import datetime
from typing import List, Dict

from deconfliction import Mission, Conflict, Severity


def generate_summary_report(
    primary_mission: Mission,
    traffic_missions: List[Mission],
    conflicts: List[Conflict],
    metrics: Dict,
    analysis_time: float
) -> str:
    """
    Generate a formatted textual summary report string for UAV deconfliction.

    Args:
        primary_mission: Primary drone Mission object
        traffic_missions: List of traffic Missions
        conflicts: List of Conflict objects detected
        metrics: Dictionary of analysis metrics and timings
        analysis_time: Total analysis time in seconds

    Returns:
        A detailed formatted string report.
    """
    report = []
    report.append("=" * 80)
    report.append("UAV STRATEGIC DECONFLICTION SYSTEM - SUMMARY REPORT")
    report.append("=" * 80)
    report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("")
    report.append("PRIMARY MISSION")
    report.append("-" * 80)
    report.append(f"Drone ID: {primary_mission.drone_id}")
    report.append(f"Waypoints: {len(primary_mission.waypoints)}")
    report.append(f"Time Window: {primary_mission.start_time:.1f}s - {primary_mission.end_time:.1f}s")
    # Call if method, else just get property
    duration = primary_mission.duration() if callable(primary_mission.duration) else primary_mission.duration
    total_distance = primary_mission.total_distance() if callable(primary_mission.total_distance) else primary_mission.total_distance
    report.append(f"Duration: {duration:.1f}s")
    report.append(f"Total Distance: {total_distance:.1f}m")
    report.append(f"Cruise Speed: {primary_mission.cruise_speed:.2f} m/s")
    report.append("")
    report.append("TRAFFIC ENVIRONMENT")
    report.append("-" * 80)
    report.append(f"Total Traffic Drones: {len(traffic_missions)}")
    report.append("")
    report.append("DECONFLICTION ANALYSIS")
    report.append("-" * 80)
    report.append(f"Stage 1 (Filtering): {metrics.get('stage1_time', 0)*1000:.2f} ms")
    report.append(f"Reduction: {metrics.get('stage1_reduction', 0)}")
    report.append(f"Stage 2 (Grid): {metrics.get('stage2_time', 0)*1000:.2f} ms")
    report.append(f"Raw conflicts: {metrics.get('raw_conflicts', 0)}")
    report.append(f"Stage 3 (Risk): {metrics.get('stage3_time', 0)*1000:.2f} ms")
    report.append(f"Assessed conflicts: {metrics.get('assessed_conflicts', 0)}")
    report.append(f"Total Analysis Time: {analysis_time*1000:.2f} ms")
    report.append("")
    report.append("DECISION")
    report.append("-" * 80)

    if any(c.severity == Severity.CRITICAL for c in conflicts):
        report.append("STATUS: ✗ MISSION REJECTED - Critical conflicts detected.")
    else:
        report.append("STATUS: ✓ MISSION CLEARED - No critical conflicts detected.")

    report.append("")
    if conflicts:
        severity_counts = {sev: 0 for sev in Severity}
        for c in conflicts:
            severity_counts[c.severity] += 1

        report.append("CONFLICT SUMMARY")
        report.append("-" * 80)
        report.append(f"Total Conflicts: {len(conflicts)}")
        for sev in Severity:
            report.append(f"  {sev.name}: {severity_counts.get(sev, 0)}")

        report.append("")
        report.append("TOP 5 HIGHEST RISK CONFLICTS")
        report.append("-" * 80)

        top_conflicts = sorted(conflicts, key=lambda c: c.risk_score, reverse=True)[:5]
        for i, c in enumerate(top_conflicts, 1):
            report.append(f"{i}. [{c.severity.name}] vs {c.conflicting_drone}")
            report.append(f"    Risk: {c.risk_score:.3f} | Separation: {c.separation_distance:.1f}m | Time: {c.time:.1f}s")
            report.append(f"    Recommendation: {c.recommendation}")
            report.append("")

    report.append("=" * 80)
    report.append("END OF REPORT")
    report.append("=" * 80)

    return "\n".join(report)


def export_results_to_files(
    primary_mission: Mission,
    traffic_missions: List[Mission],
    results: Dict,
    airspace_x: float,
    airspace_y: float,
    airspace_z: float,
    output_dir: str
) -> None:
    """
    Export missions, conflicts, metrics, and summary reports to JSON and TXT files.

    Args:
        primary_mission: Primary Mission object
        traffic_missions: List of traffic Mission objects
        results: Dict containing 'conflicts', 'metrics', 'analysis_time', 'is_clear'
        airspace_x: Airspace X dimension
        airspace_y: Airspace Y dimension
        airspace_z: Airspace Z dimension
        output_dir: Directory path to save exported files
    """
    os.makedirs(output_dir, exist_ok=True)

    # Export primary mission JSON
    primary_json = {
        "drone_id": primary_mission.drone_id,
        "start_time": primary_mission.start_time,
        "end_time": primary_mission.end_time,
        "cruise_speed": primary_mission.cruise_speed,
        "waypoints": [{"x": wp.x, "y": wp.y, "z": wp.z} for wp in primary_mission.waypoints],
        "total_distance": primary_mission.total_distance() if callable(primary_mission.total_distance) else primary_mission.total_distance,
        "duration": primary_mission.duration() if callable(primary_mission.duration) else primary_mission.duration,
    }
    with open(os.path.join(output_dir, "primary_mission.json"), "w") as f:
        json.dump(primary_json, f, indent=2)

    # Export traffic missions JSON
    traffic_json = {
        "metadata": {
            "num_drones": len(traffic_missions),
            "airspace_dimensions": {"x": airspace_x, "y": airspace_y, "z": airspace_z},
            "simulation_duration": 3600,
            "flight_duration": 600,
            "velocity": 12,
        },
        "traffic": [
            {
                "drone_id": m.drone_id,
                "start_time": m.start_time,
                "end_time": m.end_time,
                "cruise_speed": m.cruise_speed,
                "waypoints": [{"x": wp.x, "y": wp.y, "z": wp.z} for wp in m.waypoints],
                "total_distance": m.total_distance() if callable(m.total_distance) else m.total_distance,
                "duration": m.duration() if callable(m.duration) else m.duration,
            }
            for m in traffic_missions
        ],
    }
    with open(os.path.join(output_dir, "traffic_missions.json"), "w") as f:
        json.dump(traffic_json, f, indent=2)

    # Export deconfliction results JSON
    conflicts = results.get("conflicts", [])
    metrics = results.get("metrics", {})
    analysis_time = results.get("analysis_time", 0)
    is_clear = results.get("is_clear", True)

    results_json = {
        "is_clear": is_clear,
        "analysis_time_ms": analysis_time * 1000,
        "metrics": {
            "stage1_reduction": metrics.get("stage1_reduction", 0),
            "stage1_time_ms": metrics.get("stage1_time", 0) * 1000,
            "stage2_time_ms": metrics.get("stage2_time", 0) * 1000,
            "stage3_time_ms": metrics.get("stage3_time", 0) * 1000,
            "total_time_ms": metrics.get("total_time", 0) * 1000,
            "raw_conflicts": metrics.get("raw_conflicts", 0),
            "assessed_conflicts": metrics.get("assessed_conflicts", 0),
        },
        "conflicts": [
            {
                "time": c.time,
                "location": {"x": c.location.x, "y": c.location.y, "z": c.location.z},
                "conflicting_drone": c.conflicting_drone,
                "severity": c.severity.name,
                "risk_score": c.risk_score,
                "separation_distance": c.separation_distance,
                "relative_velocity": c.relative_velocity,
                "time_to_collision": c.time_to_collision,
                "conflict_duration": c.conflict_duration,
                "altitude_risk_factor": c.altitude_risk_factor,
                "recommendation": c.recommendation,
            }
            for c in conflicts
        ],
    }
    with open(os.path.join(output_dir, "deconfliction_results.json"), "w") as f:
        json.dump(results_json, f, indent=2)

    # Generate and save summary report text file with utf-8 encoding
    summary_report = generate_summary_report(
        primary_mission,
        traffic_missions,
        conflicts,
        metrics,
        analysis_time,
    )
    with open(os.path.join(output_dir, "summary_report.txt"), "w", encoding="utf-8") as f:
        f.write(summary_report)
