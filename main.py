#!/usr/bin/python3

from os import path

# NUT UPS to monitor
UPS_NAME = "SMT1500RM2U-1"
NUT_HOST = "10.50.200.50"
NUT_PORT = "3493"

# Times
POLL_INTERVAL_S = 1     # NUT poll interval
SCHEDULE_TIME_M = 5     # Time to wait before shutting down after reaching normal threshold
CRITICAL_TIME_M = 1     # Time to wait before shutting down after reaching critical threshold

# Normal thresholds, set to None to disable
SCHEDULE_VOLTAGE = None     # Normal voltage threshold
SCHEDULE_RUNTIME = None     # Normal runtime threshold
SCHEDULE_PERCENT = None     # Normal battery percentage threshold

# Critical thresholds, set to None to disable
CRITICAL_VOLTAGE = None     # Critical voltage threshold
CRITICAL_RUNTIME = None     # Critical runtime threshold
CRITICAL_PERCENT = None     # Critical battery percentage threshold

# Other constants
SCRIPT_DIR = path.normpath(path.dirname(__file__))
LOG_FILE = f'{SCRIPT_DIR}/loggers.log'
NOTIFY_SCRIPT = f'{SCRIPT_DIR}/notify.sh'

def log():
    pass

def notify():
    pass

def poll():
    pass

def main():
    pass

if __name__ == '__main__':
    main()