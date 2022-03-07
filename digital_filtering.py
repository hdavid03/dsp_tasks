#!/bin/python3

from datetime import datetime as dt
import scipy.signal as sig
import pandas as ps
import matplotlib.pyplot as mplot
import numpy as np
import getopt
import sys

# this function gives that how to use this program
def usage() :
    print(
        '-h --help for help\r\n-i --infile filename\r\n'
    )

# handling of input arguments
# return with the path of the input file
def opt_walk(opts) :
    infile = None
    for o, a in opts :
        if o in ("-h", "--help") :
            usage()
        elif o in ("-i", "--infile") :
            infile = a
        else :
            print("unhandled option")
            usage()
    return infile

# estimating of the sampling period time
# description of this function and comments can be found in data_visualizations.py 
def calculate_sample_time(ts_list) :
    step = 1
    finished = False
    sample_time = 0
    n = len(ts_list)
    ctr = 1
    while not finished :
        pre_dif = ts_list[step] - ts_list[0]
        dif = ts_list[2 * step] - ts_list[step]
        ctr += 1
        if pre_dif != dif :
            step += 1
        elif ctr > n :
            finished = True
        else :
            stopped = False
            for i in range(3 * step, int(n * 0.01), step) :
                dif = ts_list[i] - ts_list[i - step]
                if dif != pre_dif:
                    stopped = True
                    break
            if stopped :
                step += 1
            else :
                sample_time = (ts_list[step] - ts_list[0]) / step
                finished = True
    return sample_time / 1000

# this function is showing the menu
def menu() :
    print(
        'Select an option:\r\n'
        '0) - show menu\r\n'
        '1) - show time based figure of the input data set\r\n'
        '2) - show the sampling frequency & time\r\n'
        '3) - find peak values\r\n'
        '4) - show the input signal in frequency domain\r\n'
        '5) - show histogram of data set\r\n'
        '6) - show scatter diagram of data set\r\n'
        '7) - show statistical informations of the data set\r\n'
        'x) - exit from this program'
    )

# convert datetime strings to milliseconds
# timestamps parameter must be iterable and the elements must be %Y-%m-%d %H:%M:%S.%f in format
def convert_timestamps_to_ms(timestamps) :
    ts_list = []
    for ts in timestamps:
        ts_list.append(dt.strptime(ts, '%Y-%m-%d %H:%M:%S.%f').timestamp() * 1000)
    return ts_list

def low_pass_fir(order, cutoff_freq) :
    return sig.firwin(order + 1, cutoff_freq)

def high_pass_fir(order, pass_freq) :
    return sig.firwin(order + 1, pass_freq, pass_zero=False)

def band_pass_fir(order, pass_f, stop_f) :
    return sig.firwin(order + 1, [pass_f, stop_f], pass_zero=False)

def main() :
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hi:", ["help", "infile="])
    except getopt.GetoptError as err:
        print(err + '\r\n')
        usage()
        sys.exit(1)
    # opt_walk function returns with the path of the input file
    infile = opt_walk(opts)
    # reading the csv file
    data_set = ps.read_csv(infile, sep=',', squeeze=True, names=['time_stamp', 'acceleration'])
    # converting the DataFrame object to numpy array
    arr = data_set.to_numpy()
    # the first column of array contains the dates of sampling and the second one contains the values
    dates = 0
    values = 1
    # converting the date timestamps to millisecond values
    ts_list = convert_timestamps_to_ms(arr[:, dates])
    sampling_time_sec = calculate_sample_time(ts_list)
    sampling_frequency_hz = (1 / sampling_time_sec)

if __name__ == '__main__' :
    main()