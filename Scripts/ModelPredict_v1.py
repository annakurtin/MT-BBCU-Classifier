import opensoundscape
from opensoundscape.ml.cnn import load_model
from opensoundscape import Audio
# Other utilities and packages
import torch
from pathlib import Path
import numpy as np
import pandas as pd
from glob import glob
import subprocess
import time
import os
import streamlit as st

'''
# Script to run BBCU Model 2.0 

'''

# Establish year and collabroator
year = st.text_input("Enter the year the data was collected", "")
if year:
    if (year.isnumeric()):
        st.success("Success!")
    else:
        st.warning("You have not input a numeric value for year")

collab = st.radio("Select Collaborator: ", ('UMBEL', 'FWP'))
if (collab == 'UMBEL'):
    region = " "
elif (collab == 'FWP'):
    region = st.text_input("Please enter the region (ex 6):")
    if region:
        if not (region.isnumeric()):
            st.warning("You have not input a numeric value for the region")
if year and region:
    st.write("Currently running", collab, "region",region, year, "data")


# Establish paths
# Path to audio to run on
#audio_file_location = st.text_input("Please enter the path to the folder of audio files") 
# Figure this out later
audio_file_location = "D:/Test_Files_M2.0GUI/2022_UMBEL/82-1"

# Path to .csv of files to exclude 
#files_to_exclude = st.text_input("Please enter the path to a .csv file containing the IDs of files to exclude from analysis") 
# Figure this out later
files_to_exclude = "D:/CNN/Model_FilestoExclude_forGUI/2022_UMBEL_IncorrectSizeAcousticFiles.csv"

# Specify the path to the model
# This shouldn't need changing
model_path = "D:/CNN/Model_FilestoExclude_forGUI/epoch-10_opso-0-10-1.model"

# Specify path to output for clips
#outputs_path = st.text_input("Please enter the path to the folder where you want the .csv from the machine learning model to be written") 
outputs_path = 'D:/Test_Files_M2.0GUI/Test_Scores_Output'


# Read in audio files and exclude the ones you want to leave out
#audio_files_list = list(glob(audio_file_location + "/*/*.[wW][aA][vV]"))
audio_files_list = list(glob(audio_file_location + "/*.[wW][aA][vV]"))
audio_files = pd.DataFrame(audio_files_list, columns=["file"])
#st.write(audio_files.head(10))
# Read files to exclude
exclude_data = pd.read_csv(files_to_exclude)
# Convert all file names to upper case to catch .wav and .WAV
exclude_data['File_Name'] = exclude_data['File_Name'].str.upper()
# st.write(exclude_data.head(10))
# working fine
exclude_files = exclude_data['File_Name'].tolist()
# Create a new column 'file_name' in audio_files
audio_files['file_name'] = audio_files['file'].apply(lambda x: Path(x).name) # used to be .stem
# convert the file_name to filter into upper case to catch .WAV vs .wav
audio_files['file_name'] = audio_files['file_name'].str.upper()

# Filter out files based on 'file_name'
audio_files = audio_files[~audio_files['file_name'].isin(exclude_files)]
# Set 'file' as the index in audio_files_filtered
audio_files.set_index('file', inplace=True)
# Remove the 'file_name' column from audio_files_filtered
audio_files.drop('file_name', axis=1, inplace=True)

# try writing the updated audio_files to a local directory 
output_name = "test_output.csv"
output_file_path = os.path.join(outputs_path, output_name)
#st.write(audio_files.head(10))
#audio_files.to_csv(output_file_path)


# Run the model    
model = load_model(model_path)

# Spectrogram preprocessing
model.preprocessor.pipeline.load_audio.set(sample_rate=11025)
model.preprocessor.pipeline.bandpass.set(min_f=200, max_f=3500)
model.preprocessor.pipeline.to_spec.set(window_samples=512, overlap_samples=256)
model.preprocessor.pipeline.frequency_mask.bypass = True
st.write("Loaded model and configured preprocessing of spectrogram")

if(st.button("Click Here to Run BBCU Model 2.0 On Selected Data")):
    with st.spinner("Running classifier...", show_time=True):
        scores = model.predict(audio_files)
    st.success("Classifier run complete!")
    scores.to_csv(output_file_path)

# Old code
_ = '''
#print("Shape of scores:", scores.shape)

# Specify the path and name for the scores
output_file_path = os.path.join(outputs_path, f"predictions_{os.path.basename(model_path).split('.')[0]}-{os.path.basename(audio_file_location)}.csv")
# Write the scores to a .csv in this location
scores.to_csv(output_file_path)

st.text("Done!")
'''