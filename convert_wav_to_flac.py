import os
import shutil
import argparse
from pydub import AudioSegment

def convert_wav_to_flac(input_folder, output_folder):
    """
    Converts .wav files in the input folder to .flac format and
    moves them to the specified output folder.

    Args:
        input_folder (str): Path to the folder containing .wav files.
        output_folder (str): Path to the folder where .flac files will be saved.
    """
    # Ensure the output folder exists
    os.makedirs(output_folder, exist_ok=True)

    # List all .wav files in the input folder
    wav_files = [f for f in os.listdir(input_folder) if f.endswith(".wav")]

    if not wav_files:
        print(f"No .wav files found in {input_folder}.")
        return
    
    # List all existing .flac files in the output folder
    existing_flac_files = set(
        os.path.splitext(f)[0] for f in os.listdir(output_folder) if f.endswith(".flac")
    )

    for wav_file in wav_files:
        # Define input and output file paths
        wav_path = os.path.join(input_folder, wav_file)
        flac_file = os.path.splitext(wav_file)[0] + ".flac"
        flac_path = os.path.join(output_folder, flac_file)

         # Check if the corresponding .flac file already exists
        if os.path.splitext(wav_file)[0] in existing_flac_files:
            print(f"Skipping {wav_file}, already converted.")
            continue

        try:
            # Load .wav file and export as .flac
            audio = AudioSegment.from_wav(wav_path)
            audio.export(flac_path, format="flac")
            print(f"Converted {wav_file} to {flac_file}.")
        except Exception as e:
            print(f"Error converting {wav_file}: {e}")

    print(f"All .wav files have been converted and moved to {output_folder}.")

def main():
    parser = argparse.ArgumentParser(
        description="Convert .wav files in input folder to .flac files in the output folder"
    )
    parser.add_argument(
        "--input_dir", 
        required=True, 
        help="Path to the directory containing .wav files."
    )
    parser.add_argument(
        "--output_dir", 
        required=True, 
        help="Path to the directory where .flac files need to be saved."
    )
    
    args = parser.parse_args()
    input_folder = args.input_dir
    output_folder = args.output_dir
    convert_wav_to_flac(input_folder, output_folder)

# Example usage
if __name__ == "__main__":
    main()
    
    
