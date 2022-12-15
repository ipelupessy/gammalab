from . import all_services, shared_output

import multiprocessing
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

    t=threading.Thread(target=output_thread, name="output")
    t.daemon=True
    t.start()

    for s in all_services:
        s.start()

def shutdown():
    if all_services:
        shared_output.put("[Shutdown] shutting down")

    for s in all_services:
          s.stop()

    while all_services:
        s=all_services.pop()
        try:
          s.close()
        except Exception as ex:
          shared_output.put("[Shutdown] "+str(ex))

    shared_output.put("[Shutdown] done")

    time.sleep(0.5)

def check_user_input():
    input()

def main(timeout=None):

    startup()

    shared_output.put("[Main] running")

    input_checker=threading.Thread(target=check_user_input)
    input_checker.daemon=True
    input_checker.start()
    input_checker.join(timeout)    
    
    shutdown()
    
    
