# Laundering Attacks for Synthetic Audios
This repository contains all the laundering attacks done code for the paper titled "Is Audio Spoof Detection Robust to Laundering Attacks?". 

Code Authors: Surya Subramani, Hashim Ali, Raksha Varahamurthy, Shefali Gokrn

# types of laundering attacks
Format = "attack_param"
## reverberation
1) rt_0.3
2) rt_0.6
3) rt_0.9
## noise
1) babble_0 or babble_10 or babble_20
2) volvo_0 or volvo_10 or volvo_20
3) white_0 or white_10 or white_20
4) street_0 or street_10 or street_20
5) cafe_0 or cafe_10 or cafe_20
## low pass filtering
1) lpf_7000
## resampling
1) resample_22050 or resample_44100 or resample_8000 or resample_11025
## recompression
1) recompression_128k or recompression_64k or recompression_196k or recompression_64k or recompression_16k or recompression_256k or recompression_320k

1) ```bash
   pip install -r requirements.txt 
2) ```bash
   python main.py audio_laundering "audio_path" "attack_param"
3)check the output folder you will find the laundered audios with the respective suffix


This repo is done for the research work submitted to 
