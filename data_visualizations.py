#!/bin/python3

from genericpath import exists
from datetime import datetime
import pandas as ps
import statistics as stat
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
    verbose = False
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
        ts_list.append(datetime.strptime(ts, '%Y-%m-%d %H:%M:%S.%f').timestamp() * 1000)
    return ts_list

# this function gives the locations of the data set in a list
def get_positions_of_data_set(data_set) :
    positions = range(0, len(data_set))
    return positions

# this function finds the peak values of the data_set input parameter
# data_set must be an two dimensional array
# it gives back locations of the peak values and of course the peak values with timestamps
def find_peak_values_with_postitions(data_set) :
    peak_values = [[], []]
    positions = []
    # if the first data is greater than second, then it is a peak value
    if data_set[0, 1] > data_set[1, 1] :
        peak_values[0].append(data_set[0, 0])
        peak_values[1].append(data_set[0, 1])
        positions.append(0)
    # this peak finding algorithm is really simple and not the fastest one but it works very well
    # the algorithm examines the neighbors of the data and if they are less then this, then this data is a peak value
    i = 1
    size = len(data_set[:,0])
    while i < (size - 1) :
        if (data_set[i, 1] > data_set[i - 1, 1]) and (data_set[i, 1] > data_set[i + 1, 1]) :
            peak_values[0].append(data_set[i, 0])
            peak_values[1].append(data_set[i, 1])
            positions.append(i)
            i += 2
        else :
            i += 1
    # if the last data is greater then penultimate data, then is a peak value
    if data_set[-1, 1] > data_set[-2, 1] :
        peak_values[0].append(data_set[size - 1, 0])
        peak_values[1].append(data_set[size - 1, 1])
        positions.append(size - 1)
    return peak_values, positions

# the goal of this function is to reduce the number of peak values by finding the peaks from the peak_values list (input parameter)
# if this algorithm runs several times, then the targeted small local ranges will be wider and wider
# the description of the peak finding algorithm can be find at the find_peak_values_with_positions function
def reduce_peak_values(peak_values, positions) :
    new_positions = []
    new_peak_values = [[], []]
    if peak_values[1][0] > peak_values[1][1] :
        new_peak_values[0].append(peak_values[0][0])
        new_peak_values[1].append(peak_values[1][0])
        new_positions.append(positions[0])
    i = 1
    size = len(peak_values[0])
    while i < (size - 1) :
        if (peak_values[1][i] > peak_values[1][i - 1]) and (peak_values[1][i] > peak_values[1][i + 1]) :
            new_peak_values[0].append(peak_values[0][i])
            new_peak_values[1].append(peak_values[1][i])
            new_positions.append(positions[i])
            i += 2
        else :
            i += 1
    if peak_values[1][-1] > peak_values[1][-2] :
        new_peak_values[0].append(peak_values[0][size - 1])
        new_peak_values[1].append(peak_values[1][size - 1])
        new_positions.append(positions[size - 1])
    return new_peak_values, new_positions
    
# estimating of the sampling period time
# the problem is that the dates in the input files are not accurate enough
# to solve this problem I created a really simple algorithm in this function
def calculate_sample_time(ts_list) :
    step = 1
    finished = False
    sample_time = 0
    n = len(ts_list)
    ctr = 1
    # if finished parameter will be true, then the algorithm probably estimated the value of the sampling period time
    # if the finished parameter becomes true, but the algorithm failed, then the return value will be zero
    while not finished :
        # start with step=1 (this step or jump value will be greater and greater during the process)
        # calculation of the time difference between two pairs of values and counting the operations
        pre_dif = ts_list[step] - ts_list[0]
        dif = ts_list[2 * step] - ts_list[step]
        ctr += 1
        # if the two time differences are not equal to each other, then the step value will be increased
        if pre_dif != dif :
            step += 1
        # if the count of the operations is greater than length of the input list, then algorithm failed or there is no valid sampling frequency value
        elif ctr > n :
            finished = True
        # if the compared time differences are equal to each other, then this algorithm makes sure that this sampling period value is acceptable
        else :
            # the stopped flag will be true, if the calculated time difference is not acceptable as sampling period
            stopped = False
            # the algorithm assumes that there is a lot of data in the input file, so it checks only 1% of the data set
            for i in range(3 * step, int(n * 0.01), step) :
                dif = ts_list[i] - ts_list[i - step]
                if dif != pre_dif:
                    stopped = True
                    break
            # if stopped flag is true, then the algorithm try to estimate the sampling period with increased step value
            if stopped :
                step += 1
            # if the stopped flag is false, then the algorithm estimated the value of the period time
            # (attention! we use only 1% of data, so the success of this algorithm depends on the size of data)
            else :
                sample_time = (ts_list[step] - ts_list[0]) / step
                finished = True
    # get the sample time in sec (ts_list is in ms)
    return sample_time / 1000

def show_statistics(data_set) :
    # mean - 1/N * sum(data)
    mean = stat.fmean(data_set)
    # median - ex.: [1, 2, 3, 4, 5] -> 3
    median = stat.median(data_set)
    # mode - ex.: [1, 1, 2, 3, 3, 4, 4, 4, 4, 5, 5] -> 4
    mode = stat.mode(data_set)
    # deviation - sqrt(VAR(data))
    deviation = stat.pstdev(data_set, mean)
    # variance - VAR(data) = 1/N * sum([(d - mean)**2 for d in data])
    variance = deviation**2
    print(
        'Mean of data set: ' + str(mean) + '\r\n'
        'Mode of data set: ' + str(mode) + '\r\n'
        'Median of data set: ' + str(median) + '\r\n'
        'Variance of data set: ' + str(variance) + '\r\n'
        'Deviation of data set: ' + str(deviation) + '\r\n'
    )

def calculate_fft_with_freq_line(data_set, sampling_frequency) :
    d_fft = np.fft.fft(data_set)
    n = len(d_fft)
    d_fft = d_fft / n
    df = sampling_frequency / n
    stop = n * df
    freq_line = np.arange(0, stop, df)
    return freq_line, d_fft

def show_fft_figure(freq_line, data_set, sampling_frequency) :
    data_set_db = 20 * np.lib.scimath.log10(np.abs(data_set))
    mplot.semilogx(freq_line, data_set_db)
    mplot.title('DFT of the data set on logarithmic scale')
    mplot.xlabel('Frequency [Hz]')
    mplot.ylabel('Amplitude [dB]')
    mplot.xlim(0, sampling_frequency / 2)
    mplot.grid()
    mplot.show()

def show_scatter(data_set) :
    x = range(0, len(data_set))
    mplot.scatter(x, data_set)
    mplot.title('Scatter diagram')
    mplot.xlabel('Locations')
    mplot.ylabel('Values')
    mplot.show()

def get_user_input():
    ok = False
    while not ok :
        answ = input()
        try :
            res = int(answ)
        except ValueError :
            print('You answer is invalid. Try again!')
            continue
        if res not in range(1,10) :
            print('Your answer is not in range (1-9). Try again!')
        else :
            ok = True
    return res

def show_time_diagram(t, y) :
    mplot.plot(t, y)
    mplot.title('Logarithmic frequency domain')
    mplot.xlabel('Time [sec]')
    mplot.ylabel('Acceleration')
    mplot.grid()
    mplot.xlim(t[0], t[-1])
    mplot.show()

def get_time_points(sampling_period, positions) :
    time_points = []
    for i in positions : 
        time_points.append(i * sampling_period)
    return time_points

def show_peak_values(t, y, tp, p) :
    mplot.plot(t, y)
    mplot.title('Peak values of the data set')
    mplot.xlabel('Time [sec]')
    mplot.ylabel('Acceleration')
    mplot.xlim(t[0], t[-1])
    mplot.grid()
    mplot.plot(tp, p, 'o')
    mplot.show()

def show_histogram(data_set, sampling_time) :
    figure, hist = mplot.subplots()
    hist.hist(data_set)
    y_values = hist.get_yticks()
    hist.set_yticklabels(['{:.2f}'.format(i * sampling_time) for i in y_values])
    mplot.title('Histogram')
    mplot.xlabel('Acceleration')
    mplot.ylabel('Time [s]')
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
            show_time_diagram(time_line, arr[:, 1])
        elif option == '2' :
            print('Sampling frequency in Hz: ' + str(sampling_frequency_hz) + '\r\nSampling time period in second: ' + str(sampling_time_sec))
        elif option == '3' :
            print('This program use a simple peak finding algorithm. The more times the algorithm runs, the wider ranges it covers.\r\n'
            'How many times should the algorithm runs (1-10)?')
            res = get_user_input() 
            peak_values, positions = find_peak_values_with_postitions(arr)
            for i in range(0, int(res) - 1) :
                peak_values, positions = reduce_peak_values(peak_values, positions)
            time_points = get_time_points(sampling_time_sec, positions)
            show_peak_values(time_line, arr[:, 1], time_points, peak_values[1])
        elif option == '4' :
            freq_line, fft_data_set = calculate_fft_with_freq_line(arr[:,1], sampling_frequency_hz)
            show_fft_figure(freq_line, fft_data_set, sampling_frequency_hz)
        elif option == '5' :
            show_histogram(arr[:,1], sampling_time_sec)
        elif option == '6' :
            show_scatter(arr[:,1])
        elif option == '7' :
            show_statistics(arr[:,1])
        elif option == 'x' :
            quit = True
        else :
            print('Invalid input parameter. Try again!\r\n')

if __name__ == '__main__' :
    main()