''' 
Clip Extraction Code
This is a script to extract top scoring clips from each site. The output will give you the scripts to run the listening_notebook code on to annotate the clips for cuckoo presence. 

Copied from script of same name from model 1.0 files 1/11/2024
Last edited 2/19/2024
'''

from opensoundscape.audio import Audio
#from opensoundscape.helpers import hex_to_time
import pandas as pd
from glob import glob
import subprocess
import os
from os.path import exists
from datetime import date
import numpy as np

# Suppress userwarnings about metadata
#Warning.filterwarnings("ignore", category=UserWarning)

# Establish which dataset you're working on and where the metadata is
# Take this from the already established user input
year = '2021' # Format YYYY
collab = 'UMBEL' # Format UMBEL or FWPR#
metadata = st.file_uploader("Upload a .csv file containing file IDs to exclude", type=['csv'])
# Establish the file path for the metadata folder
#### Change to user selected file **********************************
#metad_path = 'C:/Users/ak201255/Documents/Cuckoo-Research/Data/Metadata/Outputs/'
#metad_file = '2021_ARUDeployment_Retrieval_Metadata_UMBEL_Cleaned2-21.csv'
# 2022 UMBEL:'2022_ARUDeployment_Retrieval_Metadata_UMBEL_Cleaned1-22.csv'
# 2021: '2021_ARUDeployment_Retrieval_Metadata_UMBEL_Cleaned1-22.csv'
# 2022 FWP:'2022_ARUDeployment_Retrieval_Metadata_FWPALL_Cleaned1-22.csv'
# 2023 Data:'2023_ARUDeployment_MetadataFull_Cleaned10-24.csv'
# SHOULDN'T HAVE TO EDIT BELOW THIS LINE


# Establish which dataset you're working with 
dataset = f'{year}_{collab}'
print(dataset)

# Later should only have to change E: to F: to run on Ery
# Establish the file path for the scores ###### CHANGE THIS BACK #####
### Use the scores data that's already present *******************************
score_path = f'F:/CNN_Classifier_Files/Model_2.0/Model_Scores/predictions_epoch-10_opso-0-10-1-{year}_{collab}_Audio.csv'
# Establish the file path for where the clips will go
clips_path = f'F:/Cuckoo_Acoustic_Data/{year}/{year}_{collab}_Data/{year}_{collab}_Clips/'
# Establish the file path for the folder with all the audio files
audio_path = f'F:/Cuckoo_Acoustic_Data/{year}/{year}_{collab}_Data/{year}_{collab}_Audio/'
# User input multi select for classes **************************************
# Establish which classes you are annotating
classes = ['cadence_coo','rattle']

# Read in the csv for the location IDs
metadata = pd.read_csv(metad_path+metad_file, encoding= 'unicode_escape')
# change all column names to upper case
# Do a file upload for the metadata? ******************************
# Take the column labeled 'point_ID' and put it into a list [with tolist()] that is sorted in orde [with sorted()], then converted to a set of iterable elements [with set()]
locs_list = sorted(set(metadata['point_id'].tolist()))

print("The current scores file is",score_path)
# Pull the scores into a dataframe
sf = pd.read_csv(score_path)
# Change all values of \ in the file column of sf to / 
sf['file'] = sf['file'].str.replace("\\","/")
#print("Scores file:")
#print(sf['file'])

# make a new column called point_id from the string after the second / in the file column 
sf['point_id'] = sf['file'].apply(lambda x: x.split('/')[-2] if isinstance(x, str) else None)
# Extract the point IDs from the first column in the scores file and create a list of unique ones 
point_list = list(set(sf['point_id']))
print("List of points:",point_list)

# Format the scores file 
# Make a column for date
sf['date'] = [(d.split('_')[-2]) for d in sf['file'].tolist()]
#print(sf.dtypes)
sf['date'] = pd.to_numeric(sf['date'])
# print(sf.dtypes['date']) # This is now a number
# Filter out only the dates that fall within the time period
# transform to numeric, pick out only the files that are greater than 20230601 and less than 20230815
#### User input of date ranges, then format them together
first_date = int(f'{year}0601')
last_date = int(f'{year}0815')
sf = sf.loc[(sf['date'] >= first_date) & (sf['date'] <= last_date)]
#print(max(sf['date']))
#print(min(sf['date'])) # This looks like it's working fine

# Convert date to a string for later
sf['date'] = sf['date'].astype(str)
# Make a column for the hour of the recording
sf['hour'] = [(d.split('_')[-1].split('.')[0]) for d in sf['file'].tolist()]
# Convert hour to an integer
sf['hour'] = sf['hour'].astype(int)
# Make a new column for diurnal or nocturnal time period
sf['time_period'] = np.where((sf['hour'] == 70000) | (sf['hour'] == 90000), 'diurnal', 
                             np.where((sf['hour'] == 230000) | (sf['hour'] == 10000), 'nocturnal', 'unknown'))
# Drop any files that are outside of the established time period
sf.drop(sf[sf['time_period'] == 'unknown'].index, inplace=True)
# Make a column specifying the species
sf['species'] = "BBCU"
# Order the columns
sf = sf[['file', 
         'date',
         'hour',
         'time_period',
         'point_id',
         'start_time',
         'end_time',
         'species',
         'cadence_coo',
         'rattle']]
# make a clean index column
sf = sf.reset_index(drop=True)


#print(sf.head())
# Make a folder for the clips to go into
big_folder = clips_path+dataset+'_topclip_perperiod'
# Check if this folder exists and if not, make it
if not os.path.exists(big_folder):
    os.makedirs(big_folder)

# Initialize an empty dataframe for this dataset
dataset_df = pd.DataFrame()


# Iterate through each point in the point_list
for point in point_list:
    # Initialize an emtpy dataframe for this point
    keep_df = pd.DataFrame()
    # Initialize a folder relating the class to the location you're looking at
    folder = clips_path + dataset + '_topclip_perperiod/' + point
    print("The current point is", point)
    print()

    # Check if the location from the file is included in the list of locations of the acoustic data, and if not, nothing happens
    if point not in locs_list:
        # place for future code if the location is not in the list
        #Warning.warn('point ID from scores file not in list from acoustic metadata', UserWarning)
        print('WARNING:',point,'is not in metadata __________________')
    else:
        # Check if the folder already exists, and if not, create the folder
        if not os.path.exists(folder):
            os.makedirs(folder)
            print('folder for',point,' made')
            print()

        # Copy over the scores file: Use .copy() to ensure df is a standalone copy and not ust a view of the original dataframe
        df = sf.copy() 
        # Pull out just the values that reflect the current point
        df = df[df['point_id'] == point]
        
        
        # Iterate through each class in the CNN model
        for cl in classes:
            print('Working on ' + cl)
            print()
            #### May need to remove underscores in cadence_coo? ####
    
            # Initialize a counter
            num = 0
    
            # make a sub data frame to work with
            sub_df = df.copy()
            # Find the index of the top scoring file from each day and each time period for that class
            idx = sub_df.groupby(['date', 'time_period'])[cl].idxmax()
            # Use the index to retrieve the corresponding row values
            sub_df = sub_df.loc[idx, ['point_id', 'date', 'hour', 'time_period', cl, 'file', 'start_time', 'end_time']]
            #### NEED TO CHECK IF THIS WORKS ON MULTIPLE DAYS ####
            # Make a column for clip
            sub_df['clip'] = [
                clips_path + dataset + '_topclip_perperiod/' + point + '/' + str(sub_df['date'].iat[i]) + '_' + str(
                    sub_df['hour'].iat[i]) + '_' + str(sub_df['start_time'].iat[i]) + 's-' + str(
                    sub_df['end_time'].iat[i]) + 's_'+ cl + '.wav' for i in range(len(sub_df))]
            
            num += len(sub_df)
            print('num is ',num)
    
            # Test output ####
            #sub_df.to_csv(folder + '/' + point + cl + '_testsub_df.csv', index = False) # This works since it's not overwriting things
    
            # Append the top clips to the dataframe for this point
            keep_df = keep_df._append(sub_df, ignore_index = True)   
    
            # Test output ####
            #keep_df.to_csv(folder + '/' + point + cl + '_testkeep_df.csv', index = False)
            
            # decide whether to keep in new data
            if num < 2:
                print(f'{point} does not have a full day of top scoring files for this class ({cl}).')
    
            if len(df) < 1:
                print(point + ' failed.')
                continue
        # ChatGPTs code to sort by point
        # Sort the DataFrame by 'point_id'
        #keep_df = keep_df.sort_values(by=['point_id','date','time_period']).reset_index(drop=True)
        # Renumber the indices
        keep_df = keep_df.reset_index(drop=True)
        # Reshape this data to create one column for call_type and one column for scores
        keep_df = pd.melt(keep_df,
                          id_vars=['point_id', 'date', 'hour', 'time_period', 'file', 'start_time', 'end_time', 'clip'],
                          var_name='call_type', value_name='score')
        # Remove the NAs
        keep_df = keep_df.dropna(subset=['score'])
    
        # Test ####
        #keep_df.to_csv(folder + '/' + point + '_testkeep_df.csv', index = False)
               
        # save the audio files from the top scoring rows you pulled
        for i in range(len(keep_df)):
            # specify the specific audiofile to load, specify which clip you want to isolate
            filename = keep_df['file'].iat[i]
            filename = os.path.join("F:/", *filename.split("/")[1:])
            # Check
            print('check filename')
            print(filename)
            audio = Audio.from_file(filename, offset=int(keep_df['start_time'].iat[i]), duration=5)
            # save the new clip to the clip name you specified previously
            audio.save(keep_df['clip'].iat[i])
               
        # Append the top clips to keep_df
        dataset_df = dataset_df._append(keep_df, ignore_index = True) 
             
dataset_df = dataset_df.sort_values(by=['point_id','date','time_period']).reset_index(drop=True)
# save the csv for this dataset after iterating through all points
dataset_df.to_csv(big_folder + '/' + dataset + '_topclips_perSiteperPeriod.csv', index = False)

