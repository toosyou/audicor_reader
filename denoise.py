import numpy as np
import pywt
from scipy.signal import medfilt

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

def denoise(ecg_data, number_channels=None):
    number_channels = ecg_data.shape[0] if number_channels is None else number_channels
    for i in range(number_channels): # number of channel
        ecg_data[i] = wavelet_threshold(ecg_data[i])
        ecg_data[i] = baseline_wander_removal(ecg_data[i])

    return ecg_data
