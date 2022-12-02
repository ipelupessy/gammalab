from ..service import ThreadService, ReceivingService
from ..wire import FloatWire, HistogramWire

import numpy
import time

class Monitor(ThreadService, ReceivingService):
    input_wire_class=FloatWire

    def __init__(self, window=5, vmin=-0.01, vmax=1.1, outfile=None):                
        self.window=window
        self.vmin=vmin
        self.vmax=vmax
        self.outfile=outfile
        self.do_update=True

        super(Monitor, self).__init__()
        self.thread.daemon=True

    def update_plot(self,nframe):

        if self.do_update==False:
            return self.plot

        data=[]
        while True:
            _data=self.receive_input(False)
            if _data is None:
                break
            data.append(_data)

        if data:
            data=numpy.concatenate(data)
        else:
            return self.plot

        if self.stopped:
            self.do_update=False
            if self.outfile is not None:
              self.fig.savefig(self.outfile+'.png')
            self.done=True
            return self.plot
        
        while len(data)>0:
          
            n=min(len(data),len(self.plotdata)-self.nplot)
            
            self.plotdata[self.nplot:self.nplot+n]=data[:n]
            data=data[n:]
            self.nplot=(self.nplot+n) % len(self.plotdata)
                            
        self.plot[0].set_ydata(self.plotdata)
        return self.plot
  
    def start_process(self):
        global FuncAnimation, pyplot
        try:
            from matplotlib.animation import FuncAnimation
            from matplotlib import pyplot    
        except Exception as ex:
            self.print_message("import error: {0}".format(str(ex)))

        self.plotdata=numpy.zeros(int(self.input_wire.RATE*self.window), dtype=self.input_wire.FORMAT)
        self.plotx=numpy.arange(int(self.input_wire.RATE*self.window))/float(self.input_wire.RATE)

        self.fig, self.ax = pyplot.subplots()
        self.fig.canvas.manager.set_window_title("GammaLab Monitor")

        self.ax.cla()
        self.plot=self.ax.plot(self.plotx,self.plotdata)
        self.ax.set_ylim(self.vmin,self.vmax)
        self.ax.set_xlabel("time (s)")
        self.ax.set_ylabel("level")
      
        self.nplot=0

        ani = FuncAnimation(self.fig, self.update_plot, interval=250, repeat=False, blit=True)

        pyplot.show(block=True)

        if self.outfile is not None:
            self.fig.savefig(self.outfile+'.png')

        self.cleanup()
        
    def close(self):
        # deamon process
        self.stop()

        while not self.done:
            time.sleep(0.1)
      

class PlotHistogram(ThreadService, ReceivingService):
    input_wire_class=HistogramWire
  
    def __init__(self, xmin=0, xmax=1., log=True, 
                    error_bars=True, outfile="histogram"):        
        self.xmin=xmin
        self.xmax=xmax
        self.log=log
        self.error_bars=error_bars
        self.outfile=outfile
        self.ymax=1.
        self.do_update=True

        super(PlotHistogram, self).__init__()
        self.thread.daemon=True

    def update_plot(self,nframe):
        
        data=None
        while True:
            _data=self.receive_input(False)
            if _data is None:
                break
            data=_data

        if self.stopped or not self.do_update or data is None:
            if self.stopped:
                self.do_update=False
                if self.outfile is not None:
                  self.fig.savefig(self.outfile+'.png')
                self.done=True
          
            if self.error_bars:
                return self._line,self._top,self._bot
            else:
                return self._line,

        hist=data["hist"]
        bins=data["bins"]

        return self.update_histogram_plot(hist,bins)

    def update_histogram_plot(self, hist, bins):
        y=numpy.zeros(2*len(hist))
        y[::2]=hist
        y[1::2]=hist
        yerr=y**0.5
        self._line.set_ydata(y)
        self._update_ylim(y.max())
        if self.error_bars:
            self._top.set_ydata(numpy.maximum(y+yerr,1))
            self._bot.set_ydata(y-yerr)
                
        if self.error_bars:
            return self._line,self._top,self._bot
        else:
            return self._line,

    def _update_ylim(self,ymax):
        if self.log:
            _ymax=ymax
            if _ymax>self.ymax:
                self.ymax=10*_ymax
                self.ax.set_ylim(0.5,2*self.ymax)
        else:
            _ymax=ymax
            if _ymax>self.ymax:
                self.ymax=1.5*ymax
                self.ax.set_ylim(0,1.3*self.ymax)      

    def _histogram_plot(self):
        self.ax.cla()
        nchannels=self.input_wire.nchannels
        vmin=self.input_wire.vmin
        vmax=self.input_wire.vmax
        hist,bins=numpy.histogram([], bins=nchannels, range=(vmin,vmax))
        x=numpy.zeros(2*nchannels)
        y=numpy.zeros(2*nchannels)
        x[::2]=bins[:-1]
        x[1::2]=bins[1:]
        y[::2]=hist
        y[1::2]=hist
        if self.error_bars:
            yerr=y**0.5
            self._top,=self.ax.plot(x,numpy.maximum(y+yerr,1),":",c="tab:orange", zorder=0)
            self._bot,=self.ax.plot(x,y-yerr,":",c="tab:orange",zorder=5)
        if self.log:
            self._line,=self.ax.semilogy(x,y+0.1, lw=2, zorder=10)
        else:
            self._line,=self.ax.plot(x,y,lw=2, zorder=10)

        self.ax.set_ylabel("counts")
        self.ax.set_xlabel(f"energy ({self.input_wire.unit})") # take label from wire?
        self.ax.set_xlim(self.xmin,self.xmax)
        self._update_ylim(max(y.max(),50))
      
    def start_process(self):
        global FuncAnimation, pyplot
        try:
            from matplotlib.animation import FuncAnimation
            from matplotlib import pyplot    
        except Exception as ex:
            self.print_message("import error: {0}".format(str(ex)))

        self.fig, self.ax = pyplot.subplots()
        self.fig.canvas.manager.set_window_title("GammaLab Histogram")
      
        self._histogram_plot()

        ani = FuncAnimation(self.fig, self.update_plot, interval=250, repeat=False, blit=True)

        pyplot.show(block=True)
                
        if self.outfile is not None:
            self.fig.savefig(self.outfile+'.png')

        self.cleanup()

    def close(self):
        # deamon process
        self.stop()

        while not self.done:
            time.sleep(0.1)

