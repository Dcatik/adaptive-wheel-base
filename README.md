# URDF to MuJoCo User Guide

## Goal

Convert a robot model from URDF to MuJoCo MJCF inside a GitHub project, open it in the MuJoCo viewer, and save a final screenshot as `mujoco/result.png`.

---

## Prerequisites

- Ubuntu 24.04
- VS Code
- Git repository already cloned
- Python 3 installed
- A valid URDF file
- STL mesh files for the robot

---

## Step 1. Create `requirements.txt`

Create a file named `requirements.txt` in the project root.

```txt
mujoco
```

---

## Step 2. Create and activate a virtual environment

From the project root:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

## Step 3. Prepare the project structure

Use this structure:

```text
adaptive-wheel-base/
├── robot_description/
│   ├── urdf/
│   │   └── mechatronic_wheel_urdf.urdf
│   └── meshes/
│       ├── Body.STL
│       ├── Wheel_Leg_1.STL
│       ├── Wheel_Arm_1.STL
│       └── ...
├── mujoco/
│   ├── mjcf/
│   │   └── robot.xml
│   └── result.png
├── tools/
│   └── urdf_to_mjcf.py
├── requirements.txt
└── README.md
```

---

## Step 4. Add MuJoCo compiler settings to the URDF

Inside the root `<robot>` tag, add:

```xml
<mujoco>
  <compiler
    meshdir="../meshes"
    discardvisual="false"
    strippath="true"
    fusestatic="false"/>
</mujoco>
```

---

## Step 5. Create the conversion script

Create `tools/urdf_to_mjcf.py`:

```python
from pathlib import Path
import sys
import mujoco

src = Path(sys.argv[1]).resolve()
dst = Path(sys.argv[2]).resolve()

spec = mujoco.MjSpec.from_file(str(src))
spec.compile()

dst.parent.mkdir(parents=True, exist_ok=True)
dst.write_text(spec.to_xml(), encoding="utf-8")

print(f"Saved MJCF to: {dst}")
```

---

## Step 6. Convert URDF to MJCF

From the project root:

```bash
python tools/urdf_to_mjcf.py \
  robot_description/urdf/mechatronic_wheel_urdf.urdf \
  mujoco/mjcf/robot.xml
```

Expected result:

```text
mujoco/mjcf/robot.xml
```

---

## Step 7. Fix `meshdir` in the generated MJCF

Open `mujoco/mjcf/robot.xml`.

If it contains:

```xml
<compiler angle="radian" meshdir="../meshes/"/>
```

and your STL files are in `robot_description/meshes/`, change it to:

```xml
<compiler angle="radian" meshdir="../../robot_description/meshes" discardvisual="false"/>
```

Do not change the individual mesh lines such as:

```xml
<mesh name="Wheel_Leg_1" file="Wheel_Leg_1.STL"/>
```

Keep those unchanged.

---

## Step 8. Open the model in MuJoCo Viewer

Run:

```bash
python -m mujoco.viewer --mjcf=mujoco/mjcf/robot.xml
```

If the model loads, the conversion worked.

---

## Step 9. Troubleshooting

### Case 1. URDF file not found

Check:

```bash
find . -maxdepth 4 \( -name "*.urdf" -o -name "*.xacro" \)
```

Use the real file path in the conversion command.

### Case 2. STL file not found

Check:

```bash
find . -iname "Wheel_Leg_1.STL"
```

Then correct `meshdir` so it points to the actual mesh folder.

### Case 3. Linux filename mismatch

Linux is case-sensitive. These are different:

```text
Wheel_Leg_1.STL
wheel_leg_1.stl
```

Verify exact names:

```bash
find robot_description/meshes -iname "*.stl"
```

---

## Step 10. Save the final image

Once the model is open in MuJoCo Viewer:

1. Position the camera.
2. Take a screenshot manually.
3. Save it as:

```text
mujoco/result.png
```

Final expected result:

```text
adaptive-wheel-base/
├── mujoco/
│   ├── mjcf/
│   │   └── robot.xml
│   └── result.png
```

---

## Result

![MuJoCo result](mujoco/result.png)