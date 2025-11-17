"""
Stage 1: Multi-Tier Filtering System.

Progressively eliminates irrelevant drones: 10,000 → 400 → 50 → 10

Three-tier approach:
1. Temporal Filter: Remove non-overlapping time windows
2. Bounding Box Filter: Remove non-intersecting spatial volumes
3. Coarse Spatial Filter: Sample-based proximity check
"""

import numpy as np
from typing import List
from .models import Mission
from .trajectory import ConstantVelocityTrajectory


class Stage1MultiTierFilter:
    """Multi-tier filtering for rapid drone elimination."""

    def __init__(self, time_margin: float = 30.0, spatial_margin: float = 500.0):
        """
        Initialize filter with safety margins.

        Args:
            time_margin: Extra time buffer (seconds)
            spatial_margin: Extra space buffer (meters)
        """
        self.time_margin = time_margin
        self.spatial_margin = spatial_margin
        self.stats = {
            'initial': 0, 
            'after_temporal': 0, 
            'after_bbox': 0, 
            'after_coarse': 0
        }

    def filter(self, primary_mission: Mission, 
               all_missions: List[Mission]) -> List[Mission]:
        """
        Execute 3-tier filtering pipeline.

        Args:
            primary_mission: Mission to check
            all_missions: All registered missions in airspace

        Returns:
            Filtered list of candidate missions that might conflict
        """
        self.stats['initial'] = len(all_missions)

        # Tier 1: Temporal Filter
        temporal_candidates = self._temporal_filter(primary_mission, all_missions)
        self.stats['after_temporal'] = len(temporal_candidates)

        # Tier 2: Bounding Box Filter
        bbox_candidates = self._bounding_box_filter(primary_mission, temporal_candidates)
        self.stats['after_bbox'] = len(bbox_candidates)

        # Tier 3: Coarse Spatial Filter
        final_candidates = self._coarse_spatial_filter(primary_mission, bbox_candidates)
        self.stats['after_coarse'] = len(final_candidates)

        return final_candidates

    def _temporal_filter(self, primary: Mission, 
                        missions: List[Mission]) -> List[Mission]:
        """
        Tier 1: Eliminate drones with non-overlapping time windows.
        Expected reduction: 10,000 → 400 (95%)
        """
        primary_start = primary.start_time - self.time_margin
        primary_end = primary.end_time + self.time_margin

        candidates = []
        for mission in missions:
            # Check time window overlap
            if not (mission.end_time < primary_start or 
                    mission.start_time > primary_end):
                candidates.append(mission)

        return candidates

    def _bounding_box_filter(self, primary: Mission, 
                            missions: List[Mission]) -> List[Mission]:
        """
        Tier 2: Eliminate drones with non-intersecting bounding boxes.
        Expected reduction: 400 → 50 (7×)
        """
        primary_min, primary_max = primary.get_bounding_box()
        primary_min = primary_min - self.spatial_margin
        primary_max = primary_max + self.spatial_margin

        candidates = []
        for mission in missions:
            mission_min, mission_max = mission.get_bounding_box()

            if self._boxes_intersect(primary_min, primary_max, 
                                    mission_min, mission_max):
                candidates.append(mission)

        return candidates

    def _boxes_intersect(self, min1: np.ndarray, max1: np.ndarray,
                        min2: np.ndarray, max2: np.ndarray) -> bool:
        """Check if two 3D bounding boxes intersect."""
        return np.all(min1 <= max2) and np.all(min2 <= max1)

    def _coarse_spatial_filter(self, primary: Mission, 
                              missions: List[Mission]) -> List[Mission]:
        """
        Tier 3: Coarse spatial check with 10-second time steps.
        Expected reduction: 50 → 10 (5×)
        """
        primary_traj = ConstantVelocityTrajectory(primary)
        time_step = 10.0        # Coarse sampling interval
        coarse_buffer = 200.0   # Generous buffer for coarse check

        candidates = []
        for mission in missions:
            mission_traj = ConstantVelocityTrajectory(mission)

            # Sample at coarse intervals
            t_start = max(primary.start_time, mission.start_time)
            t_end = min(primary.end_time, mission.end_time)

            if t_start >= t_end:
                continue

            times = np.arange(t_start, t_end, time_step)
            is_candidate = False

            for t in times:
                p1 = primary_traj.get_position(t)
                p2 = mission_traj.get_position(t)

                if p1 and p2:
                    distance = p1.distance_to(p2)
                    if distance < coarse_buffer:
                        is_candidate = True
                        break

            if is_candidate:
                candidates.append(mission)

        return candidates

    def get_filtering_report(self) -> str:
        """Generate filtering statistics report."""
        report = "\n" + "="*70 + "\n"
        report += "STAGE 1: Multi-Tier Filtering Results\n"
        report += "="*70 + "\n"
        report += f"Initial drones: {self.stats['initial']:6d}\n"

        if self.stats['initial'] > 0:
            temporal_reduction = (1 - self.stats['after_temporal'] / 
                                self.stats['initial']) * 100
            report += (f"After Temporal Filter: {self.stats['after_temporal']:6d} "
                      f"({temporal_reduction:.1f}% eliminated)\n")

        if self.stats['after_temporal'] > 0:
            bbox_factor = self.stats['after_temporal'] / max(1, self.stats['after_bbox'])
            report += (f"After Bounding Box: {self.stats['after_bbox']:6d} "
                      f"({bbox_factor:.1f}× reduction)\n")

        if self.stats['after_bbox'] > 0:
            coarse_factor = self.stats['after_bbox'] / max(1, self.stats['after_coarse'])
            report += (f"After Coarse Spatial: {self.stats['after_coarse']:6d} "
                      f"({coarse_factor:.1f}× reduction)\n")

        report += "="*70 + "\n"
        return report
