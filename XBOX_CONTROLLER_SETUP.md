# Xbox Controller Remote Control Setup

This guide explains how to use an Xbox controller to remotely drive your Pybricks robot.

## What You Need

1. LEGO SPIKE Prime Hub with Pybricks firmware installed
2. Xbox controller (Xbox 360, Xbox One, or Xbox Series X/S)
3. Computer with Python installed
4. USB cable or Bluetooth to connect controller to computer

## Installation Steps

### 1. Install Dependencies

```bash
pip install pygame pybricksdev
```

### 2. Connect Your Xbox Controller

**Option A: USB Connection (Recommended)**
- Plug your Xbox controller into your computer with a USB cable
- Wait for it to be recognized (LED should light up)

**Option B: Bluetooth Connection**
- Put controller in pairing mode (hold Xbox + Sync buttons)
- On your computer, go to Bluetooth settings and pair the controller
- Wait for connection (LED should stay solid)

### 3. Pair Your Pybricks Hub

Your hub needs to be paired with your computer for Bluetooth communication:

```bash
# List available Pybricks devices
pybricksdev scan

# The first time, you may need to pair the hub
# Follow prompts to connect
```

## Running the Remote Control

1. Turn on your Pybricks hub
2. Make sure Xbox controller is connected to computer
3. Run the program:

```bash
python xbox_controller_drive.py
```

4. The program will:
   - Connect to your Xbox controller
   - Connect to your Pybricks hub via Bluetooth
   - Upload control code to the hub
   - Start listening to controller input

## Controls

| Control | Action |
|---------|--------|
| **Left Stick (Up/Down)** | Drive forward/backward |
| **Right Stick (Left/Right)** | Turn left/right |
| **A Button** | Emergency stop |
| **Ctrl+C** | Exit program |

## How It Works

1. **Computer Side**: The `xbox_controller_drive.py` script runs on your computer, reading input from the Xbox controller using the `pygame` library

2. **Hub Side**: A small control script is uploaded to the hub that receives drive commands over Bluetooth and controls the motors

3. **Communication**: Commands are sent at ~20Hz (20 times per second) for responsive control

## Tuning the Controls

You can adjust the following parameters in `xbox_controller_drive.py`:

```python
MAX_SPEED = 500      # Maximum drive speed in mm/s
TURN_SPEED = 200     # Maximum turn rate in deg/s
DEADZONE = 0.1       # Ignore small joystick movements (0.0-1.0)
```

Lower values = more precise, slower movement
Higher values = faster, less precise movement

## Troubleshooting

### "No controller detected"
- Make sure controller is properly connected via USB or Bluetooth
- Try unplugging and reconnecting
- Check if controller works in other programs

### "pybricksdev not found"
- Install it: `pip install pybricksdev`
- Make sure you're using the correct Python environment

### Hub won't connect
- Make sure hub is turned on and has battery
- Verify Bluetooth is enabled on your computer
- Try running: `pybricksdev scan` to see if hub is visible
- Restart the hub by holding the center button

### Robot doesn't move
- Check motor ports (should be Port A and Port B)
- Verify motor directions match your robot configuration
- Test motors individually with a simple program first

### Controller feels sluggish
- Reduce the `time.sleep(0.05)` value in the main loop for faster updates
- Check your Bluetooth connection quality
- Make sure no other programs are using the controller

### Robot moves opposite direction
- In the hub script, swap `Direction.COUNTERCLOCKWISE` and `Direction.CLOCKWISE` for the motors
- Or multiply the speed values by -1

## Safety Tips

- **Start with LOW MAX_SPEED** (like 200) until you're comfortable
- Always have someone ready to press the **A button** for emergency stop
- Test in an open area away from obstacles
- Keep hands clear of wheels and gears
- The hub CENTER button also works as an emergency stop

## Advanced: Tank Drive Mode

If you want tank-style driving (each stick controls one side), create a modified version:

```python
# Left stick controls left motor
# Right stick controls right motor
left_speed = -controller.joystick.get_axis(1) * MAX_SPEED
right_speed = -controller.joystick.get_axis(3) * MAX_SPEED
```

## Testing Without Hardware

To test controller input without a hub connected:

```python
import pygame

pygame.init()
pygame.joystick.init()
joystick = pygame.joystick.Joystick(0)
joystick.init()

print("Testing controller...")
while True:
    pygame.event.pump()
    print(f"Left Y: {joystick.get_axis(1):.2f} | Right X: {joystick.get_axis(2):.2f}")
    time.sleep(0.1)
```

Press Ctrl+C to exit.

## Next Steps

- Try adding button controls for attachment motors (Port C and Port D)
- Implement multiple speed modes (slow, medium, fast) with bumper buttons
- Add visual feedback with hub display or lights
- Record and playback movement sequences

Happy driving!
