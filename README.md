# - WORK IN PROGRESS -

## Windows daemon process that checks if the computer has not been used for n minutes and then puts it into standby mode.

Do an internet search for "windows won't go to sleep" and you know why I made this 😠.

It checks the output of ```powercfg /requests``` for processes that should prevent the computer from going to sleep.

It also checks mouse and keyboard events to see if the user is using the computer.

If none of this is detected, the computer is put into standby using `psshutdown.exe -d`.

The time to sleep is configurable through the SLEEP_AFTER_MINUTES constant.

### Installation
This script needs the tool [psshutdown.exe](https://learn.microsoft.com/en-us/sysinternals/downloads/psshutdown) from the Windows Sysinternals suite to put the computer into standby.

The only python dependency is pynput (for checking keyboard/mouse activity).

```
pip install pynput
```

> [!IMPORTANT]
This script needs to be run in administrator mode because ```powercfg /requests``` doesn't work as normal user.

#### It can be automatically started using the Windows Task Scheduler

- Open Task scheduler
- Click on "Create Task"
- Name it "Sleepy"
- Check "Run with highest privileges"
- Check "hidden"

#### Triggers
- In the Triggers tab click on "New..."
- In the "Begin the task" dropdown choose "On connection to user session"
- Select "Connection from local computer"
- Uncheck "Stop task if it runs longer than"

#### Actions
- In the Actions tab click on "New..."
- In the "Start a program" dropdown choose "Start a program"
- In the "Program/script" field enter the path to your "pythonw.exe"
- In the "Add arguments (optional)" field enter the path to your "sleepy.py"
