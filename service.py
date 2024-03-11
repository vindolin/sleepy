import threading
import win32serviceutil
import win32service
import win32event
import servicemanager
import socket

import sleepy


class AppServerSvc (win32serviceutil.ServiceFramework):
    _svc_name_ = "Sleepy"
    _svc_display_name_ = "Sleepy Service"

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        socket.setdefaulttimeout(60)

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)

    def SvcDoRun(self):
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                              servicemanager.PYS_SERVICE_STARTED,
                              (self._svc_name_, ''))
        self.is_alive = True
        threading.Thread(target=self.main).start()

    def main(self):
        # Your business logic or call to any class should be here
        # this time it creates a text.txt and writes Test Service in a daily manner
        sleepy.main()


if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(AppServerSvc)
