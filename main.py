#!/usr/bin/python3

from os import path
from datetime import datetime
from time import sleep, time
from subprocess import run, PIPE

# NUT UPS to monitor
UPS_NAME = "SMT1500RM2U-1"
NUT_HOST = "10.50.200.50"
NUT_PORT = "3493"

# Times
POLL_INTERVAL_S = 1     # NUT poll interval
REGULAR_TIME_S = 30   # Time to wait before shutting down after reaching normal threshold
CRITICAL_TIME_S = 5    # Time to wait before shutting down after reaching critical threshold

# Thresholds to schedule shutdowns at
# Set to None to disable threshold
THRESHOLDS = {
    'regular': {
        'voltage': None,
        'runtime': 3600,
        'charge': 50
    },
    'critical': {
        'voltage': None,
        'runtime': 600,
        'charge': 10
    }
}

# Other constants
UPSC_KEYS = {
    'voltage': 'battery.voltage',
    'runtime': 'battery.runtime',
    'charge': 'battery.charge'
}
SCRIPT_DIR = path.normpath(path.dirname(__file__))  # Location of this script
LOG_FILE = f'{SCRIPT_DIR}/loggers.log'              # Location of log file
NOTIFY_SCRIPT = f'{SCRIPT_DIR}/notify.sh'           # Location of notifier script
NOTIFY_TITLE = 'NUT Shutdown Scheduler'             # Title to use for notifications

def log(data):
    try:
        # Add time to log message
        now = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
        line = f'{now} - {data}'

        # Print line
        print(line)
        # Write line
        with open(LOG_FILE, 'a') as f:
            f.write(line + '\n')
    except Exception as e:
        raise Exception(f'Failed to log: {e}')

def notify(data):
    try:
        # Run notify script
        proc = run([NOTIFY_SCRIPT, NOTIFY_TITLE, data], stdout=PIPE, stderr=PIPE)
        # Check for success
        if proc.returncode != 0:
            stderr = proc.stderr.decode('utf-8')
            raise Exception(f'Non-zero exit code: {stderr}')
    except Exception as e:
        raise Exception(f'Failed to send notification: {e}')

def notify_and_log(data):
    try:
        log(data)
        notify(data)
    except Exception as e:
        raise Exception(f'Failed to notify and log: {e}')

def poll():
    try:
        # Run UPS client command
        proc = run(['upsc', f'{UPS_NAME}@{NUT_HOST}:{NUT_PORT}'], stdout=PIPE, stderr=PIPE)

        # Check exit code
        if proc.returncode != 0:
            stderr = proc.stderr.decode('utf-8')
            raise Exception(f'Non-zero exit code: {stderr}')
        else:
            stdout = proc.stdout.decode('utf-8').strip()
            dump_obj = {}
            result_obj = {}

            # Parse upsc output into dict
            for line in stdout.split('\n'):
                [key, value] = line.split(': ')
                dump_obj[key] = value

            # Filter out the relevant fields
            for field in UPSC_KEYS:
                key = UPSC_KEYS[field]
                result_obj[field] = dump_obj[key] if key in dump_obj else None

            # Return relevant dict values
            return result_obj
    except Exception as e:
        raise Exception(f'Failed to poll NUT server: {e}')

def is_below_threshold(thresholds, values):
    # Loop over threshold keys
    for key in thresholds:
        threshold = thresholds[key]
        # Check if value for threshold is below or at threshold
        if threshold is not None:
            if float(values[key]) <= float(threshold):
                return True
    return False

def is_below_critical_threshold(values):
    # Check critical thresholds
    return is_below_threshold(THRESHOLDS['critical'], values)

def is_below_regular_threshold(values):
    # Check regular thresholds
    return is_below_threshold(THRESHOLDS['regular'], values)

def get_scheduled_shutdown_time():
    try:
        # Get current timestamp
        now = time()
        # Poll NUT server
        polled = poll()
        print(polled)
        
        # Check for thresholds
        if is_below_critical_threshold(polled):
            return now + CRITICAL_TIME_S
        elif is_below_regular_threshold(polled):
            return now + REGULAR_TIME_S
        else:
            return None
    except Exception as e:
        raise Exception(f'Failed to calculate scheduled shutdown time: {e}')

def shutdown():
    try:
        # Run shutdown command
        proc = run(['echo', 'shutdown', '0'], stdout=PIPE, stderr=PIPE)
        # Check for success
        if proc.returncode != 0:
            stderr = proc.stderr.decode('utf-8')
            raise Exception(f'Non-zero exit code: {stderr}')
    except Exception as e:
        raise Exception(f'Failed to initiate shutdown: {e}')

shutdown_at = None

try:
    if __name__ == '__main__':
        while 1:
            try:
                # If past scheduled shutdown time, shutdown now
                if shutdown_at is not None and time() >= shutdown_at:
                    notify_and_log('Shutting down now!')
                    shutdown()
                else:
                    # Get time when to shutdown
                    new_shutdown_at = get_scheduled_shutdown_time()

                    # If shouldn't shutdown
                    if new_shutdown_at is None:
                        # Cancel shutdown if scheduled
                        if shutdown_at is not None:
                            notify_and_log('Above threshold: cancelling shutdown!')
                            shutdown_at = None
                    # If should shutdown
                    else:
                        # schedule shutdown if not scheduled yet
                        if shutdown_at is None:
                            notify_and_log(f'Below threshold: sheduling shutdown in {round(new_shutdown_at - time())}s')
                            shutdown_at = new_shutdown_at
                        # If already scheduled, compare schedules
                        else:
                            # Use earlier time
                            if new_shutdown_at < shutdown_at:
                                notify_and_log(f'Updating scheduled shutdown in {round(new_shutdown_at - time())}s')
                                shutdown_at = min(shutdown_at, new_shutdown_at)
            except Exception as e:
                notify_and_log(f'Error: {e}')
            finally:
                sleep(POLL_INTERVAL_S)
except Exception as e:
    print(f'Something really went wrong: {e}')