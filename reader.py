#!/usr/bin/env python3
import numpy as np
import matplotlib as mpl
mpl.use('Agg')
from matplotlib import pyplot as plt
from tqdm import tqdm
import argparse
import re

def save_fig(filename, data, figsize=(20, 20)):
    mpl.rcParams['agg.path.chunksize'] = 10000
    fig = plt.figure(figsize=figsize)
    for index_channel, channel_data in enumerate(data):
        fig.add_subplot(data.shape[0], 1, index_channel+1)
        plt.plot(channel_data)
    fig.tight_layout()
    fig.savefig(filename)

def get_ekg(filename, number_channels=10, bytes_per_value=2, value_signed=True, loc_data_start=0x4B8):
    data = [ list() for _ in range(number_channels) ]
    with open(filename, 'rb') as f:
        f.seek(loc_data_start, 0)
        while True:
            raw = f.read(bytes_per_value * number_channels)
            if len(raw) < bytes_per_value * number_channels:
                break
            for index_channel in range(number_channels):
                data[index_channel].append(int.from_bytes(
                    raw[index_channel*bytes_per_value: (index_channel+1)*bytes_per_value],
                    byteorder='little', signed=value_signed))
    data = np.array(data)
    data = data[:, :10000]

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
        channel_signals = [ [] for _ in range(number_channels) ]
        data_cycle = int(main_sampling_rate // channel_sampling_rate[-1])
        index_order = []
        for cycle in range(data_cycle):
            for index_channel in range(number_channels):
                if cycle % (main_sampling_rate // channel_sampling_rate[index_channel]) == 0:
                    index_order.append(index_channel)

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
        number_cycles = file_size // 2 // len(index_order)

        # reading raw file
        f.seek(0x200) # 512
        for _ in tqdm(range(number_cycles),desc='reading '+filename, disable=not verbose):
            for index_channel in index_order:
                raw = f.read(0x2)
                if len(raw) < 0x2: break # EOF
                channel_signals[index_channel].append(np.frombuffer(raw, dtype=np.uint16)[0] )
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
