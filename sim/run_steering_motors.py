import math
import time
from pathlib import Path

import mujoco
import mujoco.viewer

from control.steering_stepper import SteeringStepper


MODEL_PATH = Path(__file__).resolve().parents[1] / "mujoco" / "mjcf" / "robot.xml"


def require_id(model, obj_type, name: str) -> int:
    obj_id = mujoco.mj_name2id(model, obj_type, name)
    if obj_id == -1:
        raise ValueError(f"MuJoCo object not found: {name}")
    return obj_id


def clip(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def angle_error(target: float, current: float) -> float:
    return math.atan2(math.sin(target - current), math.cos(target - current))


def main() -> None:
    # Load model and simulation data.
    model = mujoco.MjModel.from_xml_path(str(MODEL_PATH))
    data = mujoco.MjData(model)
    dt = model.opt.timestep

    steppers = [SteeringStepper() for _ in range(4)]

    actuator_names = [
        "steering_motor_1",
        "steering_motor_2",
        "steering_motor_3",
        "steering_motor_4",
    ]

    joint_names = [
        "Steering_Joint_1",
        "Steering_Joint_2",
        "Steering_Joint_3",
        "Steering_Joint_4",
    ]

    actuator_ids = [
        require_id(model, mujoco.mjtObj.mjOBJ_ACTUATOR, name)
        for name in actuator_names
    ]
    joint_ids = [
        require_id(model, mujoco.mjtObj.mjOBJ_JOINT, name)
        for name in joint_names
    ]

    qpos_addrs = [model.jnt_qposadr[joint_id] for joint_id in joint_ids]
    dof_addrs = [model.jnt_dofadr[joint_id] for joint_id in joint_ids]

    max_target = math.radians(45.0)
    zero_target = 0.0

    switch_threshold = math.radians(2.0)


    velocity_threshold = math.radians(2.0)


    outer_targets = [-max_target, max_target, max_target, -max_target]

    use_outer_phase = False

    # Start from zero.
    target_angles = [zero_target, zero_target, zero_target, zero_target]

    for k in range(4):
        steppers[k].reset()
        steppers[k].set_reference(target_angles[k])

    data.ctrl[:] = 0.0

    # Run passive viewer loop.
    with mujoco.viewer.launch_passive(model, data) as viewer:
        while viewer.is_running():
            step_start = time.time()


            deltas = [data.qpos[qpos_addrs[k]] for k in range(4)]
            delta_dots = [data.qvel[dof_addrs[k]] for k in range(4)]


            all_reached = True
            for k in range(4):
                err = angle_error(target_angles[k], deltas[k])
                if abs(err) > switch_threshold or abs(delta_dots[k]) > velocity_threshold:
                    all_reached = False
                    break

            if all_reached:
                use_outer_phase = not use_outer_phase

                for k in range(4):
                    target_angles[k] = outer_targets[k] if use_outer_phase else zero_target
                    steppers[k].set_reference(target_angles[k])

            # Compute torques and apply them to the actuators.
            for k in range(4):
                tau = steppers[k].compute_torque(
                    delta=deltas[k],
                    delta_dot=delta_dots[k],
                    dt=dt,
                )

                ctrl_min = float(model.actuator_ctrlrange[actuator_ids[k], 0])
                ctrl_max = float(model.actuator_ctrlrange[actuator_ids[k], 1])
                data.ctrl[actuator_ids[k]] = clip(tau, ctrl_min, ctrl_max)

            mujoco.mj_step(model, data)
            viewer.sync()

            remaining = dt - (time.time() - step_start)
            if remaining > 0:
                time.sleep(remaining)


if __name__ == "__main__":
    main()