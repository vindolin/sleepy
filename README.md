# - WORK IN PROGRESS -

## Windows Daemon process that checks if the computer wasn't in use for n minutes and then put it into standby.

Do an internet search for "windows won't go to sleep" and you know why I made this.

It checks the output powercfg /requests for processes that should prevent the computer from going to sleep.

It also checks mouse and keyboard events to see if the user is using the computer.

If these checks all pass, it will put the computer to sleep.

The time to sleep is configurable through the SLEEP_AFTER_MINUTES constant.
