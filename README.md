# - WORK IN PROGRESS -

## Windows Daemon process that checks if the computer wasn't in use for n minutes and then put it into standby.

Do an internet search for "windows won't go to sleep" and you know why I made this.

It checks the output powercfg /requests for processes that should prevent the computer from going to sleep.

It also checks mouse and keyboard events to see if the user is using the computer.

If none of this is detected the computer is put into standby using `psshutdown.exe -d`.

The time to sleep is configurable through the SLEEP_AFTER_MINUTES constant.

### Installation
This script needs the tool [psshutdown.exe](https://learn.microsoft.com/en-us/sysinternals/downloads/psshutdown) from the Windows Sysinternals suite to put the computer into standby.

The only python dependency is pynput (for checking keyboard/mouse activity).

```
pip install pynput
```


This script needs to be run in administrator mode.

You can test it in an administrator terminal with:

```
"{path to your python installation}\python.exe" "{path to sleepy.py}"

```
> [!CAUTION]
> I couldn't figure out how to load this script on logon in administrator mode.

Things I tried that didn't work:
- creating a link in %appdata%\Roaming\Microsoft\Windows\Start Menu\Programs\Startup, setting the "run as administrator" checkbox to true. (no process turned up in Task Manager)
- creating a Task Scheduler task that runs on logon with highest privileges. (no process turned up in Task Manager)
- turning the script into a Windows service (testing the service with "python service.py debug works but trying to start it results in the error: ```Starting service Error starting service: The service did not respond to the start or control request in a timely fashion```)

> [!TIP]
> Maybe the new sudo.exe feature in the next Windows release will help...
>
> Suggestions welcome!

<!--

To run the script on login, create a link in:

```
%appdata%\Microsoft\Windows\Start Menu\Programs\Startup
```

Set the Target to:

```
"{path to your python installation}\pythonw.exe" "{path to sleepy.py}"
```

Click Advance and check "Run as administrator"
-->
