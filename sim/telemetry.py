from collections import deque
import matplotlib.pyplot as plt


class WheelSample:
    def __init__(self, t, voltage, current, omega, torque):
        self.t = t
        self.voltage = voltage
        self.current = current
        self.omega = omega
        self.torque = torque


class WheelTelemetryBuffer:
    def __init__(self, maxlen: int = 2000):
        self.t = deque(maxlen=maxlen)
        self.voltage = deque(maxlen=maxlen)
        self.current = deque(maxlen=maxlen)
        self.omega = deque(maxlen=maxlen)
        self.torque = deque(maxlen=maxlen)

    def append(self, sample: WheelSample) -> None:
        self.t.append(sample.t)
        self.voltage.append(sample.voltage)
        self.current.append(sample.current)
        self.omega.append(sample.omega)
        self.torque.append(sample.torque)


class RealtimePlotter:
    def __init__(self, wheel_count: int = 4):
        plt.ion()

        self.fig, self.axes = plt.subplots(4, 1, figsize=(10, 10), sharex=True)
        self.fig.suptitle("Wheel Electromechanical States")

        self.axes[0].set_ylabel("Voltage [V]")
        self.axes[1].set_ylabel("Current [A]")
        self.axes[2].set_ylabel("Omega [rad/s]")
        self.axes[3].set_ylabel("Torque [N·m]")
        self.axes[3].set_xlabel("Time [s]")

        self.lines = {
            "voltage": [],
            "current": [],
            "omega": [],
            "torque": [],
        }

        for wheel_idx in range(wheel_count):
            label = f"wheel_{wheel_idx + 1}"
            self.lines["voltage"].append(self.axes[0].plot([], [], label=label)[0])
            self.lines["current"].append(self.axes[1].plot([], [], label=label)[0])
            self.lines["omega"].append(self.axes[2].plot([], [], label=label)[0])
            self.lines["torque"].append(self.axes[3].plot([], [], label=label)[0])

        for ax in self.axes:
            ax.grid(True)
            ax.legend(loc="upper right")

        self.fig.tight_layout()

    def update(self, buffers: list[WheelTelemetryBuffer]) -> None:
        for idx, buf in enumerate(buffers):
            t = list(buf.t)

            self.lines["voltage"][idx].set_data(t, list(buf.voltage))
            self.lines["current"][idx].set_data(t, list(buf.current))
            self.lines["omega"][idx].set_data(t, list(buf.omega))
            self.lines["torque"][idx].set_data(t, list(buf.torque))

        for ax in self.axes:
            ax.relim()
            ax.autoscale_view()

        self.fig.canvas.draw_idle()
        self.fig.canvas.flush_events()