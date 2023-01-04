from ..service import ThreadService, ReceivingService
from ..wire import FloatWire, HistogramWire, CountWire, PulseWire

import numpy
import time
import random
import pickle

class _Plot(ThreadService, ReceivingService):
    def __init__(self, outfile=None, interval=250):                
        super().__init__()
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
                outfile=self.outfile+'.png'
                self.fig.savefig(outfile)
                self.print_message(f"Image written to {outfile}")
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
            self.print_message(f"import error: {str(ex)}")
            
        self.fig, self.ax, self.artists=self.setup_plot()

        pyplot.connect('button_press_event', self.on_click)

        
        ani = FuncAnimation(self.fig, self._update_plot, interval=self.interval, blit=self.blit)

        pyplot.show(block=True)

        if self.outfile is not None:
            outfile=self.outfile+'.png'
            self.fig.savefig(outfile)
            self.print_message(f"Image written to {outfile}")

        self.cleanup()
        
    def close(self):
        # deamon process
        self.stop()

        while not self.done:
            time.sleep(0.1)


class Monitor(_Plot):
    input_wire_class=FloatWire

    def __init__(self, window=5, vmin=-0.01, vmax=1.1, outfile=None):                
        super().__init__(outfile=outfile)
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
            data.append(_data["data"])

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
                    error_bars=True, outfile="histogram",
                    background="", yrange=1.e4, time_normalized=False):        
        super().__init__(outfile=outfile)
        self.xmin=xmin
        self.xmax=xmax
        self.log=log
        self.error_bars=error_bars
        self.background=background #"background.histogram.pkl"
        self.yrange=yrange
        self.blit=True
        self.time_normalized=time_normalized

    def get_data(self):        
        data=None
        while True:
            _data=self.receive_input(False)
            if _data is None:
                break
            data=_data
 
        return data

    def convert_hist_bins(self,hist,bins,total_time):
        yerr=hist**0.5
        yerr=numpy.maximum(yerr,1)
        if self.time_normalized:
            hist=hist/total_time
            yerr=yerr/total_time
        if self.input_wire.histogram_mode!="normal":
            binsize=(bins[1:]-bins[:-1])
            hist=hist/(binsize)
            yerr=yerr/(binsize)
        return hist,bins,yerr

    def update_plot(self,nframe, data):

        hist=data["hist"]
        total_count=hist.sum()
        bins=data["bins"]
        total_time=data["total_time"]
        hist,bins,yerr=self.convert_hist_bins(hist,bins,total_time)
        self.bins=bins
                
        self._line.set_data(hist,bins)
        if self.error_bars:
            self._top.set_data(hist+yerr,bins)
            self._bot.set_data(hist-yerr,bins)

        self._text.set_text(f"time(s): {total_time:10.2f}\ntotal counts: {total_count:09d}")

        self._update_ylim(hist[hist!=0].min(), hist.max())

        return self.artists

    def _update_ylim(self, ymin, ymax, ax=None):
        if ax is None:
            ax=self.ax
        _ymin,_ymax=ax.get_ylim()
        ymin_=_ymin
        ymax_=_ymax
        
        if self.log:
            ymin_=10**(numpy.floor(numpy.log10(ymin))-0.2)
            ymax_=10**numpy.ceil(numpy.log10(ymax*1.2))
        else:
            ymin_=0
            ymax_=2**numpy.ceil(numpy.log2(ymax*1.2))
            
        if _ymax!=ymax_ or _ymin!=ymin_:
            ax.set_ylim(ymin_,ymax_)
            pyplot.draw()


    def background_hist_bins(self):
        with open(self.background,'rb') as f:
            data=pickle.load(f)
        hist=data["hist"]
        bins=data["bins"]
        total_time=data["total_time"]
        if self.input_wire.unit != data["unit"]:
            message=f"Background spectrum wrong unit, expect {self.input_wire.unit}, has {data['unit']}"
            raise Exception(message)
        if (len(bins)!=len(self.bins) or numpy.any(bins-self.bins>1.e-7)) and self.input_wire.histogram_mode=="normal": 
            message=f"Background spectrum binning does not match"
            raise Exception(message)

        return self.convert_hist_bins(hist,bins,total_time)
        

    def setup_plot(self):
        fig, ax = pyplot.subplots()
        fig.canvas.manager.set_window_title("GammaLab Histogram")
        ax.cla()
        
        nchannels=self.input_wire.nchannels
        vmin=self.input_wire.vmin
        vmax=self.input_wire.vmax
        hist,bins=numpy.histogram([], bins=nchannels, range=(vmin,vmax))
        self.bins=bins

        if self.error_bars:
            yerr=hist**0.5
            self._top=ax.stairs(numpy.maximum(hist+yerr,1),bins,ls=":",color="tab:orange", zorder=0)
            self._bot=ax.stairs(hist-yerr,bins,ls=":",color="tab:orange",zorder=5)
        self._line=ax.stairs(hist,bins,lw=2, zorder=10)
        if self.background:
            hist,bins,err=self.background_hist_bins()
            _line=ax.stairs(hist,bins,lw=2., zorder=11, color="tab:grey", ls="--")
        if self.log:
            ax.set_yscale("log", nonpositive="mask")

        ylabel="counts"
        if self.time_normalized:
          ylabel=ylabel+" / s"

        if self.input_wire.histogram_mode=="normal":
            ylabel=ylabel+" / bin"
        else:
            ylabel=ylabel+f" / {self.input_wire.unit}"
        ax.set_ylabel(ylabel)

        self._text=ax.text(0.95,0.95,f"time(s): {0.:10.2f}\ntotal counts: {0:09d}", va='top', ha='right',transform=ax.transAxes)
            

        ax.set_xlabel(f"energy ({self.input_wire.unit})")
        ax.set_xlim(self.xmin,self.xmax)
        self.ymin, self.ymax=ax.get_ylim()
        if self.log:
            self.ymin=self.ymax/self.yrange
            ax.set_ylim(self.ymin,self.ymax)
        
        pyplot.tight_layout()
        
        if self.error_bars:
            artists=[self._text,self._line, self._top, self._bot]
        else:
            artists=[self._text,self._line]
        
        return fig,ax,artists
      
class CountPlot(_Plot):
    input_wire_class=CountWire

    def __init__(self, outfile=None):                
        super().__init__(outfile=outfile)
        self.time=[]
        self.count=[]
        self.total_time=0
        self.avgcps=0
        self.blit=True

    def get_data(self):        
        data=None
        while True:
            _data=self.receive_input(False)
            if _data is None:
                break
            data=_data
 
        return data
        

    def update_plot(self,nframe, data):
            
        cps=data["count_per_sec"]
        tbins=data["time_bins"]
        self.total_time=data["total_time"]
        interval=data["interval"]
              
        self.count=cps
        self.time=(tbins[1:]+tbins[0:-1])/2
        if self.total_time!=0:
            self.avgcps=self.count.sum()*interval/self.total_time
        else:
            self.avgcps=0.
        
        self.artists[0].set_data(self.time, self.count)
        self.artists[1].set_data([self.time[0],self.total_time], [self.avgcps,self.avgcps])

        xmin,xmax=self.ax.get_xlim()
        ymin,ymax=self.ax.get_ylim()
        _xmax=self.time[-1]
        _ymax=1.5*max(self.count)
        if _xmax>xmax or _ymax>ymax:   
            self.ax.set_xlim(0,_xmax)
            self.ax.set_ylim(0,_ymax)
            pyplot.draw()

        return self.artists
  
    def setup_plot(self):
        fig, ax = pyplot.subplots(figsize=(6,3))
        fig.canvas.manager.set_window_title("GammaLab Counts")

        ax.cla()
        artist1,=ax.plot(self.time,self.count, ".")
        artist2,=ax.plot([0,10],[self.avgcps,self.avgcps], "g--")
        ax.set_xlabel("time (s)")
        ax.set_ylabel("counts per sec")
        ax.set_xlim(0,10)
        ax.set_ylim(0,30)
        pyplot.tight_layout()

        return fig,ax,[artist1, artist2]


class PulsePlot(_Plot):
    input_wire_class=PulseWire

    def __init__(self, nplot=1, interval=250):                
        super().__init__(interval=interval)
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
        self.ax.set_ylim(dmin-.15*(dmax-dmin),dmax+0.2*(dmax-dmin))

        return self.lines[0:len(self.data)]
            
    def setup_plot(self):
        fig, ax = pyplot.subplots(figsize=(5,2))
        fig.canvas.manager.set_window_title("GammaLab Pulse Monitor")

        self.data=[numpy.array([0]*40)]*self.nplot

        self.lines=[]        
        for d in self.data:
            t=(numpy.arange(0,len(d))-5)
            line,=ax.plot(t,d,"+-")
            self.lines.append(line)

        ax.set_xlim(-5,35)
        ax.set_ylim(-.15,1.2)


        ax.set_xlabel("time")
        ax.set_ylabel("level")
        ax.set_xticks([],[])
        ax.set_yticks([],[])
        
        #~ ax.yaxis.set_label_coords(0.0,0.5)
        #~ ax.xaxis.set_label_coords(0.5,0.0)
        
        #~ ax.set_title("selected pulses")
        
        pyplot.tight_layout()
        
        artists=self.lines
        
        return fig,ax,artists
