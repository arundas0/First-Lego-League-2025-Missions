import sys
import types
import unittest


def _install_pybricks_fakes():
    pybricks = types.ModuleType("pybricks")
    hubs = types.ModuleType("pybricks.hubs")
    pupdevices = types.ModuleType("pybricks.pupdevices")
    robotics = types.ModuleType("pybricks.robotics")
    parameters = types.ModuleType("pybricks.parameters")
    tools = types.ModuleType("pybricks.tools")

    class FakeIMU:
        def __init__(self):
            self.heading_value = 0.0

        def reset_heading(self, value):
            self.heading_value = float(value)

        def heading(self):
            return float(self.heading_value)

    class FakeSpeaker:
        def beep(self, _freq, _duration):
            pass

    class FakeButtons:
        def pressed(self):
            return []

    class FakePrimeHub:
        def __init__(self):
            self.imu = FakeIMU()
            self.speaker = FakeSpeaker()
            self.buttons = FakeButtons()

    class FakeMotor:
        def __init__(self, *_args, **_kwargs):
            self.speed = 0

        def run(self, speed):
            self.speed = speed

        def stop(self):
            self.speed = 0

    class FakeDriveBase:
        def __init__(self, *_args, **_kwargs):
            self.last_settings = {}
            self.turn_calls = []

        def settings(self, **kwargs):
            self.last_settings.update(kwargs)

        def turn(self, _angle):
            self.turn_calls.append(_angle)

    class _Direction:
        COUNTERCLOCKWISE = 1
        CLOCKWISE = 2

    class _Button:
        CENTER = "center"

    class _Stop:
        HOLD = "hold"
        BRAKE = "brake"

    class _Port:
        A = "A"
        B = "B"
        C = "C"
        D = "D"

    def _wait(_ms):
        pass

    class _StopWatch:
        def reset(self):
            pass

        def time(self):
            return 0

    hubs.PrimeHub = FakePrimeHub
    pupdevices.Motor = FakeMotor
    pupdevices.ColorSensor = object
    robotics.DriveBase = FakeDriveBase
    parameters.Port = _Port
    parameters.Direction = _Direction
    parameters.Button = _Button
    parameters.Stop = _Stop
    parameters.Color = object
    tools.wait = _wait
    tools.StopWatch = _StopWatch

    sys.modules["pybricks"] = pybricks
    sys.modules["pybricks.hubs"] = hubs
    sys.modules["pybricks.pupdevices"] = pupdevices
    sys.modules["pybricks.robotics"] = robotics
    sys.modules["pybricks.parameters"] = parameters
    sys.modules["pybricks.tools"] = tools


_install_pybricks_fakes()

import FLL2025Missions as missions


class FakeRobot:
    def __init__(self, imu, turn_factor=0.9):
        self.imu = imu
        self.turn_factor = turn_factor
        self.last_settings = {}
        self.turn_calls = []

    def settings(self, **kwargs):
        self.last_settings.update(kwargs)

    def turn(self, angle):
        self.turn_calls.append(angle)
        self.imu.heading_value += angle * self.turn_factor


class FakeMotor:
    def __init__(self):
        self.speed = 0

    def run(self, speed):
        self.speed = speed

    def stop(self):
        self.speed = 0


class FakeHub:
    def __init__(self, imu):
        self.imu = imu

        class _Speaker:
            def beep(self, _freq, _duration):
                pass

        class _Buttons:
            def pressed(self):
                return []

        self.speaker = _Speaker()
        self.buttons = _Buttons()


class FakeIMU:
    def __init__(self):
        self.heading_value = 0.0

    def reset_heading(self, value):
        self.heading_value = float(value)

    def heading(self):
        return float(self.heading_value)


def _setup_mission_fakes(turn_factor=0.9):
    imu = FakeIMU()
    hub = FakeHub(imu)
    left = FakeMotor()
    right = FakeMotor()
    robot = FakeRobot(imu, turn_factor=turn_factor)

    missions.hub = hub
    missions.left_motor = left
    missions.right_motor = right
    missions.robot = robot

    missions._test_clock = 0

    def wait(ms):
        missions._test_clock += ms
        if left.speed or right.speed:
            delta = (left.speed - right.speed) * ms * 0.001 * 0.2
            imu.heading_value += delta

    class StopWatch:
        def __init__(self):
            self.start_time = missions._test_clock

        def reset(self):
            self.start_time = missions._test_clock

        def time(self):
            return missions._test_clock - self.start_time

    missions.wait = wait
    missions.StopWatch = StopWatch

    return robot, imu


class GyroTurnTests(unittest.TestCase):
    def test_gyro_turn_medium_bulk_margin_positive(self):
        robot, imu = _setup_mission_fakes(turn_factor=1.0)

        missions.gyro_turn(90, mode="medium", settle_tol=2, settle_timeout_ms=1000)

        self.assertEqual(robot.last_settings.get("turn_rate"), 140)
        self.assertAlmostEqual(robot.turn_calls[0], 87, places=3)
        self.assertLessEqual(abs(imu.heading() - 90), 2.0)

    def test_gyro_turn_medium_bulk_margin_negative(self):
        robot, imu = _setup_mission_fakes(turn_factor=1.0)

        missions.gyro_turn(-90, mode="medium", settle_tol=2, settle_timeout_ms=1000)

        self.assertAlmostEqual(robot.turn_calls[0], -87, places=3)
        self.assertLessEqual(abs(imu.heading() - (-90)), 2.0)

    def test_gyro_turn_converges_with_unpredictable_turn(self):
        robot, imu = _setup_mission_fakes(turn_factor=1.2)

        missions.gyro_turn(45, settle_tol=2, settle_timeout_ms=1000)

        self.assertGreaterEqual(len(robot.turn_calls), 2)
        self.assertLessEqual(abs(imu.heading() - 45), 2.0)


if __name__ == "__main__":
    unittest.main()
