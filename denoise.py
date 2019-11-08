import numpy as np
import pywt
from scipy.signal import medfilt

import multiprocessing as mp

def wavelet_threshold(data, wavelet='sym8', noiseSigma=14):
    levels = int(np.floor(np.log2(data.shape[0])))
    WC = pywt.wavedec(data,wavelet,level=levels)
    threshold=noiseSigma*np.sqrt(2*np.log2(data.size))
    NWC = list(map(lambda x: pywt.threshold(x,threshold, mode='soft'), WC))
    return pywt.waverec(NWC, wavelet)

def baseline_wander_removal(data):
    baseline = medfilt(data, 201)
    baseline = medfilt(baseline, 601)
    return data - baseline

def _denoise_mp(signal):
    return baseline_wander_removal(wavelet_threshold(signal))

def denoise(ecg_data, number_channels=None):
    number_channels = ecg_data.shape[0] if number_channels is None else number_channels

    with mp.Pool(processes=number_channels) as workers:
        results = list()

        for i in range(number_channels):
            results.append(workers.apply_async(_denoise_mp, (ecg_data[i], )))

        workers.close()
        workers.join()

        for i, result in enumerate(results):
            ecg_data[i] = result.get()

    # for i in range(number_channels): # number of channel
    #     ecg_data[i] = wavelet_threshold(ecg_data[i])
    #     ecg_data[i] = baseline_wander_removal(ecg_data[i])

    return ecg_data
