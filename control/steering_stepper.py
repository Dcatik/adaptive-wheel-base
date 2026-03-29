import math


class SteeringStepper:
    def __init__(
        self,
        gear_ratio=50.9,
        gear_efficiency=0.70,
        max_output_torque=4.0,
        backlash_deg=1.0,
        kp=9.9,
        ki = 5.0,
        kd=0.008,
        delta_ref=1.0,
        integral_limit = 60.0,
        integral_deadband_deg = 1.0,
        integral_error = 1.0,
    ):
        self.gear_ratio = gear_ratio
        self.gear_efficiency = gear_efficiency
        self.max_output_torque = max_output_torque
        self.backlash_deg = backlash_deg
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.delta_ref = delta_ref
        self.integral_limit = integral_limit
        self.integral_deadband_deg = integral_deadband_deg
        self.integral_error = integral_error

    def reset(self) -> None:
        # Reset target and integrator.
        self.delta_ref = 0.0
        self.integral_error = 0.0

    def set_reference(self, delta_ref: float) -> None:
        # Update steering target.
        self.delta_ref = delta_ref

    def add_step_command(self, step_count: int, microstep: int = 1) -> None:
        motor_step_deg = 1.8 / microstep

        # Output step is smaller due to gearbox ratio.
        output_step_deg = motor_step_deg / self.gear_ratio

        # Convert steps to output angle increment.
        delta_inc = math.radians(output_step_deg * step_count)

        # Accumulate target position.
        self.delta_ref += delta_inc

    def compute_torque(self, delta: float, delta_dot: float, dt: float) -> float:
        # Position error on the steering joint.
        error = self.delta_ref - delta

        # Wrap angle error to [-pi, pi].
        error = math.atan2(math.sin(error), math.cos(error))

        # Convert backlash and integral deadband to radians.
        backlash_rad = math.radians(self.backlash_deg)
        integral_deadband_rad = math.radians(self.integral_deadband_deg)

        # Simple backlash model:
        # inside backlash zone, the gearbox does not engage.
        if abs(error) < backlash_rad:
            effective_error = 0.0
        else:
            effective_error = error - math.copysign(backlash_rad, error)

        # Candidate integral update.
        integrate_allowed = abs(effective_error) > integral_deadband_rad

        if integrate_allowed:
            self.integral_error += effective_error * dt

            # Clamp integral state to avoid windup.
            self.integral_error = max(
                -self.integral_limit,
                min(self.integral_limit, self.integral_error),
            )

        raw_torque = (
            self.kp * effective_error
            + self.ki * self.integral_error
            - self.kd * delta_dot
        )

        output_torque = self.gear_efficiency * raw_torque

        saturated_output_torque = max(
            -self.max_output_torque,
            min(self.max_output_torque, output_torque),
        )

        # anti-windup:
        if integrate_allowed and output_torque != saturated_output_torque:
            if math.copysign(1.0, output_torque) == math.copysign(1.0, effective_error):
                self.integral_error -= effective_error * dt
                self.integral_error = max(
                    -self.integral_limit,
                    min(self.integral_limit, self.integral_error),
                )

                # Recompute torque after rollback.
                raw_torque = (
                    self.kp * effective_error
                    + self.ki * self.integral_error
                    - self.kd * delta_dot
                )
                output_torque = self.gear_efficiency * raw_torque
                saturated_output_torque = max(
                    -self.max_output_torque,
                    min(self.max_output_torque, output_torque),
                )

        return saturated_output_torque