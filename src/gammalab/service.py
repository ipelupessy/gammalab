from . import all_services, shared_output

import multiprocessing
import ctypes
import time

class ServiceError(Exception):
    pass

class Service(object):
    def __init__(self, **kwargs):
        super(Service, self).__init__(**kwargs)
        all_services.add(self)
        self._output=shared_output
    
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
    def print_message(self, message):
        self._output.put('['+self.__class__.__name__+'] '+message)

class SourceService(Service):
    output_wire_class=None

    def __init__(self, **kwargs):
        super(SourceService, self).__init__(**kwargs)
        self.output_wires=[]
        if self.output_wire_class is None:
            raise Exception("SourceService {0} does not specify output_wire_class".format(self))

    def output_protocol(self, wire):
        assert isinstance(wire, self.output_wire_class)

    def connect(self, wire):
        self.output_protocol(wire)
        self.output_wires.append(wire)

    def send_output(self,data):
        for w in self.output_wires:
            try:
                w.put_nowait(data)
            except:
                self.print_message("%s buffer full"%str(self))

    def plugs_into(self, other):
        try:
          other.connect_input(self)
        except ServiceError as ex:
          raise ex      
        except AssertionError as ex:
          self.print_message(str(ex))
          raise Exception("Wiring fault! Trying to connect incompatible services")
        except AttributeError as ex:
          self.print_message(str(ex))
          raise Exception("Wiring fault! Wires connected out of order?")
        
class ReceivingService(Service):
    input_wire_class=None

    def __init__(self, **kwargs):
        super(ReceivingService, self).__init__(**kwargs)
        if self.input_wire_class is None:
            raise Exception("ReceivingService {0} does not specify input_wire_class".format(self))
        self.input_wire=self.input_wire_class()
    def connect_input(self, service):
        service.connect(self.input_wire)
    def receive_input(self, block=True):
        try:
            return self.input_wire.get(block)
        except Exception as ex:
            #~ self.print_message("receive_input timeout or error")
            return None

# multiple input/outputs will be implemented by connecting to/from special attributes:
# s1.output1.plugs_into(s2)

class ThreadService(Service):
    def __init__(self, **kwargs):
        super(ThreadService, self).__init__(**kwargs)
        self.__stopped=multiprocessing.Value(ctypes.c_bool)
        self.__done=multiprocessing.Value(ctypes.c_bool)
        self.stopped=True
        self.done=False
        self.thread=multiprocessing.Process(target=self.start_process, 
                                            name=self.__class__.__name__)

    def start(self):
        self.stopped=False
        if not self.thread.is_alive():
            self.thread.start()

    def start_process(self):
        self._process()
        self.cleanup()

    def _process(self):
        while not self.stopped:
            if hasattr(self,"receive_input"):
                data=self.receive_input()
                if data is None:
                    self.stopped=True
            else:
                data=None

            # if stopped reveive input, but do not process, nor output

            if not self.stopped:
# lets try ignoring exceptions for a while:
                try:
                    data=self.process(data)
                except:
                    data=None

            if hasattr(self,"send_output"):
                if (not self.stopped and 
                    data is not None):  
                    self.send_output(data)
            
        if hasattr(self,"send_output"):
            self.send_output(None)
                    
        self.stopped=True
        
    def cleanup(self):
        self.done=True

    def stop(self):
        self.stopped=True

    def close(self):
        self.stop()

        while not self.done:
            time.sleep(0.1)

        self.thread.terminate()
        self.thread.join()
        self.thread.close()

    @property
    def done(self):
        return self.__done.value

    @done.setter
    def done(self, value):
        self.__done.value=value

    @property
    def stopped(self):
        return self.__stopped.value

    @stopped.setter
    def stopped(self, value):
        self.__stopped.value=value
