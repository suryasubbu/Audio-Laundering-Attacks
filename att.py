#!/usr/bin/env python3
from __future__ import print_function
import os
import sys
import glob
import argparse
import random

import pandas as pd
import librosa
import soundfile as sf
import pyroomacoustics as pra

# If these are your local modules, ensure they're in your PYTHONPATH or same folder.
import config
from laundering import room_reverb, noise_add, recompression, filtering, resampling
# Or, if you have a single 'laundering.py' that has everything, do:
#   from laundering import *

def choose_two_unique_values(arr):
    """
    Randomly choose two different items from arr that have different 
    'first names' (the string before the underscore).
    Prevent the combination (resample, lpf) or (lpf, resample).
    """
    # Splitting the array items to identify the first names
    first_names = [x.split("_")[0] for x in arr]

    # Create a dictionary to collect indices of the items
    first_name_dict = {}
    for idx, name in enumerate(first_names):
        if name not in first_name_dict:
            first_name_dict[name] = []
        first_name_dict[name].append(idx)

    # Create a list of indices from unique first names
    unique_first_names_indices = list(first_name_dict.values())

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
    """
    Decorator that suppresses print statements inside the wrapped function.
    """
    def func_wrapper(*args, **kwargs):
        # block all printing to the console
        original_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')
        try:
            value = func(*args, **kwargs)
        finally:
            # enable all printing to the console again
            sys.stdout.close()
            sys.stdout = original_stdout
        return value
    return func_wrapper

@blockPrinting
def audio_laundering(audio_path, attack_type):
    """
    Apply a specific laundering attack to 'audio_path' and save the result
    in config.out_dir. Returns the path to the laundered file.
    """
    out_dir = config.out_dir
    file_name_with_ext = os.path.basename(audio_path)
    file_name = file_name_with_ext.split(".")[0]
    fil_ext = file_name_with_ext.split(".")[1]

    audio_data, sr = librosa.load(audio_path, sr=None)

    attack, parameter = attack_type.split("_")
    # For debugging (won't show on console due to @blockPrinting):
    print("file:", file_name_with_ext, " attack:", attack, " parameter:", parameter)

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
            f"{out_dir}/{file_name}_RT_{param_main}_{param_dec}.wav",
            norm=True,
            bitdepth=pra.utilities.types.np.int16,  # or np.int16
        )
        wav_file = f"{out_dir}/{file_name}_RT_{param_main}_{param_dec}.wav"

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
        out_path = f"{out_dir}/{file_name}_{attack}_{parameter}.wav"
        sf.write(out_path, noise, sr, subtype='PCM_16')
        wav_file = out_path

    # 3. Recompression
    elif attack == "recompression":
        # e.g. "recompression_128"
        recompression(audio_path, out_dir, out_dir, parameter)
        wav_file = f"{out_dir}/{file_name}_recompression_{parameter}.wav"

    # 4. Low-Pass Filter
    elif attack == "lpf":
        # e.g. "lpf_7000"
        fdata = filtering(audio_data, sr)
        out_path = os.path.join(out_dir, f"{file_name}_lpf_{parameter}.wav")
        sf.write(out_path, fdata, sr, subtype='PCM_16')
        wav_file = out_path

    # 5. Resampling
    elif attack == "resample":
        # e.g. "resample_16000"
        new_sr = int(parameter)
        resampled_audio = resampling(audio_path, new_sr)
        out_path = os.path.join(out_dir, f"{file_name}_resample_{parameter}.wav")
        sf.write(out_path, resampled_audio, new_sr, subtype='PCM_16')
        wav_file = out_path

    # 6. Copy
    elif attack == "copy":
        # e.g. "copy_0" or "copy_anything"
        out_path = os.path.join(out_dir, f"{file_name}.wav")
        sf.write(out_path, audio_data, sr, subtype='PCM_16')
        wav_file = out_path

    return wav_file

def main():
    parser = argparse.ArgumentParser(
        description="Apply a specified laundering attack to all .flac files in a directory."
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
    parser.add_argument(
        "--attack", 
        required=True, 
        help=(
            "Laundering attack string of the form 'attack_param'. "
            "Examples: 'babble_0.5', 'lpf_7000', 'resample_16000', etc."
        )
    )
    args = parser.parse_args()

    # Update global config out_dir (if your config.py uses config.out_dir as the place to save outputs)
    config.out_dir = args.output_dir

    # Create output directory if it doesn't exist
    os.makedirs(args.output_dir, exist_ok=True)

    # Find all .flac files in input_dir
    flac_files = glob.glob(os.path.join(args.input_dir, "*.flac"))

    if not flac_files:
        print(f"No .flac files found in {args.input_dir}. Exiting...")
        sys.exit(0)

    for flac_path in flac_files:
        print(f"Processing: {flac_path} with attack='{args.attack}'")
        # Apply laundering
        output_file = audio_laundering(flac_path, args.attack)
        print(f"Saved laundered file to: {output_file}")

    print("All files processed successfully!")

if __name__ == "__main__":
    main()

"""
    python att.py \
    --input_dir /data/Data/AsvSpoofData_2019/train/LA/ASVspoof2019_LA_train/flac \
    --output_dir /data/ASV19/flac \
    --attack babble_0.5
"""

# python att.py --input_dir /data/Data/AsvSpoofData_2019/train/LA/ASVspoof2019_LA_train/flac --output_dir /data/ASV19/flac --attack babble_0.5