from . import all_services

def main():
    print(all_services)

    for s in all_services:
        s.start()
        
    print("running")
    raw_input()
    
    for s in all_services:
        s.stop()
        s.close()
