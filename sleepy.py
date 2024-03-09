
import subprocess
import win32api
import sys
import time

from pynput import keyboard

SLEEP_AFTER_MINUTES = 15  # amount of minutes of inactivity before triggering shutdown
SLEEP_DELAY_SEC = 5  # check interval
DO_HIBERNATE = False
DEBUG = True  # print status icons while running

KEEP_AWAKE_STRINGS = [
    'display request',
    'non-display request'
]


def check_powercfg():
    # get the output of 'powercfg /requests'
    output = subprocess.check_output(['powercfg', '/requests']).decode()
    return not any(string in output for string in KEEP_AWAKE_STRINGS)


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
        sleepy = check_powercfg()

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
