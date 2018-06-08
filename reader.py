#!/usr/bin/env python3
import numpy as np
import matplotlib as mpl
mpl.use('Agg')
from matplotlib import pyplot as plt
import argparse
import re

from scipy.signal import butter, lfilter

def butter_bandpass_filter(data, lowcut, highcut, fs, order=5):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq

    b, a = butter(order, [low, high], btype='band')
    y = lfilter(b, a, data)
    return y

def save_fig(filename, data, figsize=(20, 20)):
    mpl.rcParams['agg.path.chunksize'] = 10000
    fig = plt.figure(figsize=figsize)
    for index_channel, channel_data in enumerate(data):
        fig.add_subplot(data.shape[0], 1, index_channel+1)
        plt.plot(channel_data)
    fig.tight_layout()
    fig.savefig(filename)

def get_ekg(filename, do_bandpass_filter=True, filter_lowcut=8, filter_highcut=250):
    with open(filename, 'rb') as f:
        f.seek(0xE8)
        data_length = int.from_bytes(f.read(2), byteorder='little', signed=False)

        f.seek(0xE0)
        number_channels_ekg = int.from_bytes(f.read(2), byteorder='little', signed=False)

        f.seek(0xE4)
        number_channels_hs = int.from_bytes(f.read(2), byteorder='little', signed=False) # heart sound
        number_channels = number_channels_ekg + number_channels_hs

        data = [ list() for _ in range(number_channels) ]

        # data start
        f.seek(0x4B8)
        for index_cycle in range(data_length):
            raw = f.read(2 * number_channels)
            if len(raw) < 2 * number_channels:
                break
            for index_channel in range(number_channels):
                data[index_channel].append(int.from_bytes(
                raw[index_channel*2: (index_channel+1)*2],
                byteorder='little', signed=True))

    data = np.array(data)
    if do_bandpass_filter:
        for index_channel in range(number_channels_ekg, number_channels_ekg+number_channels_hs):
            data[index_channel] = butter_bandpass_filter(data[index_channel], filter_lowcut, filter_highcut, 1000)
    return data

def get_heart_sounds(filename, verbose=True):
    with open(filename, 'rb') as f:
        # reading header
        f.read(0x24) # padding
        number_channels = int.from_bytes(f.read(0x1), byteorder='little')
        while f.read(0x1) != b'\x0F': pass
        main_sampling_rate = float(f.read(0x10)[:0xF].decode('utf-8'))
        channel_sampling_rate = [ float(f.read(0x10)[:0xF].decode('utf-8')) for _ in range(number_channels) ]

        # calculate reading order
        data_cycle = int(main_sampling_rate // channel_sampling_rate[-1])
        index_order = list()
        number_value_per_cycle = [0] * number_channels
        index_value_per_cycle = [list() for _ in range(number_channels)]
        for cycle in range(data_cycle):
            for index_channel in range(number_channels):
                if cycle % (main_sampling_rate // channel_sampling_rate[index_channel]) == 0:
                    index_order.append(index_channel)

        for index_channel, index_value in zip(index_order, range(len(index_order))):
            number_value_per_cycle[index_channel] += 1
            index_value_per_cycle[index_channel].append(index_value)

        if verbose: # print out info
            print('Headers:')
            print('number of channels:', number_channels)
            print('main sampling rate:', main_sampling_rate)
            for index_channel in range(number_channels):
                print('sampling rate-'+str(index_channel)+':', channel_sampling_rate[index_channel])
            print('channel reading order:', index_order)

        # calculate number of cycle
        f.seek(0, 2)
        file_size = f.tell()
        # number_cycles = (file_size - 512) // 2 // len(index_order)
        number_cycles = 500
        print('reading... ETA: {:.1f}s'.format(file_size / 1000 / 1000 / 17 + 3.7))

        # reading raw file
        f.seek(0x200) # 512
        values = np.frombuffer(f.read(0x2 * number_cycles * len(index_order)), dtype=np.uint16)
        channel_signals = [ np.ndarray([number_cycles * number_value_per_cycle[i]]) for i in range(number_channels) ]
        for index_channel in range(number_channels):
            for index_value in range(number_value_per_cycle[index_channel]):
                channel_signals[index_channel][index_value::number_value_per_cycle[index_channel]] = values[index_value_per_cycle[index_channel][index_value]::len(index_order)]

        return np.array(channel_signals)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Produce ekg and heart_sound figure.')
    parser.add_argument('filename', help='Filename to read. Must be *.bin or *.raw (case-insensitive).')
    parser.add_argument(
                '-o',
                '--output',
                help='Filename of saved figure. (default: output.png)',
                dest='output_filename',
                default='output.png')

    parser.add_argument(
                '-sx',
                '--size-x',
                help='X-axis size of saved figure. (default: 20)',
                dest='size_x',
                default=20)

    parser.add_argument(
                '-sy',
                '--size-y',
                help='Y-axis size of saved figure. (default: 20)',
                dest='size_y',
                default=20)

    args = parser.parse_args()

    figsize = (int(args.size_x), int(args.size_y))
    if re.search('.*.bin', args.filename, re.IGNORECASE):
        save_fig(args.output_filename, get_ekg(args.filename), figsize=figsize)
    elif re.search('.*.raw', args.filename, re.IGNORECASE):
        save_fig(args.output_filename, get_heart_sounds(args.filename), figsize=figsize)
    else:
        print('ERROR: filename must be *.bin or *.raw (case-insensitive).')
