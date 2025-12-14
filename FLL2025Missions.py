from pybricks.hubs import PrimeHub
from pybricks.pupdevices import Motor, ColorSensor
from pybricks.robotics import DriveBase
from pybricks.parameters import Port, Direction, Button, Stop
from pybricks.tools import wait
from pybricks.parameters import Color

# -----------------------------
# Robot configuration
# -----------------------------
WHEEL_RADIUS_CM = 3.175
WHEEL_DIAMETER_MM = WHEEL_RADIUS_CM * 2 * 10  # cm -> mm
AXLE_TRACK_MM = 139  # IMPORTANT: set this to your real wheel-to-wheel distance

hub = PrimeHub()

# Drive motors (A/B). Adjust Directions if your robot drives backward.
left_motor = Motor(Port.A, Direction.COUNTERCLOCKWISE)
right_motor = Motor(Port.B, Direction.CLOCKWISE)
robot = DriveBase(left_motor, right_motor, WHEEL_DIAMETER_MM, AXLE_TRACK_MM)

# Attachment motors
motor_c = Motor(Port.C)
motor_d = Motor(Port.D)

# -----------------------------
# Shared helpers
# -----------------------------
def beep_ok():
    hub.speaker.beep(900, 80)

def beep_mission(n):
    # Beep N+1 times so kids can tell mission ran
    for _ in range(n + 1):
        hub.speaker.beep(700, 70)
        wait(80)

def emergency_stop_check():
    # CENTER button = stop anytime
    # (Bluetooth is used to START a mission; use CENTER to stop/emergency)
    if Button.CENTER in hub.buttons.pressed():
        robot.stop()
        left_motor.stop()
        right_motor.stop()
        motor_c.stop()
        motor_d.stop()
        hub.speaker.beep(200, 300)
        raise RuntimeError("Emergency stop")

def setup_drive():
    robot.stop()
    # “Default-ish” settings; missions override per move
    robot.settings(straight_speed=300, straight_acceleration=300)
    beep_ok()

def drive_cm(distance_cm, velocity_cm_s, acceleration_cm_s2, stop=Stop.HOLD):
    """Drive a set distance in cm using DriveBase (mm units internally)."""
    distance_mm = distance_cm * 10
    speed_mm_s = velocity_cm_s * 10
    accel_mm_s2 = acceleration_cm_s2 * 10

    robot.settings(straight_speed=speed_mm_s, straight_acceleration=accel_mm_s2)
    robot.straight(distance_mm)
    robot.stop()  # DriveBase stop uses internal behavior; motors also hold by default

def run_motor_for_degrees(m: Motor, degrees: int, speed: int, accel: int = 1000, stop=Stop.HOLD):

    # Note: Motor.run_angle(speed, rotation_angle) is blocking.
    m.run_angle(speed, degrees, then=stop, wait=True)

def gyro_turn(target_deg, slow_turn=False,axis_turn=True):
   
    # PrimeHub IMU heading is degrees. Reset to 0.
    hub.imu.reset_heading(0)
    wait(150)

    # Tune these for your robot
    speed = 100 if slow_turn else 400
    power = 40 if slow_turn else 60  # used as a coarse steer factor
    turn_speed = 1 if axis_turn else 3

    # We’ll spin in place by running motors opposite directions.
    # Loop until heading reaches target.
    while True:
        emergency_stop_check()
        heading = hub.imu.heading()

        # Normalize heading to [-180, 180] to match typical gyro turn logic
        if heading > 180:
            heading -= 360

        if abs(heading) >= abs(target_deg):
            break

        if target_deg > 0:  # left
            left_motor.run(-speed)
            right_motor.run(turn_speed*speed)
        else:               # right
            left_motor.run(turn_speed*speed)
            right_motor.run(-speed)

        wait(10)

    left_motor.stop()
    right_motor.stop()
    wait(100)

# -----------------------------
# Mission implementations (0–5)
# Converted from your SPIKE code
# -----------------------------
def mission_0():
    setup_drive()
    print("Mission 0")

    drive_cm(15, 30, 50)
    gyro_turn(10, slow_turn=True)
    wait(500)

    drive_cm(55, 100, 50)
    gyro_turn(-55, slow_turn=True)

    drive_cm(10, 30, 30)

    run_motor_for_degrees(motor_d, -1000, 1000) # SPIKE: move_sidearm_mission9(port.D, -1000, 1000, 500)
    run_motor_for_degrees(motor_c, 200, 1000) # SPIKE: move_sidearm_mission9(port.C, 100, 1000, 500)
    print("Turn completed")
    drive_cm(-4, 30, 50)
    print("drive complete")
    gyro_turn(40, slow_turn=False)
    drive_cm(-60, 30, 50)
    gyro_turn(45, slow_turn=False)
    drive_cm(-30, 30, 50)

def mission_1():
    setup_drive()
    print("Mission 1")

    hub.imu.reset_heading(0)
    wait(200)

    drive_cm(14, 30, 50)
    gyro_turn(45, slow_turn=True)

    run_motor_for_degrees(motor_c, 150, 720)     # move_sidearm_mission9(port.C, 150, 720, 1000)

    drive_cm(33, 30, 50)

    run_motor_for_degrees(motor_c, -120, 100)    # move_sidearm_mission9(port.C, -120, 100, 100)

    run_motor_for_degrees(motor_d, -720, 500)    # move_sidearm_mission9(port.D, -720, 500, 1000)
    run_motor_for_degrees(motor_c, 180, 1440)    # move_sidearm_mission9(port.C, 180, 1440, 1000)
    run_motor_for_degrees(motor_d, 720, 360)     # move_sidearm_mission9(port.D, 720, 360, 1000)

    drive_cm(-35, 30, 30)
    wait(200)
    drive_cm(10, 30, 50)

    gyro_turn(-30, slow_turn=False)

    drive_cm(-15, 300, 50)

    run_motor_for_degrees(motor_c, -120, 1000)
    gyro_turn(60, slow_turn=False)
    drive_cm(-40, 300, 50)

def mission_2():
    setup_drive()
    print("Mission 2")

    hub.imu.reset_heading(0)
    wait(200)

    # Your SPIKE code had a commented-out 10cm move; keeping behavior similar:
    # drive_cm(10, 30, 50)

    drive_cm(37, 30, 50)

    # SPIKE had a complex stall-detect version; here is a simpler "repeat wiggle" version:
    for _ in range(3):  # repetitions=3
        run_motor_for_degrees(motor_c, -180, 750)
        run_motor_for_degrees(motor_c, 180, 750)

    drive_cm(-15.5, 30, 50)

    hub.imu.reset_heading(0)
    wait(200)
    gyro_turn(90, slow_turn=True)

    drive_cm(195, 500, 500)

def mission_3():
    # This matches your “Challenge H 90” style (your Mission 3 file)
    setup_drive()
    print("Mission 3")

    drive_cm(41, 30, 5)
    drive_cm(-15, 17, 15)
    drive_cm(31, 15, 10)
    drive_cm(-50, 30, 10)

def mission_4():
    setup_drive()
    print("Mission 4")


    drive_cm(69, 20, 500)
    gyro_turn(43, slow_turn=True)

    drive_cm(23, 30, 200)

    # lift_arm(port.D , lift_arm_degrees=180)
    run_motor_for_degrees(motor_d, 180, 1000)

    # drop_arm(port.C , 150) then 200 fast
    run_motor_for_degrees(motor_c, 150, 300)
    wait(1000)
    run_motor_for_degrees(motor_c, 200, 1000)

    # lift_arm(port.C , -300 slow)
    run_motor_for_degrees(motor_c, -300, 500)

    drive_cm(-22, 17, 500)
    gyro_turn(140, slow_turn=False)

    drive_cm(61, 30, 500)

def mission_5():
    print("Mission 5#")
    setup_drive()

    hub.imu.reset_heading(0)
    wait(200)

    drive_cm(73, 30, 100)
    gyro_turn(-90, slow_turn=True)
    drive_cm(23, 30, 5)
    gyro_turn(-30, slow_turn=True)
    drive_cm(4, 30, 5)
    run_motor_for_degrees(motor_d, -600, 1000)
    drive_cm(10, 30, 5)
    run_motor_for_degrees(motor_d, 500, 300)
    drive_cm(-35, 30, 5)
    gyro_turn(31, slow_turn=True, axis_turn=False)
    run_motor_for_degrees(motor_d, -500, 300)
    drive_cm(10, 30, 5)
    run_motor_for_degrees(motor_d, 500, 300)

    # run_motor_for_degrees(motor_c, 450, 300)

MISSION_COLORS = [
    Color.RED,     # Mission 0
    Color.ORANGE,  # Mission 1
    Color.YELLOW,  # Mission 2
    Color.GREEN,   # Mission 3
    Color.BLUE,    # Mission 4
    Color.BLACK,  # Mission 5
]
POLL_MS = 50
def set_mission_light(index):
    hub.light.on(MISSION_COLORS[index])

# -----------------------------
# Button-to-mission launcher
# -----------------------------
MISSIONS = [
    ("Mission 0", mission_0),
    ("Mission 1", mission_1),
    ("Mission 2", mission_2),
    ("Mission 3", mission_3),
    ("Mission 4", mission_4),
    ("Mission 5", mission_5),
]

# -----------------------------
# Selector UI:
# LEFT/RIGHT = choose 0–5
# START = Bluetooth button
# -----------------------------
def beep_selection(index):
    for _ in range(index + 1):
        hub.speaker.beep(700, 60)
        wait(80)

def show_selection(index):
    name = MISSIONS[index][0]
    print("Selected:", name)
    set_mission_light(index)
    #beep_selection(index)

def wait_release_all():
    while any(b in hub.buttons.pressed() for b in [Button.LEFT, Button.RIGHT, Button.CENTER]):
        wait(20)

def main():
    selected = 0
    print("READY.")
    print("LEFT/RIGHT = choose Mission 0–5")
    print("BLUETOOTH = START immediately")

    show_selection(selected)

    right_hold_time = 0

    while True:
        emergency_stop_check()
        pressed = hub.buttons.pressed()

        # Bluetooth button = immediate START (press to run selected mission)
        if Button.BLUETOOTH in pressed:
            name, fn = MISSIONS[selected]
            print("STARTING (Bluetooth):", name)
            hub.speaker.beep(1000, 200)
            hub.light.on(Color.WHITE)   # running indicator
            wait(200)

            try:
                fn()
                hub.speaker.beep(600, 150)  # done
            except Exception as e:
                print("Error:", e)
                hub.speaker.beep(200, 500)

            # Reset after mission
            right_hold_time = 0
            set_mission_light(selected)
            show_selection(selected)

            # Wait until Bluetooth is released to avoid repeated starts
            while Button.BLUETOOTH in hub.buttons.pressed():
                wait(20)

            continue

        # ---------- RIGHT button logic(tap only) ----------
        if Button.RIGHT in pressed:
            selected = (selected + 1) % len(MISSIONS)
            show_selection(selected)
            while Button.RIGHT in hub.buttons.pressed():
                wait(20)

        # ---------- LEFT button (tap only) ----------
        if Button.LEFT in pressed:
            selected = (selected - 1) % len(MISSIONS)
            show_selection(selected)
            while Button.LEFT in hub.buttons.pressed():
                wait(20)

        wait(POLL_MS)

main()