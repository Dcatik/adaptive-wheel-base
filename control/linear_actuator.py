class LinearActuator:
    def __init__(self, z_min=0.0, z_max=0.1, max_speed=0.025, pos_eps=0.0005):
        self.z_min = float(z_min)
        self.z_max = float(z_max)
        self.max_speed = float(max_speed)
        self.pos_eps = float(pos_eps)

        self.z_ref = self.z_min

    def reset(self, z0=0.0):
        z0 = self._clip(float(z0), self.z_min, self.z_max)
        self.z_ref = z0

    def set_reference(self, z_ref):
        self.z_ref = self._clip(float(z_ref), self.z_min, self.z_max)

    def step(self, z):
        z = float(z)
        error = self.z_ref - z

        if abs(error) <= self.pos_eps:
            return 0.0

        return self.max_speed if error > 0.0 else -self.max_speed

    @staticmethod
    def _clip(value, low, high):
        return max(low, min(high, value))