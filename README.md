# Adaptive Wheel Base

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)]()
[![MuJoCo](https://img.shields.io/badge/Physics-MuJoCo-black)]()
[![Status](https://img.shields.io/badge/Status-Prototype-orange)]()

Simulation of a 4-module adaptive robotic platform in **MuJoCo**.

Each module has 3 DoF:

- **lift** - vertical motion
- **steering** - wheel heading
- **wheel rotation** - traction

The repository contains the model, low-level controllers, and standalone simulation scripts for lift, steering, and wheel drive.

---

## Demo

[![Demo video](mujoco/result.png)](test.mp4)

> Click the image to open the simulation video.

---

## Project structure

```text
adaptive-wheel-base/
├── control/
│   ├── linear_actuator.py
│   ├── steering_stepper.py
│   └── wheel_motor.py
├── mujoco/
│   ├── mjcf/
│   │   └── robot.xml
│   └── result.png
├── robot_description/
├── sim/
│   ├── manual_drive_test.py
│   ├── run_lift_actuators.py
│   ├── run_steering_motors.py
│   ├── run_wheel_motors.py
│   └── telemetry.py
├── requirements.txt
└── README.md
```

---

## Model

Main MuJoCo model:

```text
mujoco/mjcf/robot.xml
```

The platform is built from four wheel modules.
Each module includes:

1. a **prismatic joint** for vertical motion
2. a **steering revolute joint**
3. a **wheel revolute joint**

---

## Control models

### 1. Lift actuator

The lift controller is a bounded velocity command to the target height:

```math
u_z =
\begin{cases}
0, & |z_{ref} - z| \le \varepsilon \\
v_{max}, & z_{ref} - z > \varepsilon \\
-v_{max}, & z_{ref} - z < -\varepsilon
\end{cases}
```

where:

* (z) - current lift position
* (z_{ref}) - target lift position
* (v_{max}) - maximum actuator speed
* (\varepsilon) - deadband

Implementation: `control/linear_actuator.py`

---

### 2. Steering controller

The steering loop computes torque from angular error with backlash compensation:

```math
e = \mathrm{wrap}(\delta_{ref} - \delta)
```

```math
e_{eff} =
\begin{cases}
0, & |e| < \Delta_b \\
e - \mathrm{sign}(e)\Delta_b, & |e| \ge \Delta_b
\end{cases}
```

```math
\tau = \mathrm{sat}\left(\eta_g \left(k_p e_{eff} + k_i \int e_{eff}\,dt - k_d \dot{\delta}\right)\right)
```

where:

* (\delta) - current steering angle
* (\delta_{ref}) - target steering angle
* (\Delta_b) - backlash zone
* (\eta_g) - gearbox efficiency
* (\tau) - steering torque

Implementation: `control/steering_stepper.py`

---

### 3. Wheel motor

The wheel motor is modeled as a DC motor:

```math
L \frac{di}{dt} = u - Ri - K_e \omega
```

```math
\tau = K_t i
```

where:

* (u) - motor voltage
* (i) - current
* (\omega) - angular velocity
* (R) - resistance
* (L) - inductance
* (K_e) - back-EMF constant
* (K_t) - torque constant

Implementation: `control/wheel_motor.py`

---

## Simulation scripts

### Lift test

```bash
python3 -m sim.run_lift_actuators
```

### Steering test

```bash
python3 -m sim.run_steering_motors
```

### Wheel drive test

```bash
python3 -m sim.run_wheel_motors
```

---

## Installation

Create environment and install dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

## Telemetry

Wheel drive telemetry includes:

* voltage
* current
* angular velocity
* torque

These signals are buffered and plotted in real time.

Implementation: `sim/telemetry.py`

---

## Engineering notes

* Physics engine: **MuJoCo**
* Main model format: **MJCF**
* Lift control uses **bounded speed tracking**
* Steering is controlled by an external **PID-like torque loop**
* Wheel drive uses an **electromechanical DC motor model**
* Current development focus: steering accuracy, turning behavior, and body leveling under asymmetric load

---

## GitHub cards

### Stats + top languages

<a href="https://github.com/Dcatik">
  <img height="170" align="center" src="https://github-readme-stats.vercel.app/api?username=Dcatik&show_icons=true&theme=tokyonight" />
</a>
<a href="https://github.com/Dcatik?tab=repositories">
  <img height="170" align="center" src="https://github-readme-stats.vercel.app/api/top-langs/?username=Dcatik&layout=compact&theme=tokyonight" />
</a>

### Repository card

<a href="https://github.com/Dcatik/adaptive-wheel-base">
  <img align="center" src="https://github-readme-stats.vercel.app/api/pin/?username=Dcatik&repo=adaptive-wheel-base&theme=tokyonight" />
</a>

---

## Roadmap

* improve steering precision to within a small angular tolerance
* stabilize turning in place
* improve load distribution across lift modules
* finalize body leveling control
* clean up the fourth steering module geometry
* add a more convenient operator interface

---

## License

MIT
