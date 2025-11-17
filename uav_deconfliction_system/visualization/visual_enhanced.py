"""
UAV Deconfliction System - Enhanced Interactive Visualization & Animation

===========================================================================

Features:

- Traffic drones as darker spheres, dynamically colored red/yellow on conflict/warning
- Primary drone as green diamond
- Traffic dotted paths
- Primary path dotted/solid dynamic trail
- Hover info with coordinates for primary and traffic drones
- Conflict info box below primary coords with multiple conflict details
- Zoomable 3D space with orbit controls
- Timeline compressed (1 hour -> 1 minute playback)
"""

import json
import os
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import List, Dict, Optional


class UAVVisualizationEnhanced:

    PRIMARY_COLOR = '#28a745'  # Green for primary drone
    TRAFFIC_DEFAULT_COLOR = '#2f4f4f'  # Dark slate gray for traffic drones
    CONFLICT_COLORS = {
        'CRITICAL': '#DC143C',  # Crimson red
        'HIGH': '#FF6347',      # Tomato red
        'WARNING': '#FFD700',   # Gold yellow
        'LOW': '#FFD700'        # Gold as fallback
    }
    DRONE_MARKER_SIZE = 8
    CONFLICT_MARKER_SIZE = 10

    def __init__(self, scenario_dir: str):
        self.scenario_dir = scenario_dir
        self.primary_mission = None
        self.traffic_missions = None
        self.deconfliction_results = None
        self._load_data()

    def _load_data(self):
        with open(os.path.join(self.scenario_dir, 'primary_mission.json'), 'r') as f:
            self.primary_mission = json.load(f)
        with open(os.path.join(self.scenario_dir, 'traffic_missions.json'), 'r') as f:
            self.traffic_missions = json.load(f)
        with open(os.path.join(self.scenario_dir, 'deconfliction_results.json'), 'r') as f:
            self.deconfliction_results = json.load(f)

    def interpolate_position(self, waypoints: List[Dict], cruise_speed: float,
                             start_time: float, query_time: float) -> Optional[np.ndarray]:
        # Return None if query_time is outside the drone's mission time bounds
        if query_time < start_time:
            return None
        end_time = start_time + self._mission_duration(waypoints, cruise_speed)
        if query_time > end_time:
            return None
        if len(waypoints) < 2:
            return None
        positions = np.array([[wp['x'], wp['y'], wp['z']] for wp in waypoints])
        segments = positions[1:] - positions[:-1]
        distances = np.linalg.norm(segments, axis=1)
        times = distances / cruise_speed
        cumulative_times = np.concatenate([[0], np.cumsum(times)])
        elapsed = query_time - start_time
        for i in range(len(cumulative_times) - 1):
            if cumulative_times[i] <= elapsed <= cumulative_times[i + 1]:
                segment_progress = (elapsed - cumulative_times[i]) / (cumulative_times[i + 1] - cumulative_times[i])
                position = positions[i] + segment_progress * (positions[i + 1] - positions[i])
                return position
        return positions[-1]

    def _mission_duration(self, waypoints: List[Dict], cruise_speed: float) -> float:
        if len(waypoints) < 2:
            return 0.0
        positions = np.array([[wp['x'], wp['y'], wp['z']] for wp in waypoints])
        segments = positions[1:] - positions[:-1]
        distances = np.linalg.norm(segments, axis=1)
        total_distance = np.sum(distances)
        if cruise_speed <= 0:
            return 0.0
        return total_distance / cruise_speed

    def create_animated_plot(self, fps: int = 10, duration: Optional[float] = None,
                             traffic_sample_rate: float = 0.3, show_conflict_zones: bool = True,
                             trail_length: int = 100, playback_speed: float = 0.25) -> go.Figure:
        primary_start = self.primary_mission['start_time']
        primary_end = self.primary_mission['end_time']
        if duration is None:
            all_ends = [primary_end] + [m['end_time'] for m in self.traffic_missions['traffic']]
            duration = max(all_ends)
        compressed_duration = 60.0  # 1 min playback for full duration
        time_scale = compressed_duration / duration
        dt = 1.0 / fps
        compressed_times = np.arange(0, compressed_duration, dt)

        def actual_time(t_comp):
            return primary_start + t_comp / time_scale

        traffic_drones = self.traffic_missions['traffic']
        num_to_show = max(1, int(len(traffic_drones) * traffic_sample_rate))
        step = max(1, len(traffic_drones) // num_to_show)
        selected_traffic = traffic_drones[::step]

        fig = go.Figure()

        # Add full dotted paths for traffic drones (static)
        for drone in selected_traffic:
            wp = drone['waypoints']
            wp_x = [point['x'] for point in wp]
            wp_y = [point['y'] for point in wp]
            wp_z = [point['z'] for point in wp]
            fig.add_trace(go.Scatter3d(
                x=wp_x, y=wp_y, z=wp_z,
                mode='lines',
                line=dict(color=self.TRAFFIC_DEFAULT_COLOR, width=3, dash='dot'),
                showlegend=False,
                opacity=0.4,
                hoverinfo='skip'
            ))

        full_trail_times = [actual_time(t) for t in compressed_times]
        full_trail_positions = [
            self.interpolate_position(self.primary_mission['waypoints'], self.primary_mission['cruise_speed'], primary_start, t)
            for t in full_trail_times
        ]

        frames = []
        for frame_idx, t_comp in enumerate(compressed_times):
            t_actual = actual_time(t_comp)
            frame_data = []
            conflicts_at_t = {}
            active_conflicts = []

            if show_conflict_zones and self.deconfliction_results.get('conflicts'):
                for conflict in self.deconfliction_results['conflicts']:
                    if abs(conflict['time'] - t_actual) < 2.0:
                        active_conflicts.append(conflict)
                        drone_id = conflict.get('traffic_drone_id')
                        if drone_id is not None:
                            conflicts_at_t[drone_id] = conflict
                        loc = conflict['location']
                        frame_data.append(go.Scatter3d(
                            x=[loc['x']], y=[loc['y']], z=[loc['z']],
                            mode='markers',
                            marker=dict(
                                size=self.CONFLICT_MARKER_SIZE,
                                color=self.CONFLICT_COLORS.get(conflict['severity'], '#FF0000'),
                                symbol='x',
                                opacity=0.8
                            ),
                            showlegend=False,
                            hovertemplate=(
                                f"{conflict['severity']} CONFLICT<br>Time: {conflict['time']:.1f}s<br>"
                                "X: %{x:.1f}m<br>Y: %{y:.1f}m<br>Z: %{z:.1f}m"
                            )
                        ))

            primary_pos = full_trail_positions[frame_idx]
            if primary_pos is not None:
                frame_data.append(go.Scatter3d(
                    x=[primary_pos[0]], y=[primary_pos[1]], z=[primary_pos[2]],
                    mode='markers',
                    name='Primary Drone',
                    marker=dict(
                        size=self.DRONE_MARKER_SIZE,
                        color=self.PRIMARY_COLOR,
                        symbol='diamond'
                    ),
                    hovertemplate='Primary Drone<br>X: %{x:.1f}m<br>Y: %{y:.1f}m<br>Z: %{z:.1f}m',
                    showlegend=(frame_idx == 0)
                ))

                annotations = [
                    dict(
                        showarrow=False,
                        text=f"Primary Drone<br>X: {primary_pos[0]:.1f} m<br>Y: {primary_pos[1]:.1f} m<br>Z: {primary_pos[2]:.1f} m<br>Time: {t_actual:.1f} s",
                        xref="paper", yref="paper",
                        x=1.05, y=0.75,
                        font=dict(size=12, color=self.PRIMARY_COLOR),
                        align="left",
                        bgcolor="rgba(255, 255, 255, 0.9)",
                        bordercolor=self.PRIMARY_COLOR,
                        borderwidth=2,
                        borderpad=6,
                        opacity=0.95
                    )
                ]
            else:
                # If primary_pos is None, produce minimal annotation or skip
                annotations = [
                    dict(
                        showarrow=False,
                        text=f"Primary Drone position unavailable<br>Time: {t_actual:.1f} s",
                        xref="paper", yref="paper",
                        x=1.05, y=0.75,
                        font=dict(size=12, color='grey'),
                        align="left",
                        bgcolor="rgba(255,255,255,0.7)",
                        bordercolor='grey',
                        borderwidth=2,
                        borderpad=6,
                        opacity=0.8
                    )
                ]

            if primary_pos is not None:
                trail_start_idx = max(0, frame_idx - trail_length)
                past_positions = full_trail_positions[trail_start_idx:frame_idx + 1]
                future_positions = full_trail_positions[frame_idx + 1:frame_idx + 1 + trail_length]

                past_positions = [p for p in past_positions if p is not None]
                future_positions = [p for p in future_positions if p is not None]

                if len(past_positions) >= 2:
                    past_arr = np.array(past_positions)
                    frame_data.append(go.Scatter3d(
                        x=past_arr[:, 0], y=past_arr[:, 1], z=past_arr[:, 2],
                        mode='lines',
                        line=dict(color=self.PRIMARY_COLOR, width=6, dash='solid'),
                        showlegend=False,
                        hoverinfo='skip'
                    ))
                if len(future_positions) >= 2:
                    future_arr = np.array(future_positions)
                    frame_data.append(go.Scatter3d(
                        x=future_arr[:, 0], y=future_arr[:, 1], z=future_arr[:, 2],
                        mode='lines',
                        line=dict(color=self.PRIMARY_COLOR, width=6, dash='dot'),
                        showlegend=False,
                        hoverinfo='skip'
                    ))

            # Add traffic drones at this frame, only if active within mission times
            for drone in selected_traffic:
                # Only show drone if t_actual is within mission start and end times
                if not (drone['start_time'] <= t_actual <= drone['end_time']):
                    continue
                traffic_pos = self.interpolate_position(
                    drone['waypoints'], drone['cruise_speed'], drone['start_time'], t_actual
                )
                if traffic_pos is not None:
                    conflict = conflicts_at_t.get(drone.get('drone_id'))
                    if conflict:
                        severity = conflict['severity']
                        if severity in ['CRITICAL', 'HIGH']:
                            drone_color = self.CONFLICT_COLORS['CRITICAL']
                        elif severity == 'WARNING':
                            drone_color = self.CONFLICT_COLORS['WARNING']
                        else:
                            drone_color = self.TRAFFIC_DEFAULT_COLOR
                    else:
                        drone_color = self.TRAFFIC_DEFAULT_COLOR

                    frame_data.append(go.Scatter3d(
                        x=[traffic_pos[0]], y=[traffic_pos[1]], z=[traffic_pos[2]],
                        mode='markers',
                        marker=dict(
                            size=self.DRONE_MARKER_SIZE,
                            color=drone_color,
                            symbol='circle'
                        ),
                        name=f'Traffic {drone.get("drone_id", "")}',
                        hovertemplate=(
                            f'Traffic Drone {drone.get("drone_id", "")}<br>'
                            f'X: %{{x:.1f}}m<br>Y: %{{y:.1f}}m<br>Z: %{{z:.1f}}m<br>'
                            f'Speed: {drone["cruise_speed"]:.1f} m/s'
                        ),
                        showlegend=False,
                        opacity=0.85
                    ))

            # Conflict annotations
            if active_conflicts:
                conflict_text = f"⚠ CONFLICTS DETECTED: {len(active_conflicts)}<br>"
                for idx, conflict in enumerate(active_conflicts[:3]):
                    conflict_text += (
                        f"Conflict {idx + 1}: {conflict['severity']}<br>"
                        f"Time: {conflict['time']:.1f}s<br>"
                        f"Location: ({conflict['location']['x']:.1f}, {conflict['location']['y']:.1f}, {conflict['location']['z']:.1f})<br>"
                        f"Traffic ID: {conflict.get('traffic_drone_id', 'Unknown')}<br>"
                        f"Risk Score: {conflict.get('risk_score', 0):.2f}<br>"
                        f"Distance: {conflict.get('distance', 0):.1f}m<br><br>"
                    )
                if len(active_conflicts) > 3:
                    conflict_text += f"... and {len(active_conflicts) - 3} more"
                annotations.append(dict(
                    showarrow=False,
                    text=conflict_text,
                    xref="paper", yref="paper",
                    x=1.05, y=0.35,
                    font=dict(size=11, color='#DC143C'),
                    align="left",
                    bgcolor="rgba(255, 240, 240, 0.95)",
                    bordercolor='#DC143C',
                    borderwidth=2,
                    borderpad=6,
                    opacity=0.95
                ))
            else:
                annotations.append(dict(
                    showarrow=False,
                    text="✓ No Conflicts<br>Airspace Clear",
                    xref="paper", yref="paper",
                    x=1.05, y=0.35,
                    font=dict(size=11, color='green'),
                    align="left",
                    bgcolor="rgba(240, 255, 240, 0.9)",
                    bordercolor='green',
                    borderwidth=2,
                    borderpad=6,
                    opacity=0.95
                ))

            frames.append(go.Frame(data=frame_data, name=f't={t_comp:.1f}s', layout=go.Layout(
                title_text=f"Time (compressed): {t_comp:.1f}s | Actual: {t_actual:.1f}s",
                annotations=annotations
            )))

        # Initial plot will use the first frame's data
        if frames:
            fig.add_traces(frames[0].data)

        # Add primary mission waypoints as faint yellow markers+lines for context
        pw = self.primary_mission['waypoints']
        fig.add_trace(go.Scatter3d(
            x=[wp['x'] for wp in pw],
            y=[wp['y'] for wp in pw],
            z=[wp['z'] for wp in pw],
            mode='markers+lines',
            marker=dict(size=self.DRONE_MARKER_SIZE, symbol='diamond', color='yellow', opacity=0.5),
            line=dict(color='yellow', width=2, dash='dot'),
            name='Primary Waypoints',
            showlegend=True,
            hoverinfo='skip'
        ))

        metadata = self.traffic_missions['metadata']
        airspace_x = metadata['airspace_dimensions']['x']
        airspace_y = metadata['airspace_dimensions']['y']
        airspace_z = metadata['airspace_dimensions']['z']

        scenario_name = os.path.basename(self.scenario_dir)
        is_clear = self.deconfliction_results.get('is_clear', False)
        status = "✓ CLEARED" if is_clear else "✗ REJECTED"
        fig.update_layout(
            title=f"{scenario_name.upper()} - {status} - ANIMATED",
            scene=dict(
                xaxis=dict(title='X (m)', range=[0, airspace_x]),
                yaxis=dict(title='Y (m)', range=[0, airspace_y]),
                zaxis=dict(title='Z (m)', range=[0, airspace_z]),
                aspectmode='manual',
                aspectratio=dict(x=1, y=airspace_y / airspace_x, z=airspace_z / airspace_x * 2),
                camera=dict(eye=dict(x=1.5, y=1.5, z=1.2)),
                dragmode='orbit'
            ),
            updatemenus=[{
                'type': 'buttons',
                'showactive': False,
                'y': 1.0,
                'x': 0.0,
                'xanchor': 'left',
                'yanchor': 'top',
                'buttons': [
                    {'label': '▶ Play', 'method': 'animate', 'args': [None, {
                        'frame': {'duration': int(1000 / (fps * playback_speed)), 'redraw': True},
                        'fromcurrent': True,
                        'transition': {'duration': int(500 / (fps * playback_speed))}
                    }]},
                    {'label': '⏸ Pause', 'method': 'animate', 'args': [[None], {
                        'frame': {'duration': 0, 'redraw': False},
                        'mode': 'immediate',
                        'transition': {'duration': 0}
                    }]}
                ]
            }],
            sliders=[{
                'active': 0,
                'steps': [
                    {'args': [[frame.name], {'frame': {'duration': 0, 'redraw': True}, 'mode': 'immediate'}],
                     'label': frame.name, 'method': 'animate'} for frame in frames
                ],
                'transition': {'duration': 0},
                'x': 0.1,
                'y': 0,
                'len': 0.8
            }],
            width=1600,
            height=900,
            annotations=frames[0].layout.annotations if frames else [],
            hovermode='closest'
        )
        fig.frames = frames
        return fig

    def create_static_plots(self) -> List[go.Figure]:
        """Generate static plots: 3D paths of primary and traffic drones."""
        figs = []
        metadata = self.traffic_missions['metadata']
        airspace_x = metadata['airspace_dimensions']['x']
        airspace_y = metadata['airspace_dimensions']['y']
        airspace_z = metadata['airspace_dimensions']['z']

        # Static 3D plot of primary drone path
        fig_primary = go.Figure()
        pw = self.primary_mission['waypoints']
        fig_primary.add_trace(go.Scatter3d(
            x=[wp['x'] for wp in pw],
            y=[wp['y'] for wp in pw],
            z=[wp['z'] for wp in pw],
            mode='lines+markers',
            line=dict(color=self.PRIMARY_COLOR, width=6),
            marker=dict(size=self.DRONE_MARKER_SIZE, symbol='diamond', color=self.PRIMARY_COLOR),
            name='Primary Drone Path',
            hovertemplate='X: %{x:.1f}m<br>Y: %{y:.1f}m<br>Z: %{z:.1f}m'
        ))
        fig_primary.update_layout(
            title='Primary Drone Static Path',
            scene=dict(
                xaxis=dict(range=[0, airspace_x], title='X (m)'),
                yaxis=dict(range=[0, airspace_y], title='Y (m)'),
                zaxis=dict(range=[0, airspace_z], title='Z (m)'),
                aspectmode='manual',
                aspectratio=dict(x=1, y=airspace_y / airspace_x, z=airspace_z / airspace_x * 2),
                dragmode='orbit',
            ),
            width=900,
            height=700,
            hovermode='closest'
        )
        figs.append(fig_primary)

        # Static 3D plot of traffic drone paths
        fig_traffic = go.Figure()
        traffic_list = self.traffic_missions['traffic']
        sample_traffic = traffic_list[::max(1, len(traffic_list) // 10)]
        for drone in sample_traffic:
            wp = drone['waypoints']
            fig_traffic.add_trace(go.Scatter3d(
                x=[w['x'] for w in wp],
                y=[w['y'] for w in wp],
                z=[w['z'] for w in wp],
                mode='lines+markers',
                line=dict(color=self.TRAFFIC_DEFAULT_COLOR, width=3, dash='dot'),
                marker=dict(size=self.DRONE_MARKER_SIZE, symbol='circle', color=self.TRAFFIC_DEFAULT_COLOR),
                name=f'Traffic {drone.get("drone_id", "")}',
                hovertemplate=f'Traffic {drone.get("drone_id", "")}<br>' +
                              'X: %{x:.1f}m<br>Y: %{y:.1f}m<br>Z: %{z:.1f}m'
            ))
        fig_traffic.update_layout(
            title='Traffic Drones Static Paths',
            scene=dict(
                xaxis=dict(range=[0, airspace_x], title='X (m)'),
                yaxis=dict(range=[0, airspace_y], title='Y (m)'),
                zaxis=dict(range=[0, airspace_z], title='Z (m)'),
                aspectmode='manual',
                aspectratio=dict(x=1, y=airspace_y / airspace_x, z=airspace_z / airspace_x * 2),
                dragmode='orbit'
            ),
            width=900,
            height=700,
            hovermode='closest'
        )
        figs.append(fig_traffic)
        return figs

    def export_animation_html(self, output_file: str, **kwargs):
        fig = self.create_animated_plot(**kwargs)
        fig.write_html(output_file)
        print(f"✓ Exported animation to HTML: {output_file}")

    def export_static_plots_html(self, base_output_path: str):
        figs = self.create_static_plots()
        for idx, fig in enumerate(figs):
            filename = os.path.join(base_output_path, f'static_plot_{idx + 1}.html')
            fig.write_html(filename)
            print(f"✓ Exported static plot to HTML: {filename}")


def create_comparison_videos(output_base_dir: str = "./uav_deconfliction_system/output"):
    print("\n" + "=" * 80)
    print("CREATING SCENARIO COMPARISON VISUALIZATIONS")
    print("=" * 80)

    scenarios = [
        'scenario1_random',
        'scenario2_grid',
        'scenario3_circular',
        'scenario4_straight'
    ]

    conflict_free = []
    conflicted = []

    for scenario in scenarios:
        scenario_dir = os.path.join(output_base_dir, scenario)
        if not os.path.exists(scenario_dir):
            continue
        viz = UAVVisualizationEnhanced(scenario_dir)
        if viz.deconfliction_results.get('is_clear', False):
            conflict_free.append((scenario, viz))
        else:
            conflicted.append((scenario, viz))

    if len(conflict_free) > 0 and len(conflicted) > 0:
        print(f"\nFound {len(conflict_free)} conflict-free and {len(conflicted)} conflicted scenarios")
        print("Creating comparison dashboard...")

        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=[
                f"{conflict_free[0][0]} - CLEAR",
                f"{conflicted[0][0]} - CONFLICT",
                "Conflict Zones (3D)",
                "Risk Distribution"
            ],
            specs=[
                [{'type': 'scatter3d'}, {'type': 'scatter3d'}],
                [{'type': 'scatter3d'}, {'type': 'bar'}]
            ],
            vertical_spacing=0.1,
            horizontal_spacing=0.05
        )

        # Clear scenario plot
        scenario_name, viz = conflict_free[0]
        primary = viz.primary_mission['waypoints']
        px = [wp['x'] for wp in primary]
        py = [wp['y'] for wp in primary]
        pz = [wp['z'] for wp in primary]
        fig.add_trace(go.Scatter3d(
            x=px, y=py, z=pz,
            mode='lines+markers',
            line=dict(color='green', width=6),
            marker=dict(size=5),
            name='Clear Path'
        ), row=1, col=1)

        # Conflict scenario plot
        scenario_name, viz = conflicted[0]
        primary = viz.primary_mission['waypoints']
        px = [wp['x'] for wp in primary]
        py = [wp['y'] for wp in primary]
        pz = [wp['z'] for wp in primary]
        fig.add_trace(go.Scatter3d(
            x=px, y=py, z=pz,
            mode='lines+markers',
            line=dict(color='red', width=6),
            marker=dict(size=5),
            name='Conflict Path'
        ), row=1, col=2)

        conflicts = viz.deconfliction_results.get('conflicts', [])
        if conflicts:
            cx = [c['location']['x'] for c in conflicts]
            cy = [c['location']['y'] for c in conflicts]
            cz = [c['location']['z'] for c in conflicts]
            fig.add_trace(go.Scatter3d(
                x=cx, y=cy, z=cz,
                mode='markers',
                marker=dict(size=12, color='red', symbol='x'),
                name='Conflicts'
            ), row=1, col=2)

        # Risk zones (scatter3d color-sized)
        if conflicts:
            cx = [c['location']['x'] for c in conflicts]
            cy = [c['location']['y'] for c in conflicts]
            cz = [c['location']['z'] for c in conflicts]
            sizes = [c.get('risk_score', 0)*30 + 5 for c in conflicts]
            fig.add_trace(go.Scatter3d(
                x=cx, y=cy, z=cz,
                mode='markers',
                marker=dict(
                    size=sizes,
                    color=[c.get('risk_score', 0) for c in conflicts],
                    colorscale='Reds',
                    showscale=True
                ),
                name='Risk Zones'
            ), row=2, col=1)

        # Severity distribution bar
        if conflicts:
            severity_counts = {'CRITICAL': 0, 'HIGH': 0, 'WARNING': 0, 'LOW': 0}
            for c in conflicts:
                sev = c.get('severity', '')
                if sev in severity_counts:
                    severity_counts[sev] += 1
            fig.add_trace(go.Bar(
                x=list(severity_counts.keys()),
                y=list(severity_counts.values()),
                marker=dict(color=['#DC143C', '#FF6347', '#FFA500', '#FFD700']),
                name='Severity Distribution'
            ), row=2, col=2)

        fig.update_layout(
            title_text="Conflict-Free vs Conflicted Scenario Comparison",
            height=1200,
            width=1600,
            showlegend=True
        )
        comparison_file = os.path.join(output_base_dir, 'scenario_comparison.html')
        fig.write_html(comparison_file)
        print(f"✓ Saved comparison: {comparison_file}")


def visualize_all_enhanced(output_base_dir: str = "./uav_deconfliction_system/output",
                          export_animations: bool = True,
                          export_4d: bool = False):
    print("\n" + "=" * 80)
    print("ENHANCED UAV VISUALIZATION - GENERATING ANIMATIONS AND STATIC PLOTS")
    print("=" * 80)

    scenarios = [
        'scenario1_random',
        'scenario2_grid',
        'scenario3_circular',
        'scenario4_straight'
    ]

    for scenario in scenarios:
        scenario_dir = os.path.join(output_base_dir, scenario)
        if not os.path.exists(scenario_dir):
            print(f"⚠ Skipping {scenario} - directory not found")
            continue
        print(f"\n{'─' * 80}")
        print(f"Processing: {scenario}")
        print(f"{'─' * 80}")
        viz = UAVVisualizationEnhanced(scenario_dir)
        base_output_path = scenario_dir
        if export_animations:
            animation_file = os.path.join(base_output_path, f'{scenario}_animated.html')
            viz.export_animation_html(animation_file, fps=10, playback_speed=0.25, traffic_sample_rate=0.3)
        viz.export_static_plots_html(base_output_path)

    create_comparison_videos(output_base_dir)

    print("\n" + "=" * 80)
    print("ENHANCED VISUALIZATION COMPLETE")
    print("=" * 80)
    print("\nGenerated files:")
    print(" - *_animated.html : Time-slider animated simulations")
    print(" - static_plot_*.html : Static 3D plots for primary and traffic")
    print(" - scenario_comparison.html : Side-by-side comparison")
    print("=" * 80)


def main():
    print("""
╔════════════════════════════════════════════════════════════════════════════╗
║                                                                            ║
║ UAV DECONFLICTION - ENHANCED VISUALIZATION & ANIMATION                     ║
║                                                                            ║
║ Features:                                                                   ║
║ • Traffic drones as spheres with hover coordinates                          ║
║ • Primary drone as diamond (same size)                                     ║
║ • Traffic dotted paths                                                      ║
║ • Primary path dotted/solid dynamic                                         ║
║ • Dynamic coordinate display with conflict info                            ║
║ • Zoomable and interactive 3D space                                        ║
║ • Timeline compression (1 hour to 1 min)                                  ║
║ • Interactive HTML + MP4 export ready                                      ║
║                                                                            ║
╚════════════════════════════════════════════════════════════════════════════╝
""")
    visualize_all_enhanced(
        output_base_dir="./uav_deconfliction_system/output",
        export_animations=True,
        export_4d=False
    )
    print("\n" + "=" * 80)
    print("ALL ENHANCED VISUALIZATIONS COMPLETE")
    print("=" * 80)
    print("\nYou can now:")
    print(" 1. Open *_animated.html for time-based playback")
    print(" 2. Open static_plot_*.html for static 3D visualizations")
    print(" 3. Open scenario_comparison.html for side-by-side analysis")
    print(" 4. Use Play/Pause buttons and time slider for control")
    print(" 5. Zoom, rotate, and hover over elements in 3D space")
    print("=" * 80)


if __name__ == "__main__":
    main()
