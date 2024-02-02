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

bidding = SmartDrive(
    BACK_LEFT_DRIVE_MOTOR, # Motor 1
    BACK_RIGHT_DRIVE_MOTOR, # Motor 2
    IMU_SENSOR, # Gyro sensor (IMU)
    WHEEL_TRAVEL, # Wheel travel
    TRACK_WIDTH, # Track width
    WHEEL_BASE, # Wheel base
    MM, # Units
)
nmtt = Motor(NMTT_PORT, GearSetting.RATIO_6_1)
fly_arm = Motor(FLYWHEEL_ARM_MOTOR, GearSetting.RATIO_36_1)

RoE = Controller() # Ruler of Everything



"""
Preferred robot controls:
Axis 1 - Rotates robot (clockwise/counterclockwise)
Axis 3 - Moves robot forward/backward


"""

def driver_control():
    """
    Code for the driver control period.
    This mainly handles the controller input.
    """

    while True:
        rotation = RoE.axis1.value()
        drive = RoE.axis3.value()
        

        if rotation > 10:
            bidding.turn(RIGHT, rotation, PERCENT)
        elif rotation < -10:
            bidding.turn(LEFT, abs(rotation), PERCENT)
 
        if drive > 10:
            bidding.drive(FORWARD, drive, PERCENT)
        elif drive < -10:
            bidding.drive(REVERSE, abs(drive), PERCENT)
        



        
