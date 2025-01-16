from __future__ import print_function
import pandas as pd
import librosa
import soundfile as sf
import pyroomacoustics as pra
from laundering import *
import config as config
import sys, os
import random
# decorater used to block function printing to the console
def choose_two_unique_values(arr):
    # Splitting the array items to identify the first names(parts before the first underscore)
    first_names = [x.split("_")[0] for x in arr]

    # Create a dictionary to collect indices of the items
    first_name_dict = {}
    for idx, name in enumerate(first_names):
        if name not in first_name_dict:
            first_name_dict[name] = []
        first_name_dict[name].append(idx)

    # Create a list of indices from unique first names
    unique_first_names_indices = []
    for indices in first_name_dict.values():
        unique_first_names_indices.append(indices)

    while True:
        # Randomly select two different unique groups
        choice_one = random.choice(unique_first_names_indices)
        choice_two = random.choice([x for x in unique_first_names_indices if x != choice_one])

        # Randomly select one item from each chosen group
        selection_one = arr[random.choice(choice_one)]
        selection_two = arr[random.choice(choice_two)]

        # Extract the first names again to check the condition
        first_name_one = selection_one.split('_')[0]
        first_name_two = selection_two.split('_')[0]

        # Check that resampling and lpf do not pair up
        if not ((first_name_one == "resample" and first_name_two == "lpf") or
                (first_name_one == "lpf" and first_name_two == "resample")):
            return selection_one, selection_two
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
        wav_file = f"{out_dir}{file_name.split(".")[0]}_RT_{str(parameter).split(".")[0]}_{str(parameter).split(".")[1]}.wav"
        audio_data, sr = librosa.load( f"{out_dir}/{file_name.split(".")[0]}_RT_{str(parameter).split(".")[0]}_{str(parameter).split(".")[1]}.wav",sr = None)
    
    if attack == "babble" or attack == "volvo" or attack == "white" or attack == "cafe" or attack == "street":
        noise = noise_add(f"noises/{attack}.wav",float(parameter),float(float(parameter)+0.5),audio_data,sr)
        wavf.write(f"{out_dir}/{file_name}_{attack}_{parameter}.wav", sr, noise)
        audio_data, sr = librosa.load(f"{out_dir}/{file_name}_{attack}_{parameter}.wav",sr = None)
        wav_file = f"{out_dir}{file_name}_{attack}_{parameter}.wav"
    if attack == "recompression":
        recompression(audio_path, out_dir,out_dir,parameter)
        audio_data, sr = librosa.load("{}/{}_{}_{}.wav".format(out_dir,file_name,"recompression",parameter),sr = None)
        wav_file = "{}{}_{}_{}.wav".format(out_dir,file_name,"recompression",parameter)
    if attack == "lpf":
        f = filtering(audio_data,sr)
        sf.write(os.path.join(out_dir, f'{file_name}_lpf_7000.wav'),f, sr,subtype='PCM_16')
        audio_data, sr = librosa.load(os.path.join(out_dir, f'{file_name}_lpf_7000.wav'),sr = None)
        wav_file = os.path.join(out_dir, f'{file_name}_lpf_7000.wav')
    if attack == "resample":
        resampled_audio = resampling(audio_path,int(parameter))
        # sf.write(os.path.join(out_dir, f'{file_name}_resample_{str(parameter)}.wav'),resampled_audio, int(parameter),subtype='PCM_16')
        sf.write(os.path.join(out_dir, f'{file_name}_resample_{str(parameter)}.wav'),resampled_audio, int(parameter),subtype='PCM_16')
        wav_file = os.path.join(out_dir, f'{file_name}_resample_{str(parameter)}.wav')

    if attack == "copy":
        wavf.write(f"{out_dir}/{file_name}.wav", sr, audio_data)
        wav_file = f"{out_dir}/{file_name}.wav"
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
            rtt = f"RT_{str(parameter).split(".")[0]}_{str(parameter).split(".")[1]}"
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
    # globals()[sys.argv[1]](sys.argv[2],sys.argv[3])
    def get_files(directory):
        flac_files = []
        
        # Walk through the directory
        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith('.flac') or file.endswith('.wav') or file.endswith('.mp3'):
                    flac_files.append(os.path.join(root, file))
        
        return flac_files

    audio_path = get_files("/data/asv_spoof_challenge/flac_T/")
    # aa = np.random.choice(audio_path,size = round(len(audio_path)*0.2),replace=False)
    aa = np.array(audio_path)
    prot = pd.read_csv("/data/asv_spoof_challenge/ASVspoof5_train_metadata.txt",sep=" ")
    prot.columns = ["tag","audioname","gender","ifen","stag","spoof"]
    pdd = pd.DataFrame(aa)
    pdd.columns = ["path"]
    pdd[["","","","","filename"]] = pdd['path'].str.split('/', expand=True)
    pdd[["audioname","format"]] = pdd['filename'].str.split('.', expand=True)
    big = pdd.merge(prot, how = "inner", on = "audioname")
    print(big.drop_duplicates().shape)
    att_type = "Reverberation"
    par_array = np.array(["rt_0.3","rt_0.6","rt_0.9"])
    big.drop_duplicates("audioname",inplace=True)
    print(big.columns,big.shape)
    big[["tag","audioname","gender","ifen","stag","spoof","path"]].to_csv("/data/asv_spoof_challenge/ASVspoof5_train_metadata_20_path.txt",index = False,sep = " ",header= None)
    for index,row in big.iterrows():
        par_choice = np.random.choice(par_array)
        print(row["audioname"],par_choice,att_type)

    # meta_data = pd.read_csv("/data/asv_spoof_challenge/ASVspoof5_train_metadata_20_path.txt",sep = " ")
    # meta_data.columns = ["tag","audioname","gender","ifen","stag","spoof","path"]
    # att_type = "Resampling"
    # par_array = np.array(["resample_11025" ,
    #     "resample_8000",
    #     "resample_22050",
    #     "resample_44100","rt_0.3","rt_0.6","rt_0.9",
    #     "babble_10","babble_20",
    #     "white_10","white_20",
    #     "volvo_10","volvo_20",
    #     "street_10","street_20",
    #     "cafe_10","cafe_20",
    #     "lpf_7000","recompression_16k","recompression_64k","recompression_128k","recompression_196k","recompression_256k",
    #     "recompression_320k"])
    # meta_data["attack"]= att_type
    # # b = []
    # for index,row in meta_data.iterrows():
    #     val1, val2 = choose_two_unique_values(par_array)
    #     val = np.array([val1,val2])
    #     # par_choice = 
    #     v = row["path"]
    #     for par_choice in val:
    #         print(v)
    #         aa = v
    #         v = audio_laundering(v, par_choice)
    #     os.remove(aa)
    #     print("removed", aa)
    #     # a_name = f"{row["audioname"]}_{par_choice}"
    #     print(v)
    #     # b.append([row["audioname"],par_choice])
    # # g = pd.DataFrame(b)
    # # g.columns = ["audioname","adapted","par"]
    # # print(g)
    # # big = g.merge(meta_data,how = "inner",on = "audioname")
    # # big[["tag","adapted","gender","ifen","stag","spoof","attack","par"]].to_csv("/data/asv_spoof_challenge/ASVspoof5_train_metadata_20_path_copy.txt",index = False,sep = " ",header= None)



