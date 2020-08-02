from . import all_services, shared_output

import threading
import time

try:
    input=raw_input
except:
    pass

def output_thread():
    message=None
    while message!="[Shutdown] done":
        message=shared_output.get(True)
        print(message)

def startup():
    print("[Startup] entry")

    t=threading.Thread(target=output_thread)
    t.daemon=True
    t.start()

    for s in all_services:
        s.start()

def shutdown():
    if all_services:
        shared_output.put("[Shutdown] shutting down")

    while all_services:
        s=all_services.pop()
        try:
          s.stop()
          s.close()
        except Exception as ex:
          shared_output.put("[Shutdown] "+str(ex))

    shared_output.put("[Shutdown] done")

    exit(0)

def main(timeout=None):

    startup()

    if timeout is not None:
        timer=threading.Timer(timeout, shutdown)
        timer.daemon=True
        timer.start()
        
    shared_output.put("[Main] running")
    input()

    shutdown()
    
    
