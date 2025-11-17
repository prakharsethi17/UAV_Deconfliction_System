# UAV Strategic Deconfliction System

A Unmanned Aerial Vehicle (UAV) deconfliction system designed for high-density airspace management. The system efficiently detects and assesses conflicts between a primary drone mission and hundreds of traffic drones using a **3-stage pipeline** with multi-tier filtering, 4D occupancy grid, and risk scoring.

---

## Features

### Core Capabilities
- **3-Stage Deconfliction Pipeline**: Multi-tier filtering (temporal, bounding box, coarse spatial) → 4D occupancy grid → risk scoring
- **Scalable Performance**: Handles 10,000+ drones efficiently (typical reduction: 10,000 → 400 → 50 → 10)
- **Dynamic Safety Buffer**: Physics-based separation distances accounting for velocity, reaction time, acceleration, and GPS uncertainty
- **Risk Assessment**: Quantitative risk scoring (0.0-1.0) with 5 severity levels (SAFE, LOW, WARNING, HIGH, CRITICAL)
- **Mission Pattern Library**: 11+ pre-built traffic patterns + flexible primary mission generators
- **Interactive Visualization**: 3D animated Plotly visualizations with conflict highlighting and trajectory playback
- **Comprehensive Reporting**: JSON exports, textual summaries, and HTML comparison dashboards

### Mission Generation
**Primary Drone Patterns:**
- Straight Line
- Multi-Waypoint
- Grid Survey
- Circular Inspection
- Custom Waypoints
- Random Mission Type

**Traffic Drone Patterns:**
- Flyby, Circular Surveillance, Triangular, Star, Random (Simple)
- Grid Surveillance, Mapping, Figure-8 (Complex)
- Highrise Inspection, Lowrise Inspection, Holding Pattern (Inspection)

---

## Repository Structure

```
uav_deconfliction_system/
│
├── deconfliction/                   # Core deconfliction engine
│   ├── __init__.py
│   ├── models.py                    # Data models (Waypoint, Mission, Conflict, Severity)
│   ├── trajectory.py                # Constant-velocity trajectory interpolation
│   ├── filters.py                   # Stage 1: Multi-tier filtering
│   ├── occupancy_grid.py            # Stage 2: 4D occupancy grid
│   ├── risk_scoring.py              # Stage 3: Risk assessment & prioritization
│   ├── deconfliction_system.py      # Main system integration
│   └── test.py                      # Unit test & example usage
│
├── primary_path_generation/         # Primary mission pattern generators
│   ├── __init__.py
│   ├── base_patterns.py             # Straight line & multi-waypoint
│   ├── survey_patterns.py           # Grid survey & circular inspection
│   ├── generator.py                 # PrimaryDroneGenerator class
│
├── traffic_generation/              # Traffic drone pattern generators
│   ├── __init__.py
│   ├── simple_patterns.py           # Flyby, circular, triangular, star, random
│   ├── complex_patterns.py          # Grid, mapping, figure-8
│   ├── inspection_patterns.py       # Highrise, lowrise, holding patterns
│   ├── generator.py                 # TrafficGenerator class
│
├── visualization/                   # 3D visualization & animation
│   └── visual_enhanced.py           # Plotly-based interactive visualizations
│
├── output/                          # Integration demo outputs & scenario runner
│   ├── __init__.py
│   ├── scenarios.py                 # Pre-configured test scenarios
│   ├── demo_runner.py               # Complete workflow orchestrator
│   └── reporting.py                 # Export utilities (JSON, TXT)
│
├── demo/                            # Generated demo scenario outputs
│   ├── scenario1_random/
│   │   ├── deconfliction_results.json
│   │   ├── primary_mission.json
│   │   ├── traffic_missions.json
│   │   ├── summary_report.txt
│   │   └── scenario1_random_animated.html
│   ├── scenario2_grid/              # (Same structure)
│   ├── scenario3_circular/          # (Same structure)
│   ├── scenario4_straight/          # (Same structure)
│   └── scenario_comparison.html     # Multi-scenario comparison dashboard
│
├── README.md                        # This file
├── requirements.txt                 # Python dependencies
```

---

## 🛠️ Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/uav_deconfliction_system.git
   cd uav_deconfliction_system
   ```

2. **Create a virtual environment (recommended):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

### Dependencies (`requirements.txt`)
```
numpy>=1.21.0
plotly>=5.0.0
kaleido>=0.2.1    # For static image export
```

---

## 🚦 Quick Start

### 1. Run Complete Integration Demo
Execute the full workflow with 4 pre-configured scenarios:

```bash
python -m output.demo_runner
```

**Generates:**
- `./output/scenario1_random/` - Random mission with 75 traffic drones
- `./output/scenario2_grid/` - Grid survey with 80 traffic drones
- `./output/scenario3_circular/` - Circular inspection with 60 traffic drones
- `./output/scenario4_straight/` - Straight line with 50 traffic drones

Each scenario directory contains:
- `primary_mission.json` - Primary drone waypoints & metadata
- `traffic_missions.json` - All traffic drone missions
- `deconfliction_results.json` - Conflicts, metrics, risk scores
- `summary_report.txt` - Human-readable analysis report

---

## System Architecture

### 3-Stage Deconfliction Pipeline

```
┌─────────────────────────────────────────────────────────────────┐
│  INPUT: Primary Mission + 10,000 Traffic Drones                 │
└────────────────────────────┬────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────┐
│  STAGE 1: Multi-Tier Filtering                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ Tier 1: Temporal Filter (Time Window Overlap)           │   │
│  │ 10,000 → 400 drones (95% eliminated)                     │   │
│  └──────────────────┬───────────────────────────────────────┘   │
│  ┌──────────────────▼───────────────────────────────────────┐   │
│  │ Tier 2: Bounding Box Filter (3D Spatial Overlap)        │   │
│  │ 400 → 50 drones (7× reduction)                           │   │
│  └──────────────────┬───────────────────────────────────────┘   │
│  ┌──────────────────▼───────────────────────────────────────┐   │
│  │ Tier 3: Coarse Spatial Filter (10s sampling, 200m buf)  │   │
│  │ 50 → 10 drones (5× reduction)                            │   │
│  └──────────────────────────────────────────────────────────┘   │
└────────────────────────────┬────────────────────────────────────┘
                             │ 10 candidate drones
┌────────────────────────────▼────────────────────────────────────┐
│  STAGE 2: 4D Occupancy Grid                                     │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ Grid: 100×100×100m spatial cells, 1s temporal res       │   │
│  │ Query: 3×3×3 neighborhood check at 1s intervals          │   │
│  │ Output: Raw conflict detections (time, location, dist)   │   │
│  └──────────────────────────────────────────────────────────┘   │
└────────────────────────────┬────────────────────────────────────┘
                             │ Raw conflicts
┌────────────────────────────▼────────────────────────────────────┐
│  STAGE 3: Risk Scoring & Prioritization                         │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ Compute:                                                  │   │
│  │  - Dynamic safety buffer (velocity-dependent)            │   │
│  │  - Relative velocity                                      │   │
│  │  - Time to collision (TTC)                                │   │
│  │  - Conflict duration                                      │   │
│  │  - Altitude risk factor                                   │   │
│  │                                                            │   │
│  │ Risk Score = f(separation, velocity, duration, TTC) ×    │   │
│  │              altitude_risk                                │   │
│  │                                                            │   │
│  │ Severity: CRITICAL | HIGH | WARNING | LOW | SAFE         │   │
│  │ Recommendation: REJECT | DELAY | ADJUST | CLEAR          │   │
│  └──────────────────────────────────────────────────────────┘   │
└────────────────────────────┬────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────┐
│  OUTPUT: Assessed Conflicts + Metrics + Decision (CLEAR/REJECT) │
└─────────────────────────────────────────────────────────────────┘
```

### Data Models

```python
# Waypoint: 3D spatial coordinate
Waypoint(x: float, y: float, z: float)

# Mission: Complete drone flight plan
Mission(
    waypoints: List[Waypoint],
    start_time: float,
    end_time: float,
    drone_id: str,
    cruise_speed: Optional[float]  # Auto-computed if None
)

# Conflict: Detected collision with risk assessment
Conflict(
    time: float,
    location: Waypoint,
    primary_drone: str,
    conflicting_drone: str,
    separation_distance: float,
    relative_velocity: float,
    conflict_duration: float,
    altitude_risk_factor: float,
    risk_score: float,              # 0.0 (safe) to 1.0 (critical)
    severity: Severity,             # CRITICAL|HIGH|WARNING|LOW|SAFE
    time_to_collision: float,
    recommendation: str             # Actionable guidance
)

# Severity: Risk level enumeration
Severity = Enum('Severity', ['SAFE', 'LOW', 'WARNING', 'HIGH', 'CRITICAL'])
```

---

## Pre-Configured Scenarios

The system includes 4 pre-configured test scenarios:

### Scenario 1: Random Mission Type
- **Primary:** Random mission pattern (straight/multi/grid/circular)
- **Traffic:** 75 diverse drones
- **Seed:** 42
- **Output:** `./output/scenario1_random/`

### Scenario 2: Grid Survey Mission
- **Primary:** 6-row grid survey (2000×2000m)
- **Traffic:** 80 diverse drones
- **Seed:** 123
- **Output:** `./output/scenario2_grid/`

### Scenario 3: Circular Inspection
- **Primary:** 16-point circular inspection (600m radius)
- **Traffic:** 60 diverse drones
- **Seed:** 456
- **Output:** `./output/scenario3_circular/`

### Scenario 4: Straight Line
- **Primary:** Diagonal crossing (0,0,100) → (5000,5000,150)
- **Traffic:** 50 diverse drones
- **Seed:** 789
- **Output:** `./output/scenario4_straight/`

---

### Text Report (`summary_report.txt`)

```
================================================================================
UAV STRATEGIC DECONFLICTION SYSTEM - SUMMARY REPORT
================================================================================
Generated: 2025-11-17 10:45:32

PRIMARY MISSION
--------------------------------------------------------------------------------
Drone ID: PRIMARY_DRONE
Waypoints: 5
Time Window: 300.0s - 524.5s
Duration: 224.5s
Total Distance: 2694.3m
Cruise Speed: 12.00 m/s

TRAFFIC ENVIRONMENT
--------------------------------------------------------------------------------
Total Traffic Drones: 75

DECONFLICTION ANALYSIS
--------------------------------------------------------------------------------
Stage 1 (Filtering):   8.21ms
Reduction: 75 → 8
Stage 2 (Grid):   4.56ms
Raw conflicts: 12
Stage 3 (Risk):   2.66ms
Assessed conflicts: 5
Total Analysis Time:  15.43ms

DECISION
--------------------------------------------------------------------------------
STATUS: ✗ MISSION REJECTED - Critical conflicts detected.

CONFLICT SUMMARY
--------------------------------------------------------------------------------
Total Conflicts: 5
 CRITICAL: 1
 HIGH: 2
 WARNING: 2

TOP 5 HIGHEST RISK CONFLICTS
--------------------------------------------------------------------------------
1. [CRITICAL] vs TRAFFIC-023
 Risk: 0.845 | Separation: 35.2m | Time: 345.2s
 Recommendation: REJECT - Imminent collision (TTC=1.8s). Head-on conflict requires rerouting.

2. [HIGH] vs TRAFFIC-045
 Risk: 0.723 | Separation: 42.3m | Time: 378.5s
 Recommendation: WARN - High risk conflict. Suggest altitude adjustment (+50m) or 30s delay.

...

================================================================================
END OF REPORT
================================================================================
```

---

## Visualization

The system includes comprehensive 3D visualization capabilities via Plotly:

### Features
- **Animated 3D Trajectories**: Time-synchronized playback of all drones
- **Color-Coded Drones**: Primary (green), traffic (darker/lighter), conflicts (red/yellow markers)
- **Conflict Highlighting**: Visual markers at collision points with severity indicators
- **Interactive Controls**: Pan, zoom, rotate, timeline scrubbing
- **Multi-View Layouts**: 3D perspective, top-down, side views

### Visualization Files

Each scenario generates:
- `scenario_name_animated.html` - Interactive 3D animation
- `scenario_comparison.html` - Multi-scenario comparison dashboard

Open HTML files in any modern browser (Chrome, Firefox, Safari, Edge).

---

## Testing

### Run Unit Tests

```bash
# Test core deconfliction module
python -m deconfliction.test

# Run integration tests
python -m output.demo_runner
```

### Expected Test Results
- All modules should execute without errors
- Processing times should be <50ms for typical scenarios
- Output files should be generated in `./output/` directories

---