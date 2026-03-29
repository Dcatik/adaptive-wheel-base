class WheelMotor:
    def __init__(self, R, L, Ke, Kt, current_limit=30.0, i=0.0):
        self.R = R
        self.L = L
        self.Ke = Ke
        self.Kt = Kt
        self.current_limit = current_limit
        self.i = i

    def reset(self) -> None:
        # Reset current state to zero.
        self.i = 0.0

    def step(self, voltage: float, omega: float, dt: float) -> float:
        # Current dynamics:
        # L * di/dt = u - R*i - Ke*omega
        di_dt = (voltage - self.R * self.i - self.Ke * omega) / self.L

        # Euler integration:
        # i(k+1) = i(k) + dt * di/dt
        self.i += dt * di_dt

        # Clamp current to a realistic range.
        self.i = max(-self.current_limit, min(self.current_limit, self.i))

        # Motor torque:
        # tau = Kt * i
        return self.Kt * self.i