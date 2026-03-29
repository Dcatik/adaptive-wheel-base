import math
import time
from pathlib import Path

import mujoco
import mujoco.viewer

from control.linear_actuator import LinearActuator
from control.steering_stepper import SteeringStepper


MODEL_PATH = Path(__file__).resolve().parents[1] / "mujoco" / "mjcf" / "robot.xml"

N = 4
BODY_NAME = "Body"
LEG_NAMES = [f"Wheel_Leg_{i}" for i in range(1, N + 1)]

TURN_ANGLE = math.radians(45.0)
LIFT_MIN = 0.0
LIFT_MAX = 0.1
LIFT_LOW = 0.0
LIFT_HIGH = 0.1

STEERING_POS_TOL = math.radians(5.0)
STEERING_VEL_TOL = math.radians(5.0)

WHEEL_SIGNS = [1.0, 1.0, -1.0, -1.0]

TURN_SIGNS = [1.0, 1.0, 1.0, 1.0]


def require_id(model, obj_type, name: str) -> int:
    obj_id = mujoco.mj_name2id(model, obj_type, name)
    if obj_id == -1:
        raise ValueError(f"MuJoCo object not found: {name}")
    return obj_id


def get_ids(model, obj_type, pattern: str) -> list[int]:
    return [require_id(model, obj_type, pattern.format(i)) for i in range(1, N + 1)]


def clip(x: float, low: float, high: float) -> float:
    return max(low, min(high, x))


def angle_error(target: float, current: float) -> float:
    return math.atan2(math.sin(target - current), math.cos(target - current))


def body_roll_pitch(data: mujoco.MjData, body_id: int) -> tuple[float, float]:
    R = data.xmat[body_id].reshape(3, 3)
    pitch = math.asin(-clip(R[2, 0], -1.0, 1.0))
    roll = math.atan2(R[2, 1], R[2, 2])
    return roll, pitch


class LevelController:

    def __init__(self, leg_xy: list[tuple[float, float]], z_min=LIFT_MIN, z_max=LIFT_MAX):
        self.leg_xy = leg_xy
        self.z_min = float(z_min)
        self.z_max = float(z_max)

        self.kp_roll = 10.0
        self.ki_roll = 0.25
        self.kd_roll = 0.10

        self.kp_pitch = 10.0
        self.ki_pitch = 0.25
        self.kd_pitch = 0.10

        self.i_roll = 0.0
        self.i_pitch = 0.0
        self.i_limit = 0.35

        self.prev_roll = 0.0
        self.prev_pitch = 0.0
        self.initialized = False

    def reset(self) -> None:
        self.i_roll = 0.0
        self.i_pitch = 0.0
        self.prev_roll = 0.0
        self.prev_pitch = 0.0
        self.initialized = False

    def step(self, base_z: float, roll: float, pitch: float, dt: float) -> list[float]:
        if dt <= 0.0:
            raise ValueError("dt must be > 0")

        if not self.initialized:
            self.prev_roll = roll
            self.prev_pitch = pitch
            self.initialized = True

        roll_rate = (roll - self.prev_roll) / dt
        pitch_rate = (pitch - self.prev_pitch) / dt

        self.prev_roll = roll
        self.prev_pitch = pitch

        err_roll = -roll
        err_pitch = -pitch

        self.i_roll = clip(self.i_roll + err_roll * dt, -self.i_limit, self.i_limit)
        self.i_pitch = clip(self.i_pitch + err_pitch * dt, -self.i_limit, self.i_limit)

        u_roll = (
            self.kp_roll * err_roll
            + self.ki_roll * self.i_roll
            - self.kd_roll * roll_rate
        )
        u_pitch = (
            self.kp_pitch * err_pitch
            + self.ki_pitch * self.i_pitch
            - self.kd_pitch * pitch_rate
        )

        targets = []
        for x, y in self.leg_xy:
            z = base_z + u_roll * y - u_pitch * x
            targets.append(clip(z, self.z_min, self.z_max))

        return targets


def main() -> None:
    model = mujoco.MjModel.from_xml_path(str(MODEL_PATH))
    data = mujoco.MjData(model)
    mujoco.mj_forward(model, data)

    dt = model.opt.timestep

    body_id = require_id(model, mujoco.mjtObj.mjOBJ_BODY, BODY_NAME)
    leg_body_ids = [require_id(model, mujoco.mjtObj.mjOBJ_BODY, name) for name in LEG_NAMES]

    steering_actuator_ids = get_ids(model, mujoco.mjtObj.mjOBJ_ACTUATOR, "steering_motor_{}")
    steering_joint_ids = get_ids(model, mujoco.mjtObj.mjOBJ_JOINT, "Steering_Joint_{}")

    wheel_actuator_ids = get_ids(model, mujoco.mjtObj.mjOBJ_ACTUATOR, "wheel_motor_{}")

    lift_actuator_ids = get_ids(model, mujoco.mjtObj.mjOBJ_ACTUATOR, "lift_{}")
    lift_joint_ids = get_ids(model, mujoco.mjtObj.mjOBJ_JOINT, "Prismatic_Joint_{}")

    steering_qpos = [model.jnt_qposadr[jid] for jid in steering_joint_ids]
    steering_dof = [model.jnt_dofadr[jid] for jid in steering_joint_ids]
    lift_qpos = [model.jnt_qposadr[jid] for jid in lift_joint_ids]

    steering_limits = [
        (
            float(model.actuator_ctrlrange[aid, 0]),
            float(model.actuator_ctrlrange[aid, 1]),
        )
        for aid in steering_actuator_ids
    ]
    wheel_limits = [
        (
            float(model.actuator_ctrlrange[aid, 0]),
            float(model.actuator_ctrlrange[aid, 1]),
        )
        for aid in wheel_actuator_ids
    ]
    lift_limits = [
        (
            float(model.actuator_ctrlrange[aid, 0]),
            float(model.actuator_ctrlrange[aid, 1]),
        )
        for aid in lift_actuator_ids
    ]

    wheel_max = [max(abs(low), abs(high)) for low, high in wheel_limits]

    leg_xy = [
        (float(model.body_pos[bid][0]), float(model.body_pos[bid][1]))
        for bid in leg_body_ids
    ]
    x_mean = sum(x for x, _ in leg_xy) / N
    y_mean = sum(y for _, y in leg_xy) / N
    leg_xy = [(x - x_mean, y - y_mean) for x, y in leg_xy]

    steppers = [SteeringStepper() for _ in range(N)]
    lifts = [LinearActuator(z_min=LIFT_MIN, z_max=LIFT_MAX, max_speed=0.025) for _ in range(N)]
    level_ctrl = LevelController(leg_xy, z_min=LIFT_MIN, z_max=LIFT_MAX)

    steering_targets = [0.0] * N
    turn_targets = [-TURN_ANGLE, TURN_ANGLE, TURN_ANGLE, -TURN_ANGLE]

    mode = "stop"     # stop | forward | turn
    base_z = 0.0

    def apply_steering_targets() -> None:
        for i in range(N):
            steppers[i].set_reference(steering_targets[i])

    def reset_controllers() -> None:
        for i in range(N):
            steppers[i].reset()
        apply_steering_targets()

        for i in range(N):
            lifts[i].reset(float(data.qpos[lift_qpos[i]]))

        level_ctrl.reset()

    def key_callback(keycode: int) -> None:
        nonlocal mode, base_z, steering_targets

        try:
            key = chr(keycode).lower()
        except ValueError:
            return

        if key == "1":
            steering_targets = [0.0] * N
            apply_steering_targets()
            mode = "forward"
            print("mode=forward, steering=0")

        elif key == "2":
            mode = "stop"
            print("mode=stop")

        elif key == "3":
            steering_targets = turn_targets[:]
            apply_steering_targets()
            mode = "turn"
            print("mode=turn, steering=45deg")

        elif key == "4":
            base_z = LIFT_LOW
            print(f"base_z={base_z:.3f}")

        elif key == "5":
            base_z = LIFT_HIGH
            print(f"base_z={base_z:.3f}")

    reset_controllers()

    last_time = float(data.time)
    last_log_time = -1.0

    print("Keys:")
    print("  1 -> straight + forward")
    print("  2 -> stop")
    print("  3 -> 45 deg steering + forward")
    print("  4 -> base lift 0.0")
    print("  5 -> base lift 0.1")

    with mujoco.viewer.launch_passive(
        model,
        data,
        key_callback=key_callback,
        show_left_ui=False,
        show_right_ui=False,
    ) as viewer:
        while viewer.is_running():
            t0 = time.perf_counter()

            # reset из GUI
            if data.time < last_time:
                reset_controllers()

            last_time = float(data.time)

            steering_angles = [float(data.qpos[idx]) for idx in steering_qpos]
            steering_rates = [float(data.qvel[idx]) for idx in steering_dof]
            lift_positions = [float(data.qpos[idx]) for idx in lift_qpos]

            roll, pitch = body_roll_pitch(data, body_id)

            steering_ready = all(
                abs(angle_error(steering_targets[i], steering_angles[i])) <= STEERING_POS_TOL
                and abs(steering_rates[i]) <= STEERING_VEL_TOL
                for i in range(N)
            )

            lift_targets = level_ctrl.step(base_z=base_z, roll=roll, pitch=pitch, dt=dt)

            for i in range(N):
                lifts[i].set_reference(lift_targets[i])

            with viewer.lock():
                # steering
                for i in range(N):
                    tau = steppers[i].compute_torque(
                        delta=steering_angles[i],
                        delta_dot=steering_rates[i],
                        dt=dt,
                    )
                    low, high = steering_limits[i]
                    data.ctrl[steering_actuator_ids[i]] = clip(tau, low, high)

                # wheels
                for i in range(N):
                    cmd = 0.0

                    if steering_ready:
                        if mode == "forward":
                            cmd = WHEEL_SIGNS[i] * wheel_max[i]
                        elif mode == "turn":
                            cmd = TURN_SIGNS[i] * wheel_max[i]

                    low, high = wheel_limits[i]
                    data.ctrl[wheel_actuator_ids[i]] = clip(cmd, low, high)

                # lifts
                for i in range(N):
                    cmd = lifts[i].step(lift_positions[i])
                    low, high = lift_limits[i]
                    data.ctrl[lift_actuator_ids[i]] = clip(cmd, low, high)

                mujoco.mj_step(model, data)

            viewer.sync()

            if data.time - last_log_time > 0.5:
                last_log_time = float(data.time)
                print(
                    f"roll={math.degrees(roll): .2f} deg, "
                    f"pitch={math.degrees(pitch): .2f} deg, "
                    f"base_z={base_z:.3f}, "
                    f"ready={steering_ready}"
                )

            remaining = dt - (time.perf_counter() - t0)
            if remaining > 0.0:
                time.sleep(remaining)


if __name__ == "__main__":
    main()