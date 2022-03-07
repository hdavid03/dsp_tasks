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

def fir_filtering(filter_coeff, input) :
    n = len(input)
    order = len(filter_coeff)
    x = np.zeros(order)
    y = np.zeros(n)
    for i in range(0, n) :
        x = np.roll(x, 1)
        x[0] = input[i]
        for j in range(0, order) :
            y[i] += filter_coeff[j] * x[j]
    return y

def iir_filtering(a, b, input) :
    n = len(input)
    order = len(b)
    x = np.zeros(order)
    y = np.zeros(n)
    y_pre = np.zeros(n)
    for i in range(0, n) :
        x = np.roll(x);
        x[0] = input[i]
        for j in range(0, order - 1) :
            y[i] = y[i] + b[j] * x[j] - a[j+1] * y_pre[j]
        y[i] += b[-1] * x[-1]
        y_pre = y
    return y

# this function is showing the menu
def menu() :
    print(
        'Select an option:\r\n'
        '0) - show menu\r\n'
        '1) - show the signal before and after low pass filtering\r\n'
        '2) - show the signal before and after high pass filtering\r\n'
        '3) - show the signal before and after band pass filtering\r\n'
        '4) - show the original signal and its moving avarage\r\n'
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

def show_filtered_figure(t, y, y_filtered):
    mplot.plot(t, y, t, y_filtered)
    mplot.xlabel('Time [s]')
    mplot.ylabel('Amplitude')
    mplot.legend('Original signal', 'Signal after digital filtering')
    mplot.grid()
    mplot.show()

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
    n = len(ts_list)
    sampling_time_sec = calculate_sample_time(ts_list)
    sampling_frequency_hz = (1 / sampling_time_sec)
    order = 40
    # calculating the time axis for plotting the date set
    time_line = np.arange(0, n * sampling_time_sec, sampling_time_sec)
    nyquist_f = sampling_frequency_hz / 2
    
    quit = False
    while not quit :
        option = input()
        # options (0 - 7 + x to exit)
        if option == '0' :
            menu()
        elif option == '1' :
            lowpass_fir_filter = low_pass_fir(order, 0.00002)
            lp_filtered = fir_filtering(lowpass_fir_filter, arr[:, values])
            show_filtered_figure(time_line, arr[:, values], lp_filtered)
        elif option == '2' :
            highpass_fir_filter = high_pass_fir(order, 0.005)
            hp_filtered = fir_filtering(highpass_fir_filter, arr[:, values])
            show_filtered_figure(time_line, arr[:, 1], hp_filtered)
        elif option == '3' :
            bandpass_fir_filter = band_pass_fir(order, 0.005, 0.01)
            bp_filtered = fir_filtering(bandpass_fir_filter, arr[:, values])
            show_filtered_figure(time_line, arr[:, 1], bp_filtered)
        elif option == '4' :
            print(' ')
        elif option == 'x' :
            quit = True
        else :
            print('Invalid input parameter. Try again!\r\n')

if __name__ == '__main__' :
    main()