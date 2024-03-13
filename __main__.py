import subprocess
import sys
import tempfile
import time

from pynput import keyboard, mouse

SLEEP_AFTER_MINUTES = 15  # amount of minutes of inactivity before triggering shutdown
CHECK_LOOP_INTERVAL = 60  # check interval seconds
DO_HIBERNATE = False
DEBUG = True  # print status icons while running

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


def write_log(text, timestamp=True):
    if timestamp:
        text = f'{time.strftime("%Y-%m-%d %H:%M:%S")} {text}\n'
    else:
        text = f'{text}\n'
    with open(f'{tempfile.gettempdir()}\\sleepy.log', 'ab') as f:
        f.write(text.encode())


def print_char(char):
    print(char, end='')


def main():
    key_pressed = False
    mouse_moved = False

    write_log('Starting sleepy')

    def on_key_press(key):
        nonlocal key_pressed
        key_pressed = True

    def on_mouse_move(x, y):
        nonlocal mouse_moved
        mouse_moved = True

    # start keyboard/mouse listeners
    kb_listener = keyboard.Listener(on_press=on_key_press)
    kb_listener.start()
    mouse_listener = mouse.Listener(on_move=on_mouse_move)
    mouse_listener.start()

    counter = 0

    while True:
        sleepy = check_powercfg()

        if mouse_moved or key_pressed:
            sleepy = False

        key_pressed = False
        mouse_moved = False

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
                pass  # there's no stdout when started with pythonw?

        # this much seconds without waking entries
        if counter == SLEEP_AFTER_MINUTES * 60 / CHECK_LOOP_INTERVAL:
            # hibernate or shutdown
            flag = 'h' if DO_HIBERNATE else 'd'
            subprocess.run(f'psshutdown.exe -{flag} -t 0', shell=True)
            write_log('Shutdown triggered')
            counter = 0

        time.sleep(CHECK_LOOP_INTERVAL)


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        write_log(f'Error occured: {e}')
        raise
