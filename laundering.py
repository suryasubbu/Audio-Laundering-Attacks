from __future__ import print_function
import pandas as pd
import librosa
import soundfile as sf
import pyroomacoustics as pra
import numpy as np
import os
from audiomentations import AddShortNoises, PolarityInversion
from scipy.signal import butter, lfilter
import scipy.io.wavfile as wavf
import warnings
import subprocess
import threading
import sys
warnings.filterwarnings("ignore")

def room_reverb(audio, fs, rt60_tgt):
    
    room_dim = [10, 7.5, 3.5]  # meters
    source = [2.5, 3.73, 1.76]
    mic = [6.3, 4.87, 1.2]
    e_absorption, max_order = pra.inverse_sabine(rt60_tgt, room_dim)

    room = pra.ShoeBox(
        room_dim, fs=fs, materials=pra.Material(e_absorption), max_order=max_order
    )

    room.add_source(source, signal=audio, delay=0.5)

    mic_locs = np.c_[mic]

    room.add_microphone_array(mic_locs)
    room.simulate()
    #print("exit")
    return room.mic_array

def noise_add(noise_path,snr_rangei,snr_rangej,audio_data,sr):
    transform = AddShortNoises(
        sounds_path=noise_path,
        min_snr_db=snr_rangei,
        max_snr_db=snr_rangej,
        noise_rms="relative_to_whole_input",
        min_time_between_sounds=0.15,
        max_time_between_sounds=0.16,
        noise_transform=PolarityInversion(),
        p=1.0
    )

    augmented_white_noise = transform(audio_data, sample_rate=sr)
    return augmented_white_noise 

def resampling(audio_path,factor):
    file_name = os.path.basename(audio_path)
    audio_data, sr = librosa.load(audio_path,sr = None)

    # Up-sample by a factor 
    y_downsampled = librosa.resample(audio_data, orig_sr=sr, target_sr=factor)

    return y_downsampled

def blockPrinting(func):
    def func_wrapper(*args, **kwargs):
        # block all printing to the console
        sys.stdout = open(os.devnull, 'w')
        # call the method in question
        value = func(*args, **kwargs)
        # enable all printing to the console
        sys.stdout = sys.__stdout__
        # pass the return value of the method back
        return value

    return func_wrapper

@blockPrinting
def recompression(input_file, output_folder,output_folder2,bit_rate):
    file_name = os.path.basename(input_file)
    # Compression (wav to mp3)
    c_file = output_folder +"{}_{}.mp3".format(file_name.split(".")[0],bit_rate)
    subprocess.run(['ffmpeg', '-i', input_file, '-b:a', bit_rate, c_file])

   # Compression (mp3 to wav)
    dc_file = output_folder2 +"{}_{}{}.wav".format(file_name.split(".")[0],"recompression",bit_rate)
    subprocess.run(['ffmpeg', '-i',c_file,dc_file])
    os.remove(c_file)




def filtering(y,sr):
    def butter_lowpass(cutoff, fs, order=5):
        nyq = 0.5 * fs
        normal_cutoff = cutoff / nyq
        b, a = butter(order, normal_cutoff, btype='low', analog=False)
        return b, a

    def butter_lowpass_filter(data, cutoff, fs, order=5):
        b, a = butter_lowpass(cutoff, fs, order=order)
        print(cutoff)
        y = lfilter(b, a, data)
        return y

    lp_nyquist_fraction = 0.2  #adjustable


    lp_cutoff_frequency =7000
  
    # Apply the low-pass filter using lfilter
    filtered_data = butter_lowpass_filter(y, lp_cutoff_frequency, sr)

    return filtered_data

