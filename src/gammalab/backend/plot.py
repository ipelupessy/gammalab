from ..service import ThreadService, ReceivingService
from ..wire import FloatWire, HistogramWire, CountWire, PulseWire

import numpy
import time
import random

class _Plot(ThreadService, ReceivingService):
    def __init__(self, outfile=None, interval=250):                
        super(_Plot, self).__init__()
        self.thread.daemon=True
        self.outfile=outfile
        self.interval=interval
        self.blit=False
        self.do_update=True

    def on_click(self,event):
        if event.button is MouseButton.RIGHT:
            self.do_update=not self.do_update

    def setup_plot(self):
        raise Exception("setup_plot not implemented")

    def update_plot(self, nframe, data=None):
        raise Exception("update_plot not implemented")

    def get_data(self, nframe, data=None):
        raise Exception("get_data not implemented")

    def _update_plot(self, nframe):            
        self.fig.canvas.flush_events()

        if self.done:
            return []
      
        if self.stopped:
            self.do_update=False
            if self.outfile is not None:
                self.fig.savefig(self.outfile+'.png')
            self.done=True
            return []

        data=self.get_data()

        if self.do_update==False or data is None:
            return self.artists

        return self.update_plot(nframe, data)
        
    def start_process(self):
        global FuncAnimation, pyplot, MouseButton
        try:
            from matplotlib.backend_bases import MouseButton
            from matplotlib.animation import FuncAnimation
            from matplotlib import pyplot    
        except Exception as ex:
            self.print_message("import error: {0}".format(str(ex)))
            
        self.fig, self.ax, self.artists=self.setup_plot()

        pyplot.connect('button_press_event', self.on_click)
        
        ani = FuncAnimation(self.fig, self._update_plot, interval=self.interval, blit=self.blit)

        pyplot.show(block=True)

        if self.outfile is not None:
            self.fig.savefig(self.outfile+'.png')

        self.cleanup()
        
    def close(self):
        # deamon process
        self.stop()

        while not self.done:
            time.sleep(0.1)


class Monitor(_Plot):
    input_wire_class=FloatWire

    def __init__(self, window=5, vmin=-0.01, vmax=1.1, outfile=None):                
        super(Monitor, self).__init__(outfile=outfile)
        self.window=window
        self.vmin=vmin
        self.vmax=vmax
        self.blit=True

    def get_data(self):
        data=[]
        while True:
            _data=self.receive_input(False)
            if _data is None:
                break
            data.append(_data)

        if data:
            data=numpy.concatenate(data)
        else:
            data=None
        
        return data

    def update_plot(self,nframe, data):

        while len(data)>0:          
            n=min(len(data),len(self.plotdata)-self.nplot)
            
            self.plotdata[self.nplot:self.nplot+n]=data[:n]
            data=data[n:]
            self.nplot=(self.nplot+n) % len(self.plotdata)
                            
        self.artists[0].set_ydata(self.plotdata)
        return self.artists
  
    def setup_plot(self):
        self.plotdata=numpy.zeros(int(self.input_wire.RATE*self.window), dtype=self.input_wire.FORMAT)
        self.plotx=numpy.arange(int(self.input_wire.RATE*self.window))/float(self.input_wire.RATE)

        fig, ax = pyplot.subplots(figsize=(8,4))
        fig.canvas.manager.set_window_title("GammaLab Monitor")

        ax.cla()
        lines=ax.plot(self.plotx,self.plotdata)
        ax.set_ylim(self.vmin,self.vmax)
        ax.set_xlabel("time (s)")
        ax.set_ylabel("level")
      
        self.nplot=0
        
        return fig,ax,lines
        
class PlotHistogram(_Plot):
    input_wire_class=HistogramWire
  
    def __init__(self, xmin=0, xmax=1., log=True, 
                    error_bars=True, outfile="histogram"):        
        super(PlotHistogram, self).__init__(outfile=outfile)
        self.xmin=xmin
        self.xmax=xmax
        self.log=log
        self.error_bars=error_bars
        self.ymax=1.

    def get_data(self):        
        data=None
        while True:
            _data=self.receive_input(False)
            if _data is None:
                break
            data=_data
 
        return data

    def update_plot(self,nframe, data):

        hist=data["hist"]
        bins=data["bins"]

        y=numpy.zeros(2*len(hist))
        y[::2]=hist
        y[1::2]=hist
        yerr=y**0.5
        self._line.set_ydata(y)
        self._update_ylim(y.max())
        if self.error_bars:
            self._top.set_ydata(numpy.maximum(y+yerr,1))
            self._bot.set_ydata(y-yerr)
                
        return self.artists

    def _update_ylim(self,ymax, ax=None):
        if ax is None:
            ax=self.ax
        if self.log:
            _ymax=ymax
            if _ymax>self.ymax:
                self.ymax=10*_ymax
                ax.set_ylim(0.5,2*self.ymax)
                pyplot.draw()
        else:
            _ymax=ymax
            if _ymax>self.ymax:
                self.ymax=1.5*ymax
                ax.set_ylim(0,1.3*self.ymax)      
                pyplot.draw()

    def setup_plot(self):
        fig, ax = pyplot.subplots()
        fig.canvas.manager.set_window_title("GammaLab Histogram")
        ax.cla()
        
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
            self._top,=ax.plot(x,numpy.maximum(y+yerr,1),":",c="tab:orange", zorder=0)
            self._bot,=ax.plot(x,y-yerr,":",c="tab:orange",zorder=5)
        if self.log:
            self._line,=ax.semilogy(x,y+0.1, lw=2, zorder=10)
        else:
            self._line,=ax.plot(x,y,lw=2, zorder=10)

        ax.set_ylabel("counts")
        ax.set_xlabel(f"energy ({self.input_wire.unit})") # take label from wire?
        ax.set_xlim(self.xmin,self.xmax)
        self._update_ylim(max(y.max(),50), ax=ax)
        
        if self.error_bars:
            artists=[self._line, self._top, self._bot]
        else:
            artists=[self._line]
        
        return fig,ax,artists
      
class CountPlot(_Plot):
    input_wire_class=CountWire

    def __init__(self, outfile=None):                
        super(CountPlot, self).__init__(outfile=outfile)
        self.time=[]
        self.count=[]
        self.blit=False

    def get_data(self):
        data=[]
        while True:
            _data=self.receive_input(False)
            if _data is None:
                break
            data.append(_data)
        if data:
            return data
        else:
            return None
        

    def update_plot(self,nframe, data):
        self.time.extend([x[0] for x in data])
        self.count.extend([x[1] for x in data])
        
        self.ax.set_xlim(0,2**numpy.ceil(numpy.log2((max(self.time)+1.))))
        self.ax.set_ylim(0,2*max(self.count))

        self.artists[0].set_xdata(self.time)
        self.artists[0].set_ydata(self.count)
                
        return self.artists
  
    def setup_plot(self):
        fig, ax = pyplot.subplots()
        fig.canvas.manager.set_window_title("GammaLab Counts")

        ax.cla()
        artists=ax.plot(self.time,self.count)
        ax.set_xlabel("time (s)")
        ax.set_ylabel("counts per sec")
        ax.set_xlim(0,10)
        ax.set_ylim(0,30)

        return fig,ax,artists

class PulsePlot(_Plot):
    input_wire_class=PulseWire

    def __init__(self, nplot=1):                
        super(PulsePlot, self).__init__()
        self.nplot=nplot

    def get_data(self):
        data=[]
        while True:
            _data=self.receive_input(False)
            if _data is None:
                break
            data.append(_data)

        if data:
            return data
        else:
            return None

    def update_plot(self,nframe, data):

        self.process(data)
            
        return self.update_plot_data()

    def process(self,data):      
      
        _data=None
        for d in data:
            if _data is None:
                _data=d
            else:
                _data["pulses"].extend(d["pulses"])
                assert _data["rate"]==d["rate"]
                if d["total_time"]>_data["total_time"]:
                    _data["total_time"]=d["total_time"]
                _data["dtime"]+=d["dtime"]
      
        pulses=_data["pulses"]
        
        if pulses and len(pulses[0])<5:
            self.print_message("PulseWire does not contain pulse shape")
        
        for i,p in enumerate(random.sample(pulses, k=min(self.nplot, len(pulses)))):
            self.data[i]=p[4]
  
    def update_plot_data(self):
        dmin=9999
        dmax=-9999
        tmin=9999
        tmax=-9999
        for d,line in zip(self.data, self.lines):
            time=(numpy.arange(0,len(d))-5)
            line.set_data(time,d)                  
            
            tmin=min(tmin,time.min())
            tmax=max(tmax,time.max())
            
            dmin=min(dmin,d.min())
            dmax=max(dmax,d.max())

        self.ax.set_xlim(tmin,tmax)
        self.ax.set_ylim(dmin-.1*(dmax-dmin),dmax+0.2*(dmax-dmin))

        return self.lines[0:len(self.data)]
            
    def setup_plot(self):
        fig, ax = pyplot.subplots(figsize=(8,4))
        fig.canvas.manager.set_window_title("GammaLab Pulse Monitor")

        self.data=[numpy.array([0]*10)]*self.nplot

        self.lines=[]        
        for d in self.data:
            t=(numpy.arange(0,len(d))-5)
            line,=ax.plot(t,d,"o-")
            self.lines.append(line)

        ax.set_xlabel("time (samples)")
        ax.set_ylabel("level")
        #~ ax.set_title("selected pulses")
        
        artists=self.lines
        
        return fig,ax,artists
