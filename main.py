from __future__ import print_function
import pandas as pd
import librosa
import soundfile as sf
import pyroomacoustics as pra
from laundering import *
import config as config
import sys, os
# decorater used to block function printing to the console
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
def out_one(audio_path,reverb = False, noises =False, recomp = False, fil = False, resample = False  ):

    out_dir = config.out_dir

    file_name_with_ext = os.path.basename(audio_path)
    file_name = file_name_with_ext.split(".")[0]
    fil_ext = file_name_with_ext.split(".")[1]
    audio_data, sr = librosa.load(audio_path,sr = None)

    # Reverberation
    if reverb:
        for r in reverb:    
            room_reverb(audio_data, sr,r).to_wav(
            f"{out_dir}/{file_name.split(".")[0]}_RT_{str(r).split(".")[0]}_{str(r).split(".")[1]}.wav",
            norm=True,
            bitdepth=np.int16,
        )
        
    # Noise Addition
    if noises:
        noises = np.array(noises)
        for n in noises:
            for noisy in n:
                noise = noise_add(f"noises/{noisy[0]}.wav",float(noisy[1]),float(noisy[2]),audio_data,sr)
                wavf.write(f"{out_dir}/{file_name}_{noisy[0]}_{noisy[1]}.wav", sr, noise)

    if recomp:
         for rec in recomp:
            recompression(audio_path, out_dir,out_dir,rec)

    if fil:
        f = filtering(audio_data,sr)
        sf.write(os.path.join(out_dir, f'{file_name}_lpf_7000.wav'),f, sr,subtype='PCM_16')

    if resample:
         for res in resample:
              
            resampled_audio = resampling(audio_path,res)
            sf.write(os.path.join(out_dir, f'{file_name}_resample_{res}.wav'),resampled_audio, res,subtype='PCM_16')

# if __name__ == '__main__':
#     for a in config.audio_path:   
#         print(a)
        
#         # out_one(a,reverb = config.reverb, noises =config.noises, recomp = config.recomp, fil = config.fil, resample = config.resample )
#         #
#         out_one(a, noises = config.noises)