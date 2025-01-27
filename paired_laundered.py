import os
import random
import argparse
import librosa
import glob
import shutil
import soundfile as sf
from laundering import *  # Import the laundering functions
import config as config

def apply_laundering(audio_path, attack_type):
    """
    Apply a specific laundering attack to an audio file.

    Args:
        audio_path (str): Path to the audio file.
        attack_type (str): The type of attack to apply.
        attack_param (str): The parameter for the attack.

    Returns:
        str: Path to the processed audio file.
    """

    out_dir = config.out_dir + "/temp/"

    file_name_with_ext = os.path.basename(audio_path)
    file_name = file_name_with_ext.split(".")[0]

    audio_data, sr = librosa.load(audio_path, sr=None)
    attack,parameter = str(attack_type).split("_")
    # 1. Reverberation ("rt")
    if attack == "rt":
        param_parts = parameter.split(".")
        if len(param_parts) == 2:
            param_main, param_dec = param_parts
        else:
            param_main = parameter
            param_dec = "0"

        rvb = room_reverb(audio_data, sr, float(parameter))
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

def generate_protocol_file(output_file_name, first_attack, second_attack, protocol_file_path):
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
                 'adapted': file_name.split(".")[0],
                  'attack_1': first_attack,
                  "attack_2": second_attack})
    prot = pd.read_csv("/data/Data/AsvSpoofData_2019/train/LA/ASVspoof2019_LA_cm_protocols/ASVspoof2019.LA.cm.train.trn.txt",sep=" ")
    prot.columns = ["tag","audioname","gender","attack","spoof"]
    result_df = pd.DataFrame(data)
    prot_stoc = prot.merge(result_df,how = "inner",on = "audioname")
    prot_stoc["type"]="paired"

    # Select and format columns to save
    columns_to_save = ["tag", "adapted", "gender", "attack", "spoof", "type", "attack_1", "attack_2"]

    # Check if the protocol file already exists
    file_exists = os.path.isfile(protocol_file_path)

    # Append to the protocol file without overwriting
    prot_stoc[columns_to_save].to_csv(
        protocol_file_path,
        index=False,
        sep=" ",
        header=not file_exists,  # Write header only if file does not exist
        mode='a'  # Append mode
    )
    print(f"Updated protocol file: {protocol_file_path}")


def paired_laundering(audio_path, first_attack, second_attack, protocol_file_path):
    """
    Apply paired laundering attacks to an audio file.

    Args:
        audio_path (str): Path to the audio file.
        first_attack (str): The type of the first laundering attack.
        second_attack (str): The type of the second laundering attack.

    Returns:
        None
    """
    attack_params = {
        "REV": ["rt_0.3", "rt_0.6", "rt_0.9"],
        "AN": ["white_0", "white_10", "white_20", "babble_0", "babble_10", "babble_20",
    "volvo_0", "volvo_10", "volvo_20", "cafe_0", "cafe_10", "cafe_20",
    "street_0", "street_10", "street_20"],
        "REC": ["recompression_16k", "recompression_64k", "recompression_128k", "recompression_196k", "recompression_256k", "recompression_320k"],
        "LPF": ["lpf_7000"],
        "RES": ["resample_11025", "resample_8000", "resample_22050", "resample_44100"]
    }
    out_dir = config.out_dir
    file_name_with_ext = os.path.basename(audio_path)
    file_name = file_name_with_ext.split(".")[0]
    # Select random parameters for each attack
    first_param = random.choice(attack_params[first_attack])
    second_param = random.choice(attack_params[second_attack])

    print(f"Applying {first_attack} with parameter {first_param}.")
    intermediate_file = apply_laundering(audio_path, first_param)

    print(f"Applying {second_attack} with parameter {second_param}.")
    final_file = apply_laundering(intermediate_file, second_param)
    if final_file is None or not os.path.exists(final_file):
            print(f"Error applying {second_attack} with parameter {second_param}. Skipping...")

    else:
        # Generate the final output file name
        final_output_file_name = final_file.split('/')[-1]
        final_output_path = os.path.join(config.out_dir, final_output_file_name)

    #Move cascaded laundered file to output folder
    try:
        shutil.move(final_file, final_output_path)
        print(f"Moved file from {final_file} to {final_output_path}")
    except Exception as e:
        print(f"Error moving file: {e}")

    generate_protocol_file(final_file, first_param, second_param, protocol_file_path)    
    return final_file

def main():
    parser = argparse.ArgumentParser(description="Apply paired laundering attacks to an audio file.")
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
    parser.add_argument("--first_attack", required=True, help="Type of the first laundering attack.", choices = ["REV","AN","REC","LPF","RES"])
    parser.add_argument("--second_attack", required=True, help="Type of the second laundering attack.", choices = ["REV","AN","REC","LPF","RES"])
    parser.add_argument("--protocol_file", required=True, help="Path of the Protocol file")
    args = parser.parse_args()

    # Update global config out_dir (if your config.py uses config.out_dir as the place to save outputs)
    config.out_dir = args.output_dir

    # Create output directory if it doesn't exist
    os.makedirs(args.output_dir, exist_ok=True)
    os.makedirs(args.output_dir + "/temp", exist_ok=True) # create temp folder too to store temporary audio files

    protocol_file_path = args.protocol_file
    # Load already processed file names from the protocol file
    if os.path.exists(protocol_file_path):
        protocol_df = pd.read_csv(protocol_file_path, sep=" ", usecols=["adapted"])
        processed_files = set(protocol_df["adapted"].str.split("_").apply(lambda x: "_".join(x[:3])))

    else:
        processed_files = set()
        print(f"Protocol file not found. Processing all files...")

    # Find all .flac files in input_dir
    flac_files = glob.glob(os.path.join(args.input_dir, "*.flac"))

    if not flac_files:
        print(f"No .flac files found in {args.input_dir}. Exiting...")
        sys.exit(0)

    for flac_path in flac_files:
        file_name = os.path.basename(flac_path).split(".")[0]
        if file_name in processed_files:
            print(f"Skipping already processed file: {file_name}.flac")
            continue
        print(f"Processing: {flac_path} with a paired attacks {args.first_attack} and {args.second_attack}")
        paired_laundering(flac_path , args.first_attack, args.second_attack, protocol_file_path)

    print("All files processed successfully!")

if __name__ == "__main__":
    main()

# python paired_laundered.py  --input_dir /data/Data/AsvSpoofData_2019/train/LA/ASVspoof2019_LA_train/flac --output_dir /data/ASV19_lekha_test/paired/wav_REC_RES --first_attack REC --second_attack RES --protocol_file /data/ASV19_lekha_test/paired_REC_RES.txt