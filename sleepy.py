
import subprocess
import re
import win32api
import sys
import time

from pynput import keyboard

SLEEP_AFTER_MINUTES = 10
SLEEP_DELAY_SEC = 5


def parse_powercfg():
    # parses the output of 'powercfg /requests' and returns a dictionary of the following format:
    '''
    {'ACTIVELOCKSCREEN': [],
    'AWAYMODE': [],
    'DISPLAY': [],
    'EXECUTION': [],
    'PERFBOOST': [],
    'SYSTEM': [['[DRIVER] Legacy Kernel Caller']]}
    '''

    # get the output of 'powercfg /requests'
    output = subprocess.check_output(['powercfg', '/requests']).decode()

    data = {}

    for line in output.splitlines():
        if match := re.match(r'^(\w+)\:$', line):
            key = match.group(1)
            data[key] = []
            line_count = 0
            sub_array = []
        elif line and line != 'None.':
            if line_count == 0:
                data[key].append(sub_array)
            if line_count < 2:
                sub_array.append(line)
                line_count += 1
            else:
                sub_array = []
                data[key].append(sub_array)
                sub_array.append(line)
                line_count = 1

    return data


ignore_strings = ['An audio stream is currently in use', 'Legacy Kernel Caller']


def main():
    globals()['key_pressed'] = False

    def on_press(key):
        globals()['key_pressed'] = True

    # Start the keyboard listener.
    listener = keyboard.Listener(on_press=on_press)
    listener.start()

    counter = 0

    last_mouse_pos = win32api.GetCursorPos()

    while True:
        sleepy = True
        data = parse_powercfg()

        for key, value in data.items():
            # any of the keys ACTIVELOCKSCREEN, EXECUTION, PERFBOOST, AWAYMODE, DISPLAY, SYSTEM is active
            if key != 'SYSTEM' and len(value) > 0:
                sleepy = False

            # SYSTEM section has only one of the values below
            if key == 'SYSTEM':
                for sub_value in value:
                    # check if none of the strings in ignore_strings are in the joined_value
                    if not any(x in ''.join(sub_value) for x in ignore_strings):
                        sleepy = False
                    else:
                        sleepy = True

        # if mouse has moved, don't sleep
        cursor_pos = win32api.GetCursorPos()
        if last_mouse_pos != cursor_pos:
            sleepy = False
            last_mouse_pos = cursor_pos

        # detect keyboard presses
        if globals()['key_pressed']:
            sleepy = False
            globals()['key_pressed'] = False

        if not sleepy:  # reset counter
            counter = 0
            print('⚙️', end='')

        else:  # increment counter
            if counter > 0:
                print('💤', end='')
            counter += 1

        sys.stdout.flush()

        # this much seconds without waking entries
        if counter == SLEEP_AFTER_MINUTES * 60 / SLEEP_DELAY_SEC:
            subprocess.run(r'rundll32.exe powrprof.dll, SetSuspendState Sleep', shell=True)
            counter = 0

        time.sleep(SLEEP_DELAY_SEC)


main()
