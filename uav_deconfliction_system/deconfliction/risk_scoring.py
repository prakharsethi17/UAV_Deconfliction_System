"""
Stage 3: Risk Scoring & Prioritization System.

Quantifies conflict severity based on:
- Separation distance
- Relative velocity
- Time to collision
- Conflict duration
- Altitude risk factors

Generates actionable recommendations (CLEAR/REJECT/CAUTION).
"""

import numpy as np
from typing import List, Tuple, Dict
from .models import Mission, Conflict, Severity, Waypoint
from .trajectory import ConstantVelocityTrajectory


class Stage3RiskScoring:
    """Risk assessment and conflict prioritization."""

    def __init__(self,
                 base_safety_buffer: float = 50.0,
                 reaction_time: float = 2.5,
                 max_accel: float = 5.0,
                 gps_uncertainty: float = 10.0):
        """
        Initialize risk scoring system.

        Args:
            base_safety_buffer: Minimum safe distance (meters)
            reaction_time: Pilot/system reaction time (seconds)
            max_accel: Maximum acceleration for evasion (m/s²)
            gps_uncertainty: GPS positioning uncertainty (meters)
        """
        self.base_safety_buffer = base_safety_buffer
        self.reaction_time = reaction_time
        self.max_accel = max_accel
        self.gps_uncertainty = gps_uncertainty

    def compute_dynamic_safety_buffer(self, relative_velocity: float) -> float:
        """
        Calculate dynamic safety buffer based on physics.

        Formula: buffer = base + (v_rel × t_react) + (0.5 × a × t²) + GPS_error

        Args:
            relative_velocity: Relative velocity between drones (m/s)

        Returns:
            Dynamic safety buffer in meters
        """
        velocity_term = relative_velocity * self.reaction_time
        accel_term = 0.5 * self.max_accel * (self.reaction_time ** 2)
        return (self.base_safety_buffer + velocity_term + 
                accel_term + self.gps_uncertainty)

    def assess_conflicts(self,
                        primary_mission: Mission,
                        raw_conflicts: List[Tuple[float, Waypoint, str, float]],
                        candidate_missions: Dict[str, Mission]) -> List[Conflict]:
        """
        Assess and score all detected conflicts.

        Args:
            primary_mission: Primary mission being checked
            raw_conflicts: Raw conflict detections from occupancy grid
            candidate_missions: Dictionary of candidate missions by ID

        Returns:
            List of assessed Conflict objects, sorted by risk score
        """
        primary_traj = ConstantVelocityTrajectory(primary_mission)

        # Group conflicts by drone and time window
        conflict_groups = self._group_conflicts(raw_conflicts)
        assessed_conflicts = []

        for (drone_id, time_window), conflict_list in conflict_groups.items():
            if drone_id not in candidate_missions:
                continue

            conflicting_mission = candidate_missions[drone_id]
            conflict_traj = ConstantVelocityTrajectory(conflicting_mission)

            # Get representative conflict (closest approach)
            min_distance_conflict = min(conflict_list, key=lambda x: x[3])
            t, location, _, min_separation = min_distance_conflict

            # Calculate conflict metrics
            primary_vel = primary_traj.get_velocity(t)
            conflict_vel = conflict_traj.get_velocity(t)

            if primary_vel is None or conflict_vel is None:
                continue

            relative_velocity = np.linalg.norm(primary_vel - conflict_vel)

            # Time to collision
            ttc = (min_separation / relative_velocity 
                  if relative_velocity > 0.1 else float('inf'))

            # Conflict duration
            times = [c[0] for c in conflict_list]
            conflict_duration = max(times) - min(times)

            # Altitude risk factor
            altitude_risk = self._compute_altitude_risk(
                location.z, primary_mission, conflicting_mission
            )

            # Compute overall risk score
            risk_score, severity = self._compute_risk_score(
                min_separation, relative_velocity, conflict_duration,
                altitude_risk, ttc
            )

            # Generate recommendation
            recommendation = self._generate_recommendation(
                severity, ttc, relative_velocity
            )

            conflict = Conflict(
                time=t,
                location=location,
                primary_drone=primary_mission.drone_id,
                conflicting_drone=drone_id,
                separation_distance=min_separation,
                relative_velocity=relative_velocity,
                conflict_duration=conflict_duration,
                altitude_risk_factor=altitude_risk,
                risk_score=risk_score,
                severity=severity,
                time_to_collision=ttc,
                recommendation=recommendation
            )

            assessed_conflicts.append(conflict)

        # Sort by risk score (highest first)
        assessed_conflicts.sort(key=lambda c: c.risk_score, reverse=True)
        return assessed_conflicts

    def _group_conflicts(self, 
                        conflicts: List[Tuple[float, Waypoint, str, float]]
                        ) -> Dict[Tuple[str, int], List[Tuple[float, Waypoint, str, float]]]:
        """Group conflicts by drone and 10-second time windows."""
        groups = {}
        for conflict in conflicts:
            t, location, drone_id, distance = conflict
            time_window = int(t / 10.0)  # 10-second windows
            key = (drone_id, time_window)

            if key not in groups:
                groups[key] = []
            groups[key].append(conflict)

        return groups

    def _compute_altitude_risk(self, conflict_altitude: float,
                               primary: Mission, other: Mission) -> float:
        """
        Compute altitude-based risk factor.
        Vertical conflicts are more dangerous than horizontal.
        """
        # Get average altitude for each mission
        primary_altitudes = [wp.z for wp in primary.waypoints]
        other_altitudes = [wp.z for wp in other.waypoints]

        primary_avg_alt = np.mean(primary_altitudes)
        other_avg_alt = np.mean(other_altitudes)

        vertical_separation = abs(primary_avg_alt - other_avg_alt)

        # Risk multiplier based on vertical separation
        if vertical_separation < 30:
            return 2.0      # Critical - minimal vertical separation
        elif vertical_separation < 50:
            return 1.5      # High risk
        elif vertical_separation < 100:
            return 1.2      # Moderate risk
        else:
            return 1.0      # Low risk - good vertical separation

    def _compute_risk_score(self, 
                           separation: float, 
                           relative_velocity: float,
                           duration: float, 
                           altitude_risk: float, 
                           ttc: float) -> Tuple[float, Severity]:
        """
        Compute overall risk score and severity level.

        Risk Score = f(separation, velocity, duration, altitude)
        Range: 0.0 (safe) to 1.0 (critical)
        """
        # Normalize factors (0 = safe, 1 = critical)
        sep_factor = max(0, 1 - (separation / 100.0))  # Critical below 100m
        vel_factor = min(1.0, relative_velocity / 40.0)  # Critical above 40 m/s
        dur_factor = min(1.0, duration / 30.0)  # Critical if >30 seconds
        ttc_factor = 1.0 if ttc < 5.0 else max(0, 1 - (ttc - 5) / 20.0)

        # Weighted combination
        risk_score = (
            0.40 * sep_factor +
            0.25 * vel_factor +
            0.15 * dur_factor +
            0.20 * ttc_factor
        ) * altitude_risk

        risk_score = min(1.0, risk_score)

        # Determine severity
        if risk_score >= 0.8:
            severity = Severity.CRITICAL
        elif risk_score >= 0.6:
            severity = Severity.HIGH
        elif risk_score >= 0.4:
            severity = Severity.WARNING
        elif risk_score >= 0.2:
            severity = Severity.LOW
        else:
            severity = Severity.SAFE

        return risk_score, severity

    def _generate_recommendation(self, 
                                severity: Severity, 
                                ttc: float,
                                relative_velocity: float) -> str:
        """Generate actionable recommendation based on conflict assessment."""
        if severity == Severity.CRITICAL:
            if ttc < 5.0:
                return (f"REJECT - Imminent collision (TTC={ttc:.1f}s). "
                       f"Head-on conflict requires rerouting.")
            else:
                return ("REJECT - Critical separation violation. "
                       "Mission must be delayed or rerouted.")

        elif severity == Severity.HIGH:
            if relative_velocity > 30:
                return (f"REJECT - High relative velocity ({relative_velocity:.1f}m/s). "
                       f"Recommend 60s delay.")
            else:
                return ("WARN - High risk conflict. "
                       "Suggest altitude adjustment (+50m) or 30s delay.")

        elif severity == Severity.WARNING:
            return "CAUTION - Potential conflict detected. Monitor closely or adjust timing."

        elif severity == Severity.LOW:
            return "ADVISORY - Low risk. Proceed with caution."

        else:
            return "CLEAR - Acceptable separation maintained."
