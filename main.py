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
def audio_laundering(audio_path,type): #["noise_parameter"]

    out_dir = config.out_dir

    file_name_with_ext = os.path.basename(audio_path)
    file_name = file_name_with_ext.split(".")[0]
    fil_ext = file_name_with_ext.split(".")[1]
    audio_data, sr = librosa.load(audio_path,sr = None)
    attack,parameter = str(type).split("_")
    print("file:",file_name_with_ext," attack:",attack," parameter:", parameter )

    if attack == "rt":
        room_reverb(audio_data, sr,float(parameter)).to_wav(
            f"{out_dir}/{file_name.split(".")[0]}_RT_{str(parameter).split(".")[0]}_{str(parameter).split(".")[1]}.wav",
            norm=True,
            bitdepth=np.int16,
        )
        wav_file = f"{out_dir}/{file_name.split(".")[0]}_RT_{str(parameter).split(".")[0]}_{str(parameter).split(".")[1]}.wav"
        audio_data, sr = librosa.load( f"{out_dir}/{file_name.split(".")[0]}_RT_{str(parameter).split(".")[0]}_{str(parameter).split(".")[1]}.wav",sr = None)
    
    if attack == "babble" or attack == "volvo" or attack == "white" or attack == "cafe" or attack == "street":
        noise = noise_add(f"noises/{attack}.wav",float(parameter),float(float(parameter)+0.5),audio_data,sr)
        wavf.write(f"{out_dir}/{file_name}_{attack}_{parameter}.wav", sr, noise)
        audio_data, sr = librosa.load(f"{out_dir}/{file_name}_{attack}_{parameter}.wav",sr = None)
        wav_file = f"{out_dir}/{file_name}_{attack}_{parameter}.wav"
    if attack == "recompression":
        recompression(audio_path, out_dir,out_dir,parameter)
        audio_data, sr = librosa.load("{}/{}_{}_{}.wav".format(out_dir,file_name,"recompression",parameter),sr = None)
        wav_file = "{}/{}_{}_{}.wav".format(out_dir,file_name,"recompression",parameter)
    if attack == "lpf":
        f = filtering(audio_data,sr)
        sf.write(os.path.join(out_dir, f'{file_name}_lpf_7000.wav'),f, sr,subtype='PCM_16')
        audio_data, sr = librosa.load(os.path.join(out_dir, f'{file_name}_lpf_7000.wav'),sr = None)
        wav_file = os.path.join(out_dir, f'{file_name}_lpf_7000.wav')
    if attack == "resample":
        resampled_audio = resampling(audio_path,int(parameter))
        sf.write(os.path.join(out_dir, f'{file_name}_resample_{str(parameter)}.wav'),resampled_audio, int(parameter),subtype='PCM_16')
        wav_file = os.path.join(out_dir, f'{file_name}_resample_{str(parameter)}.wav')

    return wav_file

def audio_laundering_cascading(audio_path,type_array): #["noise_parameter"]

    out_dir = config.out_dir
    out_dir_c = config.out_dir_chunks
    file_name_with_ext = os.path.basename(audio_path)
    file_name = file_name_with_ext.split(".")[0]
    fil_ext = file_name_with_ext.split(".")[1]
    audio_data, sr = librosa.load(audio_path,sr = None)
    
    for type in type_array:
        attack,parameter = str(type).split("_")
        if attack == "rt":
            room_reverb(audio_data, sr,float(parameter)).to_wav(
                f"{out_dir_c}/{file_name.split(".")[0]}_RT_{str(parameter).split(".")[0]}_{str(parameter).split(".")[1]}.wav",
                norm=True,
                bitdepth=np.int16,
            )
            wav_file = f"{out_dir_c}/{file_name.split(".")[0]}_RT_{str(parameter).split(".")[0]}_{str(parameter).split(".")[1]}.wav"
            audio_data, sr = librosa.load( f"{out_dir_c}/{file_name.split(".")[0]}_RT_{str(parameter).split(".")[0]}_{str(parameter).split(".")[1]}.wav",sr = None)
            
        if attack == "babble" or attack == "volvo" or attack == "white" or attack == "cafe" or attack == "street":
            noise = noise_add(f"noises/{attack}.wav",float(parameter),float(float(parameter)+0.5),audio_data,sr)
            wavf.write(f"{out_dir_c}/{file_name}_{attack}_{parameter}.wav", sr, noise)
            audio_data, sr = librosa.load(f"{out_dir_c}/{file_name}_{attack}_{parameter}.wav",sr = None)
            wav_file = f"{out_dir_c}/{file_name}_{attack}_{parameter}.wav"
        if attack == "recompression":
            recompression(audio_path, out_dir_c,out_dir_c,parameter)
            audio_data, sr = librosa.load("{}/{}_{}_{}.wav".format(out_dir_c,file_name,"recompression",parameter),sr = None)
            wav_file = "{}/{}_{}_{}.wav".format(out_dir_c,file_name,"recompression",parameter)
        if attack == "lpf":
            f = filtering(audio_data,sr)
            sf.write(os.path.join(out_dir_c, f'{file_name}_lpf_7000.wav'),f, sr,subtype='PCM_16')
            audio_data, sr = librosa.load(os.path.join(out_dir_c, f'{file_name}_lpf_7000.wav'),sr = None)
            wav_file = os.path.join(out_dir_c, f'{file_name}_lpf_7000.wav')
        if attack == "resample":
            resampled_audio = resampling(audio_path,int(parameter))
            sf.write(os.path.join(out_dir_c, f'{file_name}_resample_{str(parameter)}.wav'),resampled_audio, int(parameter),subtype='PCM_16')
            audio_data, sr = librosa.load(os.path.join(out_dir_c, f'{file_name}_resample_{str(parameter)}.wav'),sr = None)
            wav_file = os.path.join(out_dir_c, f'{file_name}_resample_{str(parameter)}.wav')
    sf.write(os.path.join(out_dir,f'{file_name}_resample_{str(parameter)}.wav'))
    return wav_file

if __name__ == '__main__':
    globals()[sys.argv[1]](sys.argv[2],sys.argv[3])