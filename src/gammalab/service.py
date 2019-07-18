from . import all_services

import threading

class ServiceError(Exception):
    pass

class Service(object):
    def __init__(self):
        all_services.add(self)
      
    def start(self):
        raise Exception("not implemented for %s"%str(self))
    def stop(self):
        raise Exception("not implemented for %s"%str(self))
    def close(self):
        raise Exception("not implemented for %s"%str(self))
    def plugs_into(self, other):
        raise ServiceError("service %s has no outputs"%str(self))
    def connect_to(self, other):
        raise ServiceError("service %s has no inputs"%str(self))

class SourceService(Service):
    def __init__(self):
        Service.__init__(self)
        self.wires=[]

    def send_output(self,data):
        for w in self.wires:
            try:
                w.put_nowait(data)
            except:
                print("%s buffer full"%str(self))

    def plugs_into(self, other):
        try:
          other.connect_input(self)
        except ServiceError as ex:
          raise ex          
        except Exception as ex:
          print ex
          raise Exception("trying to connect incompatible services")
        
class ReceivingService(Service):
    def __init__(self):
        Service.__init__(self)
    def connect_input(self):
        raise Exception("not implemented")
    def receive_input(self, block=True):
        return self.input_wire.get(block, 2)

# multiple input/outputs will be implemented by connecting to/from special attributes:
# s1.output1.plugs_into(s2)

class ThreadService(object):
    def __init__(self):
        self.stopped=True
        self.done=False
        self.thread=threading.Thread(target=self._process)

    def start(self):
        if not self.thread.is_alive():
            self.thread.start()
        self.stopped=False

    def _process(self):
        raise Exception("not implemented")

    def stop(self):
        self.stopped=True

    def close(self):
        self.stop()
        self.done=True
        self.thread.join()
