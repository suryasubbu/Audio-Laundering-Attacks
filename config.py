import os

def get_files(directory):
    flac_files = []
    
    # Walk through the directory
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.flac') or file.endswith('.wav') or file.endswith('.mp3'):
                flac_files.append(os.path.join(root, file))
    
    return flac_files

out_dir = "/data/ASV19/wav_paired_REV_LPF/"

#reverb parameters

reverb = [0.3,0.6,0.9]
noises =[[["white",0,0.5],["white",10,10.5],["white",20,20.5]],
         [["babble",0,0.5],["babble",10,10.5],["babble",20,20.5]],
         [["volvo",0,0.5],["volvo",10,10.5],["volvo",20,20.5]],
         [["cafe",0,0.5],["cafe",10,10.5],["cafe",20,20.5]],
         [["street",0,0.5],["street",10,10.5],["street",20,20.5]]]
recomp = ["16k","64k","128k","196k","256k","320k"]
fil = True
resample = [    11025 ,
        8000,
        22050,
        44100]