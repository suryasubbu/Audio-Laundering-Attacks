import random
import argparse
import os
import glob
import shutil
import librosa
import soundfile as sf
import pyroomacoustics as pra
from laundering import *
import config as config

# Parameters for each attack type
rt_params = ["rt_0.3", "rt_0.6", "rt_0.9"]
noises_random = [
    "white_0", "white_10", "white_20", "babble_0", "babble_10", "babble_20",
    "volvo_0", "volvo_10", "volvo_20", "cafe_0", "cafe_10", "cafe_20",
    "street_0", "street_10", "street_20"
]
recomp_params = [
    "recompression_16k", "recompression_64k", "recompression_128k",
    "recompression_196k", "recompression_256k", "recompression_320k"
]
filtering_param = ["lpf_7000"]
resample_params = ["resample_11025", "resample_8000", "resample_22050", "resample_44100"]

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
def audio_laundering(audio_path, attack_type): #["noise_parameter"]

    out_dir = config.out_dir + "/temp/"

    file_name_with_ext = os.path.basename(audio_path)
    file_name = file_name_with_ext.split(".")[0]
    
    fil_ext = file_name_with_ext.split(".")[1]
    audio_data, sr = librosa.load(audio_path,sr = None)
    attack,parameter = str(attack_type).split("_")
    print("file:",file_name_with_ext," attack:",attack," parameter:", parameter )

    # Initialize wav_file path (to be overwritten in each block)
    wav_file = None

    # 1. Reverberation ("rt")
    if attack == "rt":
        # e.g. "rt_0.5"
        rvb = room_reverb(audio_data, sr, float(parameter))
        # Save
        # Splitting parameter by '.' to preserve parts for the filename if needed
        param_parts = parameter.split(".")
        if len(param_parts) == 2:
            param_main, param_dec = param_parts
        else:
            param_main = parameter
            param_dec = "0"
        rvb.to_wav(
            f"{out_dir}/{file_name}_RT{param_main}{param_dec}.wav",
            norm=True,
            bitdepth=np.int16,  # or np.int16
        )
        wav_file = f"{out_dir}/{file_name}_RT{param_main}{param_dec}.wav"

    # 2. Adding Noise
    elif attack in ["babble", "volvo", "white", "cafe", "street"]:
        # e.g. "babble_0.5"
        noise = noise_add(
            f"noises/{attack}.wav",
            float(parameter),
            float(float(parameter) + 0.5),
            audio_data,
            sr
        )
        out_path = f"{out_dir}/{file_name}_{attack}{parameter}.wav"
        sf.write(out_path, noise, sr, subtype='PCM_16')
        wav_file = out_path

    # 3. Recompression
    elif attack == "recompression":
        # e.g. "recompression_128"
        recompression(audio_path, out_dir, out_dir, parameter)
        wav_file = f"{out_dir}/{file_name}_recompression{parameter}.wav"

    # 4. Low-Pass Filter
    elif attack == "lpf":
        # e.g. "lpf_7000"
        fdata = filtering(audio_data, sr)
        out_path = os.path.join(out_dir, f"{file_name}_lpf{parameter}.wav")
        sf.write(out_path, fdata, sr, subtype='PCM_16')
        wav_file = out_path

    # 5. Resampling
    elif attack == "resample":
        # e.g. "resample_16000"
        new_sr = int(parameter)
        resampled_audio = resampling(audio_path, new_sr)
        out_path = os.path.join(out_dir, f"{file_name}_resample{parameter}.wav")
        sf.write(out_path, resampled_audio, new_sr, subtype='PCM_16')
        wav_file = out_path

    # 6. Copy
    elif attack == "copy":
        # e.g. "copy_0" or "copy_anything"
        out_path = os.path.join(out_dir, f"{file_name}.wav")
        sf.write(out_path, audio_data, sr, subtype='PCM_16')
        wav_file = out_path

    return wav_file

def generate_protocol_file(output_file_name, attacks_list):
    protocol_file_path = "/data/ASV19_lekha_test/cascaded_ASV19.txt" #file path for protocol file
    data = []
    file = output_file_name.replace(".wav", "")
    #remove the preceding folder paths
    file_name = file.split('/')[-1]
    # Split the file name by '_'
    parts = file_name.split('_')
    
    # Extract the audioname (first three parts)
    audioname = '_'.join(parts[:3])
    
    # Extract the attack_type (remaining parts)
    data.append({"audioname":audioname, 
                 "adapted": file_name.split(".")[0], 
                 "attack_1": attacks_list[0],
                 "attack_2": attacks_list[1],
                 "attack_3": attacks_list[2],
                 "attack_4": attacks_list[3],
                 "attack_5": attacks_list[4]
                 })
    prot = pd.read_csv("/data/Data/AsvSpoofData_2019/train/LA/ASVspoof2019_LA_cm_protocols/ASVspoof2019.LA.cm.train.trn.txt",sep=" ")
    prot.columns = ["tag","audioname","gender","attack","spoof"]
    result_df = pd.DataFrame(data)
    prot_casc = prot.merge(result_df,how = "inner",on = "audioname")
    prot_casc["type"]="cascaded"

    # Select and format columns to save
    columns_to_save = ["tag", "adapted", "gender", "attack", "spoof", "type","attack_1", "attack_2", "attack_3","attack_4", "attack_5"]

    # Check if the protocol file already exists
    file_exists = os.path.isfile(protocol_file_path)

    # Append to the protocol file without overwriting
    prot_casc[columns_to_save].to_csv(
        protocol_file_path,
        index=False,
        sep=" ",
        header=not file_exists,  # Write header only if file does not exist
        mode='a'  # Append mode
    )
    print(f"Updated protocol file: {protocol_file_path}")


def cascaded_audio_laundering(audio_path):
    """
    Perform cascading attacks on the input audio file.
    The attacks are applied in the order: rt -> noise -> recompression -> lpf -> resample.
    """
    out_dir = config.out_dir
    file_name_with_ext = os.path.basename(audio_path)
    file_name = file_name_with_ext.split(".")[0]
    attacked_params_list = []
    
    for attack_type, params in [
        ("rt", rt_params),
        ("noise", noises_random),
        ("recompression", recomp_params),
        ("lpf", filtering_param),
        ("resample", resample_params)
    ]:
        # Randomly select a parameter for the current attack
        selected_param = random.choice(params)
        attack_param = selected_param
        print(f"Applying {attack_type} with parameter: {selected_param}")
        
        # Apply the laundering attack
        processed_audio_path = audio_laundering(audio_path, selected_param)
        
        if processed_audio_path is None or not os.path.exists(processed_audio_path):
            print(f"Error applying {attack_type} with parameter {selected_param}. Skipping...")
            break
        
        attacked_params_list.append(selected_param)
        audio_path = processed_audio_path

    if len(attacked_params_list) == 5:

        # Generate the final output file name
        final_output_file_name = processed_audio_path.split('/')[-1]
        final_output_path = os.path.join(config.out_dir, final_output_file_name)

        #Move cascaded laundered file to output folder
        try:
            shutil.move(processed_audio_path, final_output_path)
            print(f"Moved file from {processed_audio_path} to {final_output_path}")
        except Exception as e:
            print(f"Error moving file: {e}")

        generate_protocol_file(processed_audio_path, attacked_params_list)    

        return processed_audio_path
    else:
        print("There was error in generating cascaded file")

def main():
    parser = argparse.ArgumentParser(
        description="Apply cascading laundering attacks to all .flac files in a directory."
    )
    parser.add_argument(
        "--input_dir", 
        required=True, 
        help="Path to the directory containing .flac files."
    )
    parser.add_argument(
        "--output_dir", 
        required=True, 
        help="Path to the directory where processed files will be saved."
    )
    
    args = parser.parse_args()

    # Update global config out_dir
    config.out_dir = args.output_dir

    # Create output directory if it doesn't exist
    os.makedirs(args.output_dir, exist_ok=True)
    os.makedirs(args.output_dir + "/temp", exist_ok=True) # create temp folder too to store temporary audio files

    protocol_file_path = "/data/ASV19_lekha_test/cascaded_ASV19.txt"
    # Load already processed file names from the protocol file
    if os.path.exists(protocol_file_path):
        protocol_df = pd.read_csv(protocol_file_path, sep=" ", usecols=["adapted"])
        import pdb; pdb.set_trace()
        processed_files = set(protocol_df["adapted"].str.split("_").apply(lambda x: "_".join(x[:3])))

    else:
        processed_files = set()
        print(f"Protocol file not found. Processing all files...")

    # Find all .flac files in input_dir
    flac_files = glob.glob(os.path.join(args.input_dir, "*.flac"))

    if not flac_files:
        print(f"No .flac files found in {args.input_dir}. Exiting...")
        return

    for flac_path in flac_files:
        file_name = os.path.basename(flac_path).split(".")[0]
        if file_name in processed_files:
            print(f"Skipping already processed file: {file_name}.flac")
            continue

        print(f"Processing: {flac_path}")
        cascaded_audio_laundering(flac_path)

    print("All files processed successfully!")

if __name__ == "__main__":
    main()
