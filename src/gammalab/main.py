from . import all_services

from threading import Timer
import time
try:
    input=raw_input
except:
    pass

def startup():
    print("startup")

    for s in all_services:
        s.start()

def shutdown():
    if all_services:
        print("shutting down")

    while all_services:
        s=all_services.pop()
        try:
          s.stop()
          s.close()
        except Exception as ex:
          print(ex)

    exit(0)

def main(timeout=None):

    startup()

    if timeout is not None:
        timer=Timer(timeout, shutdown)
        timer.daemon=True
        timer.start()
        
    print("running")
    input()

    shutdown()
    
    
