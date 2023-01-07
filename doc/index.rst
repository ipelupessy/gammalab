.. GammaLab documentation master file, created by
   sphinx-quickstart on Fri Jan  6 15:08:47 2023.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. include:: ../README.rst

Documentation of included tools
===============================

Three tools are distributed with the GammaLab package: ```gammalab-monitor.py```, ```gammalab-histogram.py``` 
and ```gammalab-calibration-calc.py```. The first tool ```gammalab-monitor.py``` can be used to monitor and/or
save the soundcard data:

.. argparse::
   :filename: ../bin/gammalab-monitor.py
   :func: new_argument_parser
   :prog: gammalab-monitor

The second, ```gammalab-histogram.py```, can be used to generate and visualize histogram data for the detected 
gamma ray pulses, and a couple of other things:

.. argparse::
   :filename: ../bin/gammalab-histogram.py
   :func: new_argument_parser
   :prog: gammalab-histogram.py

Finally, ```gammalab-calibration-calc.py``` is a little tool to calculate calibration data from raw value, energy
pairs (e.g. determined by reading it off from a ```--raw``` histogram):

.. argparse::
   :filename: ../bin/gammalab-calibration-calc.py
   :func: new_argument_parser
   :prog: gammalab-calibration-calc.py

.. toctree::
   :maxdepth: 2
   :caption: Contents:


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
