# Laundering Attacks for Synthetic Audios
This repository contains all the laundering attacks done code for the paper titled "Is Audio Spoof Detection Robust to Laundering Attacks?". 
## Introduction

Laundering attacks on synthetic audios pose significant challenges in the realm of audio forensics and security. These attacks manipulate audio signals to evade detection systems, rendering synthetic audios nearly indistinguishable from authentic recordings. Key laundering techniques include reverberation, noise addition, resampling, recompression, and low pass filtering. Understanding these methods is crucial for developing robust detection mechanisms.

## Reverberation

Reverberation involves adding echoes to an audio signal, mimicking the natural reflections of sound in an environment. This technique can obscure artifacts of synthetic audio, making it harder to detect alterations. By simulating different acoustic environments, reverberation can effectively disguise synthetic origins, complicating the task for detection algorithms that rely on pristine audio characteristics.

## Noise Addition

Adding noise to an audio signal can mask the peculiarities of synthetic audio. This noise can be white, pink, or environmental sounds like street noise or chatter. Noise addition disrupts the clean, often too-perfect quality of synthetic audios, blending them more convincingly with real-world recordings. This technique not only hides synthetic traces but also tests the robustness of detection systems against varied and unpredictable noise patterns.

## Resampling

Resampling alters the audio sample rate, which can distort the signal slightly but enough to evade detection mechanisms. By changing the original sample rate, resampling modifies the spectral content and temporal features of the audio. This process can obscure synthetic fingerprints, as many detection algorithms depend on consistent sample rates and associated patterns to identify tampered audio.

## Recompression

Recompression involves re-encoding the audio signal using different codecs or compression settings. This method introduces compression artifacts and changes the signal’s characteristics, which can mask synthetic features. By recompressing synthetic audio, attackers can exploit the compression process to hide traces of synthesis, challenging detection systems that rely on identifying typical artifacts of audio synthesis.

## Low Pass Filtering

Low pass filtering removes high-frequency components from an audio signal, which can effectively disguise high-frequency artifacts common in synthetic audios. By smoothing out the audio, low pass filtering can make synthetic signals appear more natural and less detectable. This technique targets the high-frequency inconsistencies often present in synthetic audios, thereby evading detection algorithms that focus on these anomalies.

![Block Diagram](https://github.com/suryasubbu/Audio-Laundering-Attacks/assets/78839425/6e356e18-536a-43a0-a15d-e6959df9f2b3)



# Steps to add laundering attacks to synthetic audio

1) Give your audio directory path to the "audio_path" variable in config.py
2) ```bash
   python main.py
3)check the output folder you will find the laundered audios with the respective suffix


This repo is done for the research work submitted to 
