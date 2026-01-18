# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a FIRST LEGO League (FLL) 2025 robotics competition codebase written in Python using the Pybricks framework. The code runs on a LEGO SPIKE Prime Hub and controls a robot to complete various competition missions. The project is designed to be accessible to kid teams while maintaining competitive-level precision.

## Development Commands

### Installing Dependencies
```bash
pip install pybricks
# Optional for testing:
pip install pytest
```

### Deploying Code to Hub

**Option 1: Pybricks Code Web App (Recommended for beginners)**
- Open https://code.pybricks.com in browser
- Upload and run `.py` files directly from the web interface

**Option 2: Command Line (Advanced)**
```bash
# Install deployment tool
pip install pybricksdev

# Upload a mission file to the hub
pybricksdev copy FLL2025Missions.py

# Run via Bluetooth
pybricksdev run ble FLL2025Missions.py
```

### Running Tests
```bash
# Run gyro turn unit tests locally
python test_gyro_turn.py
```

### Debugging
VS Code launch configuration is available at `.vscode/launch.json` for running code via `pybricksdev` with the debugger attached.

## Code Architecture

### Robot Configuration (Lines 11-26 in FLL2025Missions.py)

Critical hardware configuration at the top of each mission file:
- **WHEEL_DIAMETER_MM**: Calculated from WHEEL_RADIUS_CM (3.175 cm → 63.5 mm)
- **AXLE_TRACK_MM**: Distance between wheels (140 mm) - **MUST BE CALIBRATED** for your specific robot
- **Motor Ports**:
  - Port A: Left drive motor (COUNTERCLOCKWISE)
  - Port B: Right drive motor (CLOCKWISE)
  - Port C: Attachment motor (e.g., arm, gear mechanism)
  - Port D: Attachment motor (e.g., sidearm, lift)

The `AXLE_TRACK_MM` value is critical for turn accuracy. The gyro turn functions print calibration suggestions when turns are significantly off-target.

### Core Motion Primitives

The codebase provides three main motion control systems:

**1. Straight Driving**
- `drive_cm(distance_cm, velocity_cm_s, acceleration_cm_s2, stop=Stop.HOLD)`: Basic straight-line movement
- `drive_cm_stall(...)`: Same as above but detects motor stalls (returns True if completed, False if stalled)

**2. Gyro-Based Turning** (Two implementations)
- `gyro_turn(target_angle, mode, settle_tol, settle_timeout_ms)`: Original hybrid turn algorithm
  - Phase A: DriveBase `robot.turn()` does bulk of turn with a settle margin
  - Phase B: IMU settle loop corrects remaining error with fine nudges
  - Prints calibration diagnostics ("Suggested AXLE_TRACK_MM *= ~X.XX")

- `gyro_turn_phase1(target_angle, mode, settle_tol, settle_timeout_ms)`: Improved version
  - More aggressive Phase A (no margin left for settling)
  - Tighter default tolerance (0.25° vs 2.0°)
  - Used in Mission 0 and other precision missions

Both use three speed modes: "slow" (80-120 deg/s), "medium" (140-150 deg/s), "fast" (200-220 deg/s)

**3. Attachment Motor Control**
- `run_motor_for_degrees(motor, degrees, speed, accel, stop, wait)`: Rotate motor by exact degrees
- `motor.run_until_stalled(speed, then, duty_limit)`: Run until physical resistance (useful for limit switches)

### Mission Structure

Each mission follows this pattern:
1. `setup_drive(back=0|1)`: Reset robot state, optionally back up 1cm, set default speeds, beep confirmation
2. Sequence of drive, turn, and attachment motor commands
3. Print total execution time at end

Missions 0-7 are stored in the `MISSIONS` list (line 468) as tuples of `(name, function)`.

### Mission Selection UI

The `main()` function (line 501) implements a button-based mission selector:
- **LEFT/RIGHT buttons**: Cycle through missions 0-7
- **BLUETOOTH button**: Start the currently selected mission
- **CENTER button**: Emergency stop (checked throughout execution via `emergency_stop_check()`)
- Hub display shows mission number, hub light shows mission color (see `MISSION_COLORS` line 451)

### Safety System

`emergency_stop_check()` (line 40) is called frequently during mission execution:
- Checks if CENTER button is pressed
- Immediately stops all motors and raises `RuntimeError("Emergency stop")`
- Should be called in any long-running loop or between major movements

## File Differences

- **FLL2025Missions.py**: Current working version with all missions 0-7 implemented. Uses `gyro_turn_phase1` for critical turns. Includes `StopWatch` for performance timing.
- **FllPython2025_01022026.py**: Earlier version dated January 2, 2026. Some missions have different parameters. Missing `StopWatch` timing. Uses `gyro_turn` (original) more frequently.
- **test_gyro_turn.py**: Unit tests for gyro turn algorithms using fake Pybricks modules (doesn't require physical hardware)

When adding new missions or modifying existing ones, work in **FLL2025Missions.py** as it's the active version.

## Calibration and Tuning

### Turn Calibration
If turns are consistently under/overshooting:
1. Run a 90° turn with `gyro_turn()` (not phase1)
2. Check console output for "Suggested AXLE_TRACK_MM *= ~X.XX"
3. Multiply your current `AXLE_TRACK_MM` by that factor
4. Update line 13 and re-test

### Drive Distance Calibration
If drives are consistently over/undershooting:
1. Verify `WHEEL_RADIUS_CM` matches your wheel size (line 11)
2. For LEGO 62.4mm wheels, use radius = 3.12 cm
3. For LEGO 63.5mm wheels (default), use radius = 3.175 cm

### Speed Tuning
- Competition table surfaces vary (friction, levelness)
- Lower speeds (20-30 cm/s) for precision tasks near mission models
- Higher speeds (50-100 cm/s) for traveling or returning home
- Attachment motors typically use 300-1000 deg/s depending on torque needs

## Adding New Missions

1. Define a new function `mission_X()` following the existing pattern
2. Add it to the `MISSIONS` list (line 468)
3. Add a color to `MISSION_COLORS` list (line 451)
4. Test incrementally: add one movement at a time, run, measure, adjust
5. Use `print()` statements for debugging (output goes to Pybricks console)
6. Always call `emergency_stop_check()` in custom loops

## Common Patterns

**Approach and Manipulate Pattern** (see mission_4, mission_5):
```python
drive_cm(distance, speed, accel)  # Approach target
gyro_turn(angle)                   # Align to target
run_motor_for_degrees(motor_c, degrees, speed)  # Manipulate attachment
drive_cm(-distance, speed, accel)  # Return home
```

**Stall-Based Positioning** (see mission_1, mission_5):
```python
motor_c.run_until_stalled(-speed, then=Stop.BRAKE, duty_limit=50)
# Motor runs until it hits physical limit, then acts as a "home position"
```

**Multi-Step Mission** (see mission_0, mission_7):
Complex missions with multiple targets combine all primitives. Use intermediate `wait()` calls to allow mechanisms to settle before the next movement.

## Pybricks-Specific Notes

- All distances internally use **millimeters** (helper functions convert cm to mm)
- Angles use **degrees** (positive = clockwise, negative = counterclockwise)
- `wait(ms)` is **non-blocking** to the hub but blocking in your code flow
- `robot.straight()` and `robot.turn()` are **blocking by default** unless `wait=False` is passed
- IMU heading wraps at ±180°, but the gyro turn functions handle this internally
- Motor stall detection via `motor.run_until_stalled()` or `robot.stalled` property
