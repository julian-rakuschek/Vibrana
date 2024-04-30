# DeweSoft Parser

Author: Julian Rakuschek

DeweSoft is a software for collecting measurements from sensor data, which can be exported as `dxd` files.
This file format is proprietary and in binary format, thus a parser is required such that they can be processed in a python environment.

The provided script [dwparser.py](dwparser.py) translates a given folder of dxd files into numpy arrays.
One dxd file results in three numpy arrays:
* `values.npy` is the raw extracted time series, provided as a 1D array
* `timestamps.npy` contains the UNIX timestamp for each value in `values.npy`
* `event_timestamps.npy` contains UNIX timestamps which are marked as events. These are not necessarily contained in `timestamps.py`, therefore, in order to match event timestamps to specific values in the time series, a nearest neighbor search is recommended.

Additionally, the parser plots the time series together with events.

## Setup
To run the parser, a Linux operating system together with python 3.11 is required.
Further, install the python packages `numpy` and `matplotlib`.
Place the dxd files in a folder `data` that is on the same hierarchy level as the folder which contains this parser, e.g.
* data
  * file1.dxd
  * file2.dxd
  * ...
* parser
  * DWDataReaderHeader.py
  * DWDataReaderLib64.so
  * dwparser.py

The script creates a new folder for each dxd file with all resulting numpy arrays and the plot.