# ---------------------------------------------------------------------------- #
#                                                                              #
# 	Module:       main.py                                                      #
# 	Author:       8510                                                         #
# 	Created:      1/31/2024, 11:39:02 AM                                       #
# 	Description:  V5 project                                                   #
#                                                                              #
# ---------------------------------------------------------------------------- #
# Library imports
#region VEXcode Generated Robot Configuration
from vex import *
import time

# Brain should be defined by default
brain=Brain()

# Robot configuration code
left_drive_smart = Motor(Ports.PORT1, GearSetting.RATIO_18_1, False)
right_drive_smart = Motor(Ports.PORT10, GearSetting.RATIO_18_1, True)
drivetrain_inertial = Inertial(Ports.PORT11)
bidding = SmartDrive(left_drive_smart, right_drive_smart, drivetrain_inertial, 319.19, 320, 40, MM, 1)
RoE = Controller(PRIMARY)


# wait for rotation sensor to fully initialize
wait(30, MSEC)

def calibrate_drivetrain():
    # Calibrate the Drivetrain Inertial
    sleep(200, MSEC)
    brain.screen.print("Calibrating")
    brain.screen.next_row()
    brain.screen.print("Inertial")
    drivetrain_inertial.calibrate()
    while drivetrain_inertial.is_calibrating():
        sleep(25, MSEC)
    brain.screen.clear_screen()
    brain.screen.set_cursor(1, 1)


def play_vexcode_sound(sound_name):
    # Helper to make playing sounds from the V5 in VEXcode easier and
    # keeps the code cleaner by making it clear what is happening.
    print("VEXPlaySound:" + sound_name)
    wait(5, MSEC)

# add a small delay to make sure we don't print in the middle of the REPL header
wait(200, MSEC)
# clear the console to make sure we don't have the REPL in the console
print("\033[2J")



# define variables used for controlling motors based on controller inputs
drivetrain_l_needs_to_be_stopped_controller_1 = False
drivetrain_r_needs_to_be_stopped_controller_1 = False

# define a task that will handle monitoring inputs from controller_1
def rc_auto_loop_function_controller_1():
    global drivetrain_l_needs_to_be_stopped_controller_1, drivetrain_r_needs_to_be_stopped_controller_1, remote_control_code_enabled
    # process the controller input every 20 milliseconds
    # update the motors based on the input values
    while True:
        if remote_control_code_enabled:
            # stop the motors if the brain is calibrating
            if drivetrain_inertial.is_calibrating():
                left_drive_smart.stop()
                right_drive_smart.stop()
                while drivetrain_inertial.is_calibrating():
                    sleep(25, MSEC)
            
            # calculate the drivetrain motor velocities from the controller joystick axies
            # left = axis3 + axis1
            # right = axis3 - axis1
            drivetrain_left_side_speed = RoE.axis3.position() + RoE.axis1.position()
            drivetrain_right_side_speed = RoE.axis3.position() - RoE.axis1.position()
            
            # check if the value is inside of the deadband range
            if drivetrain_left_side_speed < 5 and drivetrain_left_side_speed > -5:
                # check if the left motor has already been stopped
                if drivetrain_l_needs_to_be_stopped_controller_1:
                    # stop the left drive motor
                    left_drive_smart.stop()
                    # tell the code that the left motor has been stopped
                    drivetrain_l_needs_to_be_stopped_controller_1 = False
            else:
                # reset the toggle so that the deadband code knows to stop the left motor next
                # time the input is in the deadband range
                drivetrain_l_needs_to_be_stopped_controller_1 = True
            # check if the value is inside of the deadband range
            if drivetrain_right_side_speed < 5 and drivetrain_right_side_speed > -5:
                # check if the right motor has already been stopped
                if drivetrain_r_needs_to_be_stopped_controller_1:
                    # stop the right drive motor
                    right_drive_smart.stop()
                    # tell the code that the right motor has been stopped
                    drivetrain_r_needs_to_be_stopped_controller_1 = False
            else:
                # reset the toggle so that the deadband code knows to stop the right motor next
                # time the input is in the deadband range
                drivetrain_r_needs_to_be_stopped_controller_1 = True
            
            # only tell the left drive motor to spin if the values are not in the deadband range
            if drivetrain_l_needs_to_be_stopped_controller_1:
                left_drive_smart.set_velocity(drivetrain_left_side_speed, PERCENT)
                left_drive_smart.spin(FORWARD)
            # only tell the right drive motor to spin if the values are not in the deadband range
            if drivetrain_r_needs_to_be_stopped_controller_1:
                right_drive_smart.set_velocity(drivetrain_right_side_speed, PERCENT)
                right_drive_smart.spin(FORWARD)
        # wait before repeating the process
        wait(20, MSEC)

# define variable for remote controller enable/disable
remote_control_code_enabled = True

rc_auto_loop_thread_controller_1 = Thread(rc_auto_loop_function_controller_1)


## Constants

# Smart Drive information
WHEEL_TRAVEL = 300 # Millimeters
TRACK_WIDTH = 320 # Millimeters
WHEEL_BASE = 320 # Millimeters
EXTERNAL_GEAR_RATIO = 1 # Gear Ratio

# Ports
BACK_LEFT_DRIVE_MOTOR = Ports.PORT1
BACK_RIGHT_DRIVE_MOTOR = Ports.PORT10
FLYWHEEL_ARM_MOTOR = Ports.PORT4
NMTT_PORT = Ports.PORT5

IMU_SENSOR = Ports.PORT11
GPS_SENSOR = Ports.PORT8

# "Soft Enum" for the flywheel mode
class FlywheelMode:
    STOPPED = "STOPPED"
    LAUNCH = "LAUNCH"
    INTAKE = "INTAKE"
    EXPEL = "EXPEL"

bidding = SmartDrive(
    Motor(BACK_LEFT_DRIVE_MOTOR), # Motor 1
    Motor(BACK_RIGHT_DRIVE_MOTOR), # Motor 2
    Inertial(IMU_SENSOR), # Gyro sensor (IMU)
    WHEEL_TRAVEL, # Wheel travel
    TRACK_WIDTH, # Track width
    WHEEL_BASE, # Wheel base
    MM, # Units
)
nmtt = Motor(NMTT_PORT, GearSetting.RATIO_6_1, True) # Never Meant to Throw
fly_arm = Motor(FLYWHEEL_ARM_MOTOR, GearSetting.RATIO_36_1)

RoE = Controller() # Ruler of Everything
current_flywheel_mode = FlywheelMode.STOPPED

nmtt.set_stopping(COAST)
nmtt.set_max_torque(100, PERCENT)
fly_arm.set_stopping(HOLD)

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

def print_error(error: str):
    """
    Line 3 is used for errors on the controller screen. This
    will print something there.
    """
    RoE.screen.clear_row(3)
    RoE.screen.set_cursor(3, 0)
    RoE.screen.print(error)

def driver_control():
    """
    Code for the driver control period.
    This mainly handles the controller input.
    """
    RoE.screen.clear_screen()
    current_time = time.time()

    while True:
        # Control the sticks

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
            nmtt.spin(FORWARD, 75, PERCENT)

        elif current_flywheel_mode == FlywheelMode.EXPEL:
            nmtt.spin(REVERSE, 50, PERCENT)

        elif current_flywheel_mode == FlywheelMode.INTAKE:
            nmtt.spin(FORWARD, 50, PERCENT)

        elif current_flywheel_mode == FlywheelMode.STOPPED:
            nmtt.stop(COAST)

        else:
            # This should not be a thing that can happen
            print_error("INVALID NMTT STATE: {0}".format(current_flywheel_mode))

        # Control the Flywheel arm
        if RoE.buttonR2.pressing():
            fly_arm.spin(FORWARD)

        elif RoE.buttonR1.pressing():
            fly_arm.spin(REVERSE)

        else:
            fly_arm.stop(BRAKE)

        # Update the temperature of the flywheel motor on the controller every 3 seconds
        if time.time() - current_time >= 3:
            RoE.screen.clear_row(2)
            RoE.screen.set_cursor(2, 0)
            RoE.screen.print("NMTT Temp: ", nmtt.temperature(TemperatureUnits.FAHRENHEIT))

            current_time = time.time()

def set_intake():
    fly_arm.spin_to_position(60, DEGREES)

def auto_defense():
    # Face the left side of the blue or red goal
    bidding.drive_for(24, INCHES)
    bidding.turn_for(LEFT, 90, DEGREES)
    bidding.drive_for(12, INCHES)
    bidding.turn_for(RIGHT, 90, DEGREES)

    # Expel the triball into the goal, hopefully
    nmtt.spin_for(REVERSE, 1, SECONDS)

    # Turn around and grab a triball from the match load zone
    bidding.turn_for(RIGHT, 180, DEGREES)
    bidding.drive_for(FORWARD, 2, INCHES) # Make sure we're contacting the MLZ
    nmtt.spin_for(FORWARD, 1, SECONDS) # Get triball from MLZ

    # Move robot to elevation bars
    bidding.turn_for(LEFT, 45, DEGREES)
    bidding.drive_for(FORWARD, 24, INCHES)
    bidding.turn_for(LEFT, 45, DEGREES)
    bidding.drive_for(FORWARD, 24, INCHES)

    # Expel the loaded triball
    nmtt.spin_for(REVERSE, 1, SECONDS)

    # Elevate the flywheel arm
    fly_arm.spin_to_position(405, DEGREES)
    bidding.drive_for(FORWARD, 2, INCHES) # Touch the elevation bar


def auto_offense():
    # put triball into goal to line up to grab ball from neutral zone
    bidding.drive_for(48, INCHES)        #moves 2 tiles toward the middle
    bidding.turn_for(RIGHT, 90, DEGREES) #lines up to goal
    
    #scores triball
    nmtt.spin_for(REVERSE, 1, SECONDS)

    #makes for certain the triball has gone into the goal
    for i in range(2):
        bidding.drive_for(FORWARD, 8, INCHES)
        if i == 0:
            bidding.drive_for(REVERSE, 8, INCHES)
        else:
            bidding.drive_for(REVERSE, 24, INCHES)
    

selected_auto = auto_defense
chosen = False

def start_competition():
# Register change_flywheel_mode to the B button
    RoE.buttonB.pressed(change_flywheel_mode)
    RoE.buttonY.pressed(set_intake)
    RoE.buttonA.pressed(lambda: print("Hello"))

    Competition(driver_control, auto_defense)


def auto_selector():
    """
    Select the autonomous method to use before
    the match starts.
    """
    RoE.screen.clear_screen()

    def draw_choices():
        RoE.screen.clear_screen()
        
        RoE.screen.set_cursor(1, 0)
        RoE.screen.print("> DEFENSE" if chosen is False else "DEFENSE")
        RoE.screen.set_cursor(2, 0)
        RoE.screen.print("> OFFENSE" if chosen is True else "OFFENSE")

    def toggle_chosen():
        global chosen
        chosen = not chosen
        
        draw_choices()

    def submit():
        global selected_auto
        selected_auto = auto_defense if chosen is False else auto_offense

        RoE.screen.clear_screen()
        RoE.screen.set_cursor(1, 0)
        RoE.screen.print("READY")
        RoE.screen.set_cursor(2, 0)
        RoE.screen.print("Auto: {0}".format("OFFENSE" if chosen else "DEFENSE"))
        start_competition()

    draw_choices()
    RoE.buttonUp.pressed(toggle_chosen)
    RoE.buttonA.pressed(submit)


auto_selector()
# start_competition()
