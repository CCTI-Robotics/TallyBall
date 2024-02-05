# ---------------------------------------------------------------------------- #
#                                                                              #
# 	Module:       main.py                                                      #
# 	Author:       8510                                                         #
# 	Created:      1/31/2024, 11:39:02 AM                                       #
# 	Description:  V5 project                                                   #
#                                                                              #
# ---------------------------------------------------------------------------- #
# Library imports
from vex import *
import time

# Brain should be defined by default
brain=Brain()

brain.screen.print("Hello V5")

controller = Controller()

## Constants

# Smart Drive information
WHEEL_TRAVEL = 300 # Millimeters
TRACK_WIDTH = 320 # Millimeters
WHEEL_BASE = 320 # Millimeters
EXTERNAL_GEAR_RATIO = 1 # Gear Ratio

# Ports
BACK_LEFT_DRIVE_MOTOR = Ports.PORT1
BACK_RIGHT_DRIVE_MOTOR = Ports.PORT2
FLYWHEEL_ARM_MOTOR = Ports.PORT4
NMTT_PORT = Ports.PORT5

IMU_SENSOR = Ports.PORT10
GPS_SENSOR = Ports.PORT11

# "Soft Enum" for the flywheel mode
class FlywheelMode:
    STOPPED = "STOPPED"
    LAUNCH = "LAUNCH"
    INTAKE = "INTAKE"
    EXPEL = "EXPEL"

RoE = Controller() # Ruler of Everything
current_flywheel_mode = FlywheelMode.STOPPED

def update_mode(new_mode):
    """
    Update the flywheel's mode and print it on the controller screen.
    """
    global current_flywheel_mode
    current_flywheel_mode = new_mode

    RoE.screen.clear_row(1)
    RoE.screen.set_cursor(1, 0)
    RoE.screen.print(current_flywheel_mode)

def change_flywheel_mode():
    """
    Switches the flywheel mode between LAUNCH and STOPPED
    when pressing the B button.
    """
    if current_flywheel_mode == FlywheelMode.LAUNCH:
        update_mode(FlywheelMode.STOPPED)

    elif current_flywheel_mode == FlywheelMode.STOPPED:
        update_mode(FlywheelMode.LAUNCH)

RoE.buttonB.pressed(change_flywheel_mode)


def driver_control():
    """
    Code for the driver control period.
    This mainly handles the controller input.
    """
    RoE.screen.clear_screen()
    current_time = time.time()

    while True:
        # Only manually control the flywheel if its mode is not LAUNCH
        if not current_flywheel_mode == FlywheelMode.LAUNCH:
            # If L2, or left trigger, is pressed
            if RoE.buttonL2.pressing():
                update_mode(FlywheelMode.EXPEL)

            # If L1, or left shoulder, is pressed
            elif RoE.buttonL1.pressing():
                update_mode(FlywheelMode.INTAKE)

            else:
                update_mode(FlywheelMode.STOPPED)
        
        # Controller screen stuff so we know what state the robot is in
        
        # Update flywheel motor temperature every 5 seconds
        if time.time() - current_time >= 5:
            temp += 1
            controller.screen.clear_row(2)
            controller.screen.set_cursor(2, 0)
            controller.screen.print("NMTT Temp: ", temp)

            current_time = time.time()

driver_control()