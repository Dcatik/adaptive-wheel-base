# 4W3DOF Mobile Robotic Platform

> Four-wheel mobile robotic platform with active wheel modules: drive, steering, and vertical wheel positioning for terrain adaptation and body stabilization.

## Overview

This repository contains the design and development of a **4-wheel robotic platform** in which each wheel is implemented as an **independent 3-DOF module**.  
Each wheel module provides:

- **wheel rotation** for traction and motion
- **wheel steering** for directional control
- **wheel height adjustment** for active suspension and terrain adaptation

As a result, the platform combines properties of:

- classical wheeled robots
- swerve-drive systems
- active suspension platforms

The main idea of the project is to create a **modular terrain-adaptive robotic base** that can maintain mobility, stability, and controllability on uneven surfaces while staying mechanically simpler and potentially cheaper than full legged systems.

---

## Why this project

Conventional wheeled robots are efficient and mechanically simple, but they have limited adaptability to complex terrain.  
Legged robots handle terrain better, but they are much more expensive, mechanically complex, and difficult to develop.

This project explores a **middle ground**:

- better terrain handling than a regular wheeled chassis
- better controllability than passive suspension
- lower complexity than a full quadruped or humanoid locomotion system

The platform is intended as a base for:

- autonomous mobile robots
- rough-terrain delivery robots
- inspection robots
- research in locomotion and mobile manipulation
- experiments in active suspension and body stabilization

---

## Platform concept

The robot uses **4 independent wheel modules**.  
Each module has 3 controlled degrees of freedom:

### 1. Drive
Wheel spinning generates longitudinal traction and allows the robot to move.

### 2. Steering
The wheel can rotate around a vertical axis, allowing the platform to:
- turn with reduced slip
- implement omnidirectional or near-omnidirectional motion strategies
- improve maneuverability in tight spaces

### 3. Vertical wheel positioning
The wheel module can move vertically relative to the chassis.  
This is the key feature of the platform. It enables:

- adaptation to uneven ground
- chassis leveling
- pitch/roll compensation
- improved wheel-ground contact
- obstacle traversal strategies

In practice, this means the robot can actively change its geometry instead of relying only on passive compliance.

---

## Main engineering goals

The project is focused on the following technical goals:

- design of a **rigid modular chassis**
- implementation of **independent wheel modules**
- development of a **controllable active suspension architecture**
- future conversion from CAD model to **simulation model**
- study of **kinematics, dynamics, and control**
- validation of the concept in both simulation and physical prototype form

---

## Key features

- **4-wheel architecture**
- **3 DOF per wheel**
- modular wheel assemblies
- active body leveling capability
- potential support for multiple motion modes
- scalable mechanical concept for research and prototyping
- suitable as a base for ROS2 / simulation / control experiments

---

## Degrees of freedom

For the full platform:

- 4 wheel drive DOF
- 4 wheel steering DOF
- 4 wheel vertical DOF

Total controlled wheel DOF:

\[
4 \times 3 = 12
\]

This makes the platform strongly overactuated compared to standard mobile robots.  
That is both the main challenge and the main advantage of the project.

### Implications of this architecture

**Advantages**
- high adaptability
- improved terrain compliance
- better control of body attitude
- redundancy for optimization-based control

**Challenges**
- mechanical complexity
- actuator packaging
- wiring and power distribution
- control coordination between modules
- higher mass and cost compared to simpler chassis

---

## Expected control tasks

This platform is intended for future implementation of several control layers:

### Low-level control
- wheel velocity control
- steering angle control
- vertical actuator position / force control

### Mid-level control
- chassis height control
- roll and pitch stabilization
- traction management
- wheel-ground contact maintenance

### High-level control
- path tracking
- terrain-adaptive motion planning
- obstacle crossing strategies
- optimization of wheel module configuration

---

## Mechanical status

At the current stage, the project includes a CAD-based mechanical platform concept with:

- rectangular chassis body
- internal structural frame
- four corner wheel modules
- enclosed body layout
- modular integration space for electronics, battery, sensors, and compute

The design direction prioritizes:

- manufacturability
- structural clarity
- modularity
- future access for prototyping and maintenance

---

## Planned software and simulation pipeline

The long-term development path of the project is:

1. **CAD development in SolidWorks**
2. export of assembly structure to robot description format
3. creation of a **URDF / MJCF / simulation model**
4. integration with **ROS2**
5. implementation of control architecture
6. simulation on flat and uneven terrain
7. development of physical prototype

Possible simulation environments:

- Gazebo
- MuJoCo
- Isaac Sim
- custom dynamics environment

---

## Possible applications

This platform can be adapted for several use cases:

- indoor/outdoor autonomous mobile robot
- warehouse robot for non-ideal floors
- inspection robot for industrial facilities
- research platform for active suspension
- robotic base for modular payloads
- educational and academic mechatronics platform

---

## Repository goals

This repository is not only a storage place for CAD files.  
The goal is to turn it into a full engineering project containing:

- mechanical design
- actuator architecture
- control logic
- simulation models
- documentation
- prototype iteration history

In other words, this repository should evolve into a **complete development log of a terrain-adaptive mobile robotic platform**.

---

## Roadmap

### Phase 1 — Mechanical concept
- [x] Initial chassis layout
- [x] 4 wheel module architecture
- [x] body enclosure concept
- [ ] actuator selection
- [ ] bearing and transmission validation
- [ ] mass estimation

### Phase 2 — Modeling
- [ ] define kinematic structure
- [ ] derive system constraints
- [ ] export CAD to simulation-ready model
- [ ] prepare simplified dynamic model

### Phase 3 — Control
- [ ] wheel drive control
- [ ] steering control
- [ ] active height control
- [ ] body leveling controller
- [ ] terrain adaptation logic

### Phase 4 — Prototype
- [ ] manufacturing-ready redesign
- [ ] electronics integration
- [ ] power system selection
- [ ] embedded control implementation
- [ ] field testing

---

## Repository structure

Suggested project structure:

```text
.
├── cad/                # SolidWorks assemblies, parts, exports
├── docs/               # Design notes, схемы, изображения, расчёты
├── simulation/         # URDF, MJCF, Gazebo/MuJoCo models
├── control/            # Controllers and robotics software
├── electronics/        # Wiring, power, motor drivers, BOM
├── media/              # Renders, screenshots, videos
└── README.md
