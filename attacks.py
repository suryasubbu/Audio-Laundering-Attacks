from __future__ import print_function
import pandas as pd
import librosa
import soundfile as sf
import pyroomacoustics as pra
import pyroomacoustics
import numpy as np
import os
from audiomentations import AddShortNoises, PolarityInversion
from scipy.signal import butter, lfilter
import scipy.io.wavfile as wavf
import warnings
import subprocess
import threading
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

def room_reverb_out(audio, fs, rt60_tgt,master_reverb_out_path,filename,save_processed_audio_dir):
    reverb_3_audio = room_reverb(audio, fs, rt60_tgt)
    if not os.path.exists(master_reverb_out_path):
        os.makedirs(master_reverb_out_path)
    new_filename = master_reverb_out_path + filename + '_{}'.format(save_processed_audio_dir)
    print(new_filename)
    # sf.write(new_filename + '.flac', reverb_3_audio, sr, format='flac', subtype='PCM_16')
    # reverb_3_audio.to_wav(
    #     new_filename + '.wav',
    #     norm=True,
    #     bitdepth=np.int16,
    # )
    return reverb_3_audio
    

def noise_add(noise_path,snr_rangei,snr_rangej):
    transform = AddShortNoises(
        sounds_path=noise_path,
        min_snr_in_db=snr_rangei,
        max_snr_in_db=snr_rangej,
        noise_rms="relative_to_whole_input",
        min_time_between_sounds=0.5,
        max_time_between_sounds=1,
        noise_transform=PolarityInversion(),
        p=1.0
    )
    
    return transform

def noise_add_out(noise_path,snr_rangei,snr_rangej,audio_data,sr,fs,master_noise_out_path,save_processed_audio_dir,row,filename):
    fs = fs
    transform = noise_add(noise_path,snr_rangei,snr_rangej)
    augmented_white_noise = transform(audio_data, sample_rate=sr)
    # output_path = master_noise_out_path + "{}/{}/".format(save_processed_audio_dir,row["speaker"])
    # print(output_path)
    if not os.path.exists(master_noise_out_path):
        os.makedirs(master_noise_out_path)
    # print(master_noise_out_path)
    output_path = master_noise_out_path + filename + "_" + save_processed_audio_dir + ".wav"
    # write array to wav file
    noise_wav = wavf.write(output_path, sr, augmented_white_noise)

def recompression(filename,input_file, output_folder,output_folder2,bit_rate):
    basefile = os.path.basename(input_file)
    file = os.path.splitext(basefile)[0]
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    if not os.path.exists(output_folder2):
        os.makedirs(output_folder2)
    print("t")
    # Compression (wav to mp3)
    c_file = output_folder +"{}_{}.mp3".format(filename,bit_rate)
    subprocess.run(['ffmpeg', '-i', input_file, '-b:a', bit_rate, c_file])

   # Compression (mp3 to wav)
    dc_file = output_folder2 +"{}_{}.wav".format(filename,bit_rate)
    subprocess.run(['ffmpeg', '-i',c_file,dc_file])

def resample(y,sr, filename, output_folder, factor):
    
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

        # Up-sample by a factor 
    y_downsampled = librosa.resample(y, orig_sr=sr, target_sr=factor)

    # Save the up-sampled audio as .wav files
    sf.write(os.path.join(output_folder, f'{filename}_resample_{factor}.wav'),y_downsampled, factor,subtype='PCM_16')

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


def filtering(y,sr,filename, output_folder):
    
     

    # Specify the fraction of Nyquist frequency for the cutoff
    # nyquist_fraction = 0.1  #adjustable
        # Calculate the cutoff frequency
    # cutoff_frequency = nyquist_fraction * (sr / 2)
    
    
    lp_nyquist_fraction = 0.2  #adjustable


    lp_cutoff_frequency =7000
  
    # Apply the low-pass filter using lfilter
    filtered_data = butter_lowpass_filter(y, lp_cutoff_frequency, sr)
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    # sf.write(os.path.join(output_folder, f'{file[:-len("_pp_dc1")]}_low_pass_filt_.wav'),filtered_data, sr,  subtype='PCM_16')
    sf.write(os.path.join(output_folder, f'{filename}_resample_{"butterworth"}.wav'),filtered_data, sr,subtype='PCM_16')


room_reverb_out(audio, fs, rt60_tgt,master_reverb_out_path,filename,save_processed_audio_dir)