#!/bin/python3
from curses.ascii import isdigit
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
    for o, a in opts :
        if o in ("-v", "--verbose") :
            verbose = True
        elif o in ("-h", "--help") :
            usage()
            return None
        elif o in ("-i", "--infile") :
            infile = a
        else :
            print("unhandled option")
            usage()
            return None
    return { 'verbose':verbose, 'infile':infile }

def convert_timestamps_to_ms(timestamps) :
    ts_list = []
    for ts in timestamps:
        ts_list.append(datetime.strptime(ts, '%Y-%m-%d %H:%M:%S.%f').timestamp() * 1000)
    return ts_list

def get_positions_of_data_set(data_set) :
    positions = range(0, len(data_set))
    return positions

def find_peak_values_with_postitions(data_set) :
    peak_values = [[], []]
    positions = []
    if data_set[0, 1] > data_set[1, 1] :
        peak_values[0].append(data_set[0, 0])
        peak_values[1].append(data_set[0, 1])
        positions.append(0)
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
    if data_set[-1, 1] > data_set[-2, 1] :
        peak_values[0].append(data_set[size - 1, 0])
        peak_values[1].append(data_set[size - 1, 1])
        positions.append(size - 1)
    return peak_values, positions

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

def calculate_fft_with_freq_line(data_set, sampling_frequency) :
    d_fft = np.fft.fft(data_set)
    n = len(d_fft)
    d_fft = d_fft / n
    df = sampling_frequency / n
    stop = n * df
    freq_line = np.arange(0, stop, df)
    return freq_line, d_fft

def show_fft_figure(freq_line, data_set) :
    data_set_db = 20 * np.lib.scimath.log10(np.abs(data_set))
    mplot.semilogx(freq_line, data_set_db)
    mplot.xlabel('Frequency [Hz]')
    mplot.ylabel('Amplitude [dB]')
    mplot.show()

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

def show_time_diagram(t, y) :
    mplot.plot(t, y)
    mplot.xlabel('Time [sec]')
    mplot.ylabel('Acceleration')
    mplot.xlim(t[0], t[-1])
    mplot.show()

def get_time_points(sampling_period, positions) :
    time_points = []
    for i in positions : 
        time_points.append(i * sampling_period)
    return time_points

def show_peak_values(t, y, tp, p) :
    mplot.plot(t, y)
    mplot.xlabel('Time [sec]')
    mplot.ylabel('Acceleration')
    mplot.xlim(t[0], t[-1])
    mplot.plot(tp, p, 'o')
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
            print('Sampling frequency in Hz: ' + sampling_frequency_hz + '\r\nSampling time period in second: ' + sampling_time_sec)
       elif option == '3' :
            print('This program use a simple peak finding algorithm. The more times the algorithm runs, the wider ranges it covers.\r\n'
            'How many times should the algorithm runs (1-10)?\r\n')
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
            peak_values, positions = find_peak_values_with_postitions(arr)
            for i in range(0, int(res) - 1) :
                peak_values, positions = reduce_peak_values(peak_values, positions)
            time_points = get_time_points(sampling_time_sec, positions)
            show_peak_values(time_line, arr[:, 1], time_points, peak_values[1])
       elif option == '4' :
            freq_line, fft_data_set = calculate_fft_with_freq_line(arr[:,1], sampling_frequency_hz)
            show_fft_figure(freq_line, fft_data_set)
       elif option == 'x' :
            quit = True
       else :
            print('Invalid input parameter. Try again!\r\n')

if __name__ == '__main__' :
    main()