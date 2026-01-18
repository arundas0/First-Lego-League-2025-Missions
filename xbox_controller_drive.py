"""
Xbox Controller Remote Control for Pybricks Robot
Allows driving the FLL robot with an Xbox controller over Bluetooth.

Requirements:
- pip install pygame pybricksdev
- Pybricks hub with Bluetooth enabled
- Xbox controller connected to computer (USB or Bluetooth)

Controls:
- Left Stick Y-axis: Forward/Backward
- Right Stick X-axis: Left/Right turning
- Left Trigger: Brake
- A Button: Emergency stop
"""

import pygame
import sys
import time
from subprocess import Popen, PIPE
import threading
import os

# Configuration matching FLL robot setup
WHEEL_DIAMETER_MM = 63.5
AXLE_TRACK_MM = 140
MAX_SPEED = 500  # mm/s maximum speed
TURN_SPEED = 200  # deg/s maximum turn rate

# Controller deadzone (ignore small inputs)
DEADZONE = 0.1


class XboxController:
    """Handles Xbox controller input using pygame"""

    def __init__(self):
        pygame.init()
        pygame.joystick.init()

        if pygame.joystick.get_count() == 0:
            raise RuntimeError("No controller detected. Please connect Xbox controller.")

        self.joystick = pygame.joystick.Joystick(0)
        self.joystick.init()

        print(f"Controller connected: {self.joystick.get_name()}")
        print(f"Axes: {self.joystick.get_numaxes()}")
        print(f"Buttons: {self.joystick.get_numbuttons()}")

    def get_drive_values(self):
        """
        Returns (forward_speed, turn_rate, should_stop)
        forward_speed: -1.0 to 1.0 (negative = backward)
        turn_rate: -1.0 to 1.0 (negative = left)
        should_stop: True if emergency stop pressed
        """
        pygame.event.pump()

        # Left stick Y-axis for forward/backward (inverted in many controllers)
        forward = -self.joystick.get_axis(1)  # Axis 1 is typically left stick Y

        # Right stick X-axis for turning
        turn = self.joystick.get_axis(2)  # Axis 2 is typically right stick X

        # Apply deadzone
        if abs(forward) < DEADZONE:
            forward = 0.0
        if abs(turn) < DEADZONE:
            turn = 0.0

        # A button (button 0 on most Xbox controllers) for emergency stop
        stop_button = self.joystick.get_button(0)

        return forward, turn, stop_button

    def close(self):
        """Cleanup pygame resources"""
        pygame.quit()


def create_hub_script():
    """
    Creates a Python script that runs on the Pybricks hub
    to receive and execute drive commands via stdin
    """
    return """
from pybricks.hubs import PrimeHub
from pybricks.pupdevices import Motor
from pybricks.robotics import DriveBase
from pybricks.parameters import Port, Direction, Stop
from pybricks.tools import wait
import sys

# Robot configuration
WHEEL_DIAMETER_MM = 63.5
AXLE_TRACK_MM = 140

hub = PrimeHub()
left_motor = Motor(Port.A, Direction.COUNTERCLOCKWISE)
right_motor = Motor(Port.B, Direction.CLOCKWISE)
robot = DriveBase(left_motor, right_motor, WHEEL_DIAMETER_MM, AXLE_TRACK_MM)

print("Robot ready for remote control")
hub.speaker.beep(1000, 100)

try:
    while True:
        # Read command from stdin (sent from computer)
        line = sys.stdin.readline().strip()

        if not line:
            continue

        if line == "STOP":
            robot.stop()
            left_motor.stop()
            right_motor.stop()
            hub.speaker.beep(400, 200)
            break

        if line == "BRAKE":
            robot.stop()
            continue

        # Parse drive command: "DRIVE speed turn_rate"
        if line.startswith("DRIVE"):
            parts = line.split()
            if len(parts) == 3:
                speed = int(parts[1])
                turn_rate = int(parts[2])
                robot.drive(speed, turn_rate)

        wait(10)

except KeyboardInterrupt:
    pass
finally:
    robot.stop()
    print("Remote control stopped")
    hub.speaker.beep(600, 100)
"""


def main():
    """Main control loop"""
    print("=" * 50)
    print("Xbox Controller Remote Control for Pybricks")
    print("=" * 50)
    print("\nControls:")
    print("  Left Stick Y:  Forward/Backward")
    print("  Right Stick X: Turn Left/Right")
    print("  A Button:      Emergency Stop")
    print("  Ctrl+C:        Exit program")
    print("\nConnecting to controller...")

    try:
        controller = XboxController()
    except RuntimeError as e:
        print(f"Error: {e}")
        return

    print("\nController connected!")
    print("\nNow connect to your Pybricks hub:")
    print("  1. Make sure hub is on and Bluetooth is enabled")
    print("  2. This script will use pybricksdev to connect")
    print("\nStarting in 3 seconds...")
    time.sleep(3)

    # Save the hub script to a temporary file
    hub_script_path = "/tmp/pybricks_remote.py"
    with open(hub_script_path, "w") as f:
        f.write(create_hub_script())

    print("\nConnecting to hub via Bluetooth...")
    print("(This may take a few seconds...)")

    # Start pybricksdev process to run script on hub
    # Note: This requires the hub to be paired with your computer
    try:
        process = Popen(
            ["pybricksdev", "run", "ble", hub_script_path],
            stdin=PIPE,
            stdout=PIPE,
            stderr=PIPE,
            text=True,
            bufsize=1
        )
    except FileNotFoundError:
        print("\nError: pybricksdev not found!")
        print("Please install it: pip install pybricksdev")
        controller.close()
        return

    # Give the hub time to initialize
    time.sleep(2)

    print("\n" + "=" * 50)
    print("READY! Use Xbox controller to drive the robot")
    print("=" * 50)

    running = True
    last_forward = 0
    last_turn = 0

    try:
        while running:
            forward, turn, stop = controller.get_drive_values()

            if stop:
                print("\n[EMERGENCY STOP]")
                process.stdin.write("STOP\n")
                process.stdin.flush()
                running = False
                break

            # Convert normalized values to robot speeds
            drive_speed = int(forward * MAX_SPEED)
            turn_rate = int(turn * TURN_SPEED)

            # Only send command if values changed significantly
            if abs(drive_speed - last_forward) > 5 or abs(turn_rate - last_turn) > 5:
                command = f"DRIVE {drive_speed} {turn_rate}\n"
                process.stdin.write(command)
                process.stdin.flush()

                # Display current values
                print(f"\rSpeed: {drive_speed:4d} mm/s | Turn: {turn_rate:4d} deg/s", end="")

                last_forward = drive_speed
                last_turn = turn_rate

            time.sleep(0.05)  # 20Hz update rate

    except KeyboardInterrupt:
        print("\n\nExiting...")

    finally:
        # Stop the robot
        try:
            process.stdin.write("STOP\n")
            process.stdin.flush()
        except:
            pass

        # Cleanup
        controller.close()
        process.terminate()
        process.wait(timeout=2)

        # Clean up temp file
        if os.path.exists(hub_script_path):
            os.remove(hub_script_path)

        print("Remote control stopped.")


if __name__ == "__main__":
    main()
