from . import all_services

from threading import Timer
import time

def startup():
    #~ print(all_services)
    print("startup")

    for s in all_services:
        s.start()

def shutdown():
    print("shutting down")

    for s in all_services:
        s.stop()
        s.close()
        
    exit(0)

def main(timeout=None):

    startup()

    if timeout is not None:
        print "timer"
        timer=Timer(timeout, shutdown)
        timer.start()
        
    print("running")
    raw_input()

    shutdown()
    
    
