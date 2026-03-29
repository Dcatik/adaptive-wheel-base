import time
from pathlib import Path

import mujoco
import mujoco.viewer

from control.linear_actuator import LinearActuator


MODEL_PATH = Path(__file__).resolve().parents[1] / "mujoco" / "mjcf" / "robot.xml"

ACTUATOR_NAMES = [
    "lift_1",
    "lift_2",
    "lift_3",
    "lift_4",
]

JOINT_NAMES = [
    "Prismatic_Joint_1",
    "Prismatic_Joint_2",
    "Prismatic_Joint_3",
    "Prismatic_Joint_4",
]


def require_id(model, obj_type, name):
    obj_id = mujoco.mj_name2id(model, obj_type, name)
    if obj_id == -1:
        raise ValueError(f"MuJoCo object not found: {name}")
    return obj_id


def main():
    model = mujoco.MjModel.from_xml_path(str(MODEL_PATH))
    data = mujoco.MjData(model)
    mujoco.mj_forward(model, data)

    dt = model.opt.timestep

    actuator_ids = [
        require_id(model, mujoco.mjtObj.mjOBJ_ACTUATOR, name)
        for name in ACTUATOR_NAMES
    ]
    joint_ids = [
        require_id(model, mujoco.mjtObj.mjOBJ_JOINT, name)
        for name in JOINT_NAMES
    ]
    qpos_addrs = [model.jnt_qposadr[jid] for jid in joint_ids]

    lifts = [LinearActuator(z_min=0.0, z_max=0.1, max_speed=0.05) for _ in range(4)]

    for i, lift in enumerate(lifts):
        z0 = float(data.qpos[qpos_addrs[i]])
        lift.reset(z0)

    target_z = 0.05
    for lift in lifts:
        lift.set_reference(target_z)

    last_print_time = 0.0
    print_period = 0.2

    last_time = float(data.time)

    with mujoco.viewer.launch_passive(model, data) as viewer:
        while viewer.is_running():
            step_start = time.perf_counter()

            with viewer.lock():
                # detect viewer reset
                if data.time < last_time:
                    for i, lift in enumerate(lifts):
                        z0 = float(data.qpos[qpos_addrs[i]])
                        lift.reset(z0)
                        lift.set_reference(target_z)
                        data.ctrl[actuator_ids[i]] = z0

                    mujoco.mj_forward(model, data)

                last_time = float(data.time)

                for i, lift in enumerate(lifts):
                    z = float(data.qpos[qpos_addrs[i]])
                    data.ctrl[actuator_ids[i]] = lift.step(z)

                mujoco.mj_step(model, data)

            viewer.sync()

            remaining = dt - (time.perf_counter() - step_start)
            if remaining > 0.0:
                time.sleep(remaining)


if __name__ == "__main__":
    main()