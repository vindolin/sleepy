import subprocess
import sys
import tempfile
import time

import win32api

from pynput import keyboard

SLEEP_AFTER_MINUTES = 15  # amount of minutes of inactivity before triggering shutdown
CHECK_LOOP_INTERVAL = 60  # check interval seconds
DO_HIBERNATE = False
DEBUG = False  # print status icons while running

# this script checks the output of 'powercfg /requests' and looks for the following strings:
KEEP_AWAKE_STRINGS = [
    'display request',
    'non-display request'
]


def check_powercfg():
    # get the output of 'powercfg /requests'
    process = subprocess.Popen(['powercfg', '/requests'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=subprocess.CREATE_NO_WINDOW)
    output, _ = process.communicate()
    output = output.decode()
    return not any(string in output for string in KEEP_AWAKE_STRINGS)


last_debug_time = time.time()


def write_log(text):
    with open(f'{tempfile.gettempdir()}\\sleepy.log', 'ab') as f:
        f.write(f'{time.time()}: {text}\n'.encode())


def print_char(char):
    print(char, end='')


def main():
    write_log('Starting sleepy')

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
            DEBUG and print_char('⚙️')

        else:  # increment counter
            if counter > 0:
                DEBUG and print_char('💤')
            counter += 1

        if DEBUG:
            try:
                sys.stdout.flush()
            except AttributeError:
                pass  # there's no stdout when started with pythonw

        # this much seconds without waking entries
        if counter == SLEEP_AFTER_MINUTES * 60 / CHECK_LOOP_INTERVAL:
            # hibernate or shutdown
            flag = 'h' if DO_HIBERNATE else 'd'
            subprocess.run(f'psshutdown.exe -{flag}', shell=True)
            counter = 0

        time.sleep(CHECK_LOOP_INTERVAL)


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        write_log(f'Error occured at {time.strftime("%c")}: {e}'.encode())
        raise
