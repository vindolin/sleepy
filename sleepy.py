
import subprocess
import re
import win32api
import sys
import time

from pynput import keyboard

SLEEP_AFTER_MINUTES = 15  # amount of minutes of inactivity before triggering shutdown
SLEEP_DELAY_SEC = 5  # check interval
IGNORE_STRINGS = [  # ignore these strings in SYSTEM section
    'An audio stream is currently in use',
    'Legacy Kernel Caller'
]
DO_HIBERNATE = False

DEBUG = True  # print status icons while running


def parse_powercfg():
    # parses the output of 'powercfg /requests' and returns a dictionary of the following format:
    '''
    {
        'ACTIVELOCKSCREEN': [],
        'AWAYMODE': [],
        'DISPLAY': [],
        'EXECUTION': [],
        'PERFBOOST': [],
        'SYSTEM': [
            ['[DRIVER] Legacy Kernel Caller'], ...]
    }
    '''

    # get the output of 'powercfg /requests'
    output = subprocess.check_output(['powercfg', '/requests']).decode()

    data = {}

    # split the output into lines
    for line in output.splitlines():
        # sections
        if match := re.match(r'^(\w+)\:$', line):
            key = match.group(1)
            data[key] = []
            line_count = 0
            sub_array = []

        # values
        elif line and line != 'None.':
            if line_count == 0:
                data[key].append(sub_array)
            elif line_count < 2:
                sub_array.append(line)
                line_count += 1
            else:
                sub_array = []
                data[key].append(sub_array)
                sub_array.append(line)
                line_count = 1

    return data


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
                    if sub_value == []:
                        continue
                    # check if none of the strings in ignore_strings are in the joined_value
                    elif not any(x in ''.join(sub_value) for x in IGNORE_STRINGS):
                        sleepy = False

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
            DEBUG and print('⚙️', end='')

        else:  # increment counter
            if counter > 0:
                DEBUG and print('💤', end='')
            counter += 1

        sys.stdout.flush()

        # this much seconds without waking entries
        if counter == SLEEP_AFTER_MINUTES * 60 / SLEEP_DELAY_SEC:
            # hibernate or shutdown
            flag = 'h' if DO_HIBERNATE else 'd'
            subprocess.run(f'psshutdown.exe -${flag}', shell=True)
            counter = 0

        time.sleep(SLEEP_DELAY_SEC)


main()
