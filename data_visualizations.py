#!/bin/python3
from genericpath import exists
from datetime import datetime
import pandas as ps
import matplotlib.pyplot as mplot
import numpy as np
import getopt
import sys

def usage() :
    print(
        '-h --help for help\r\n-i --infile filename\r\n'
    )
    pass

def opt_walk(opts) :
    verbose = False
    infile = None
    for o, a in opts:
        if o in ("-v", "--verbose"):
            verbose = True
        elif o in ("-h", "--help"):
            usage()
            return None
        elif o in ("-i", "--infile"):
            infile = a
        else:
            print("unhandled option")
            usage()
            return None
    return { 'verbose':verbose, 'infile':infile }

def convert_timestamps_to_ms(timestamps) :
    ts_list = []
    for ts in timestamps:
        ts_list.append(datetime.strptime(ts, '%Y-%m-%d %H:%M:%S.%f').timestamp() * 1000)
    return ts_list

def find_peak_values(data_set) :
    peak_values = {}
    i = 1
    size = len(data_set[:,0])
    while i < (size - 1) :
        if (data_set[i, 1] > data_set[i - 1, 1]) and (data_set[i, 1] > data_set[i + 1, 1]) :
            peak_values[data_set[i, 0]] = data_set[i, 1]
            i += 2
        else :
            i += 1
    return peak_values

def calculate_sample_time(ts_list) :
    step = 1
    finished = False
    sample_time = 0
    ctr = 1

    while not finished :
        pre_dif = ts_list[step] - ts_list[0]
        dif = ts_list[step + step] - ts_list[step]
        ctr += 1
        if pre_dif != dif :
            step += 1
        elif ctr > len(ts_list) :
            finished = True
        else :
            stopped = False
            for i in range(3 * step, 3000, step) :
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

def menu() :
    print(
        'Select an option:\r\n'
        '0) - show menu\r\n'
        '1) - show time based figure of the input data set\r\n'
        '2) - show the sampling frequency & time\r\n'
        '3) - find peak values\r\n'
        '4) - show the input signal in frequency domain\r\n'
        'x) - exit from this program'
    )

def show_figure(x, y) :
    mplot.plot(x, y)
    mplot.xlabel('Time [sec]')
    mplot.ylabel('Acceleration')
    mplot.xlim(x[0], x[-1])
    mplot.show()

def main() :
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hi:", ["help", "infile="])
    except getopt.GetoptError as err:
        print(err + '\r\n')
        usage()
        sys.exit(1)
    
    res = opt_walk(opts)
    infile = res['infile']
    
    if (infile == None) or (not exists(infile)) :
        print('there is no existing input file\r\nhint: -i, --infile filename')
        sys.exit(1)    
    
    data_set = ps.read_csv(infile, sep=',', squeeze=True, names=['time_stamp', 'acceleration'])
    arr = data_set.to_numpy()
    ts_list = convert_timestamps_to_ms(arr[:, 0])
    sampling_time_sec = calculate_sample_time(ts_list)
    sampling_frequency_hz = (1 / sampling_time_sec)
    n = len(ts_list)
    time_line = np.arange(0, n * sampling_time_sec, sampling_time_sec)
    menu()
    quit = False
    while not quit :
       option = input()
       if option == '0' :
            menu()
       elif option == '1' :
            show_figure(time_line, arr[:, 1])
       elif option == '2' :
            print('Sampling frequency in Hz: ' + sampling_frequency_hz + '\r\nSampling time period in second: ' + sampling_time_sec)
       elif option == '3' :
            peak_values = find_peak_values(arr)
            print(peak_values)
       elif option == '4' :
            print(' ')
       elif option == 'x' :
            quit = True
       else :
            print('Invalid input parameter. Try again!\r\n')

if __name__ == '__main__' :
    main()