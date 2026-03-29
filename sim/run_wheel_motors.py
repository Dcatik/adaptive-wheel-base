import time
from pathlib import Path

import mujoco
import mujoco.viewer

from control.wheel_motor import WheelMotor
from sim.telemetry import WheelSample, WheelTelemetryBuffer, RealtimePlotter


MODEL_PATH = Path(__file__).resolve().parents[1] / "mujoco" / "mjcf" / "robot.xml"


def require_id(model, obj_type, name: str) -> int:
    # Look up a MuJoCo object by name.
    obj_id = mujoco.mj_name2id(model, obj_type, name)

    if obj_id == -1:
        raise ValueError(f"MuJoCo object not found: {name}")

    return obj_id


def main() -> None:
    # Load model and simulation data.
    model = mujoco.MjModel.from_xml_path(str(MODEL_PATH))
    data = mujoco.MjData(model)
    dt = model.opt.timestep

    # Four identical wheel motor models.
    motors = [
        WheelMotor(R=0.35, L=0.002, Ke=0.428, Kt=0.428, current_limit=10.0)
        for _ in range(4)
    ]

    buffers = [WheelTelemetryBuffer(maxlen=2000) for _ in range(4)]
    plotter = RealtimePlotter(wheel_count=4)

    actuator_names = [
        "wheel_motor_1",
        "wheel_motor_2",
        "wheel_motor_3",
        "wheel_motor_4",
    ]

    joint_names = [
        "Rotating_Joint_1",
        "Rotating_Joint_2",
        "Rotating_Joint_3",
        "Rotating_Joint_4",
    ]

    # Constant voltage commands for all wheels.
    voltage_cmds = [36.0, 36.0, 36.0, 36.0]

    actuator_ids = [
        require_id(model, mujoco.mjtObj.mjOBJ_ACTUATOR, name)
        for name in actuator_names
    ]

    joint_ids = [
        require_id(model, mujoco.mjtObj.mjOBJ_JOINT, name)
        for name in joint_names
    ]

    # Address of each wheel angular velocity in data.qvel.
    dof_addrs = [model.jnt_dofadr[joint_id] for joint_id in joint_ids]

    data.ctrl[:] = 0.0

    step_counter = 0
    # Run passive viewer loop.
    with mujoco.viewer.launch_passive(model, data) as viewer:
        while viewer.is_running():
            step_start = time.time()

            # Update each wheel independently.
            for k in range(4):
                omega = data.qvel[dof_addrs[k]]

                tau = motors[k].step(
                    voltage=voltage_cmds[k],
                    omega=omega,
                    dt=dt,
                )

                buffers[k].append(
                    WheelSample(
                        t=data.time,
                        voltage=voltage_cmds[k],
                        current=motors[k].i,
                        omega=omega,
                        torque=tau,
                    )
                )

                # Clamp torque to actuator control range.
                ctrl_min = float(model.actuator_ctrlrange[actuator_ids[k], 0])
                ctrl_max = float(model.actuator_ctrlrange[actuator_ids[k], 1])
                tau = max(ctrl_min, min(ctrl_max, tau))

                data.ctrl[actuator_ids[k]] = tau

            mujoco.mj_step(model, data)
            step_counter += 1
            if step_counter % 5 == 0:
                plotter.update(buffers)
            viewer.sync()

            remaining = dt - (time.time() - step_start)
            if remaining > 0:
                time.sleep(remaining)


if __name__ == "__main__":
    main()