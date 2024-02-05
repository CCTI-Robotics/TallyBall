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

bidding = SmartDrive(
    BACK_LEFT_DRIVE_MOTOR, # Motor 1
    BACK_RIGHT_DRIVE_MOTOR, # Motor 2
    IMU_SENSOR, # Gyro sensor (IMU)
    WHEEL_TRAVEL, # Wheel travel
    TRACK_WIDTH, # Track width
    WHEEL_BASE, # Wheel base
    MM, # Units
)
nmtt = Motor(NMTT_PORT, GearSetting.RATIO_6_1, True) # Never Meant to Throw
fly_arm = Motor(FLYWHEEL_ARM_MOTOR, GearSetting.RATIO_36_1)

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
        # Control the sticks
        rotation = RoE.axis1.value()
        drive = RoE.axis3.value()

        # Axis 1 control, or rotating the robot
        if rotation > 10:
            bidding.turn(RIGHT, rotation, PERCENT)
        elif rotation < -10:
            bidding.turn(LEFT, abs(rotation), PERCENT)
 
        # Axis 3 control, or moving the robot forward/backward
        if drive > 10:
            bidding.drive(FORWARD, drive, PERCENT)
        elif drive < -10:
            bidding.drive(REVERSE, abs(drive), PERCENT)

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
        
        if current_flywheel_mode == FlywheelMode.LAUNCH:
            nmtt.spin(FORWARD, 100, PERCENT)

        elif current_flywheel_mode == FlywheelMode.EXPEL:
            nmtt.spin(REVERSE, 50, PERCENT)

        elif current_flywheel_mode == FlywheelMode.INTAKE:
            nmtt.spin(FORWARD, 50, PERCENT)

        elif current_flywheel_mode == FlywheelMode.STOPPED:
            nmtt.stop(COAST)

        # Update the temperature of the flywheel motor on the controller
        if time.time() - current_time >= 3:
            controller.screen.clear_row(2)
            controller.screen.set_cursor(2, 0)
            controller.screen.print("NMTT Temp: ", nmtt.temperature(TemperatureUnits.FAHRENHEIT))

            current_time = time.time()
