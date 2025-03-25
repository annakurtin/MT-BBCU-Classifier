''' 
Clip Extraction Code
This is a script to extract top scoring clips from each site. The output will give you the scripts to run the listening_notebook code on to annotate the clips for cuckoo presence. 

Copied from script of same name from model 1.0 files 1/11/2024
Last edited 2/19/2024
'''
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
from os.path import exists
from datetime import date
from datetime import timedelta
import streamlit as st
import math
import re

# Make functions
#Function to find all the factors for a given number
# Inputs chosen which is the number to find the factors of
def find_factors(chosen, currentnum=None, numbers=None): 
    # Recursion start, always append 1 and start with 2
    if numbers is None:
        numbers = [1]
        currentnum = 2
    # Return last value if it's two 
    if currentnum == chosen:
        numbers.append(currentnum)
        return numbers
    else:
        # Check if the chosen item is divisible by the current number
        if chosen % currentnum == 0:
            numbers.append(currentnum)
        # Always continue with the next number:
        currentnum += 1
        # Recursion to run the function on itself again 
        return find_factors(chosen, currentnum, numbers)
        
# Function to give information about the number of days excluded from the clips and suggest better intervals
# Inputs maxdays created from subtracting the earlist user specified day from the latest user specified day (deltatime class) and excluded which is the number of days left over (deltatime class)
def info_excluded_days(maxdays, excluded):
    #excluded = dates_excluded.strftime('%Y%m%d')
        st.info(f"Excluded {excluded} days at the end of the {maxdays.days}-day monitoring period, consider a different interval")
        # Call find_factors function
        periods_options = find_factors(maxdays.days)
        # for each element in periods_options, divide maxdays.days by it to get the time period
        interval_options = []
        for i in periods_options:
            out = int(maxdays.days/i)
            interval_options.append(out)
        # Exclude the last one because this is just the total number of days
        interval_options = interval_options[1:]
        #st.info(f"Monitoring period you selected is divisible in even sections: {periods_options} ")
        st.info(f"Options for survey intervals that would be evenly distributed across the monitoring period:{interval_options} days")
    
# create a function to read in the length of the user specified intervals and provide the start date for each interval
# Inputs start (date time user specified), end (date time user specified), maxdays (calculated from start and end, deltatime) and interval (number of days desired in one survey period, provided by the user)
def date_range(start, end, maxdays, interval):
    # find the number of survey periods based on the user specified interval
    num_periods = maxdays / interval
    # truncate this  so that it is an integer and doesn't exceed the total days of the monitoring period
    periods_int = math.trunc(num_periods)
    survey_intervals = []
    for i in range(periods_int+1):
        add = interval * i # this is already in datetime format
        result = (start + add)
        survey_intervals.append(result)           
    # Calculate if any days have been cut off due to survey interval
    dates_excluded = end - (start + interval * (periods_int) )
    excluded = dates_excluded.days
    # Give input on better survey interval times if data is excluded
    if excluded > 1:
        info_excluded_days(maxdays, excluded)
    # Return a list of the start dates of each survey interval 
    return survey_intervals
    

'''
Setup and file uploads 
'''
# Establish which dataset you're working on and where the metadata is
# Take this from the already established user input
year = '2022' # Format YYYY
collab = 'UMBEL' # Format UMBEL or FWPR#
region = ""
metadata_file = st.file_uploader("Upload a .csv of the metadata for the acoustic data that contains a 'point_id' column", type=['csv'])
classes = ['cadence_coo','rattle']
# Establish which dataset you're working with 
dataset = f'{year}_{collab}'
print(dataset)

# read in scores file so you don't have to run the classifier every time
scores_file = st.file_uploader('Upload scores', type=['csv'])
scores = pd.read_csv(scores_file)

'''
Please enter some information on the beginning and end of the time period of interest. The program will use this information to only extract clips within the specified period.
'''
default_start = f"{year}-06-01"
default_end = f"{year}-08-15"
first_date = st.date_input("Please select the earliest date you would like included within the monitoring period",value = default_start)
last_date = st.date_input("Please select the latest date you would like included within the monitoring period",value = default_end)
last_date = last_date + timedelta(1)
#st.write("one plus last date",last_date)
#st.write(type(last_date))
max_days = last_date - first_date
max_days_int = max_days.days

'''
Now, please specify the duration of each survey interval within the monitoring period. This can range from one day to the maxium number of days between the first and last days you specified. 
'''
interval_int = st.number_input("Please select the number of days you would like to include within each survey interval", 1, max_days_int)
interval = timedelta(days=interval_int)
# Puts out a list containing all of the start dates of the sub survey intervals within the monitoring period 
#st.write(interval)


'''
Scores file processing and clip extraction
'''
if scores_file and metadata_file:
    # Format metadata file
    metadata = pd.read_csv(metadata_file)
    # Convert all column names to upper case and convert - or " " to a _
    ## NOTE: need to test this to ensure it's working properly with different types of input
    metadata.columns = metadata.columns.str.lower().str.replace(r'[-\s]', '_', regex=True)
    if not "point_id" in metadata.columns:
        st.warning("No column for point_id in metadata. Please reupload data")
    # Take the column labeled 'point_ID' and put it into a list [with tolist()] that is sorted in orde [with sorted()], then converted to a set of iterable elements [with set()]
    locs_list = sorted(set(metadata['point_id'].tolist()))

    # Format the scores file
    # first isolate out the file ID ****************************************
    # SEPARATE OUT THIS FILE ID THEN ISOLATE POINT ID, DATE, AND TIME FROM IT
    scores['file_id'] = scores['file'].str.extract(r'([A-Z0-9\-]+_\d{8}_\d{6})')
    # Make a column for point ID from the scores file
    scores['point_id'] = scores['file_id'].str.split('_').str[0]
    st.write(scores)
_='''
    # Make a column for point ID from the scores file
    scores['point_id'] = scores['file'].apply(lambda x: os.path.basename(x).split('_')[0] if isinstance(x, str) else None)
    # Get a list of unique point_ids in the scores file
    point_list = list(set(scores['point_id']))
    st.write(f"list of points from scores file: {point_list}")
    # Make date column
    scores['date'] = scores['file'].apply(lambda x: re.search(r'_(\d{8})_\d{6}_', os.path.basename(x)).group(1))
    st.write(scores)
    #scores['date'] = scores['file'].apply(lambda x: os.path.basename(x).split('_')[1] if isinstance(x, str) else None)
    #scores['date'] = pd.to_numeric(scores['date']) 
    scores['date'] = pd.to_datetime(scores['date'], format='%Y%m%d').dt.date
    # Exclude data that is outside the specified date ranges
    scores = scores.loc[(scores['date'] >= first_date) & (scores['date'] < last_date)]
    # Make time column
    scores['time'] = scores['file'].apply(lambda x: os.path.basename(x).split('_')[2])
    #**********************************************************************************
    # Make species column
    scores['species'] = 'BBCU'
    # Make a column for time interval
    scores['survey_interval'] = np.nan
    # Generate a list of the start dates of each interval 
    survey_starts = date_range(first_date, last_date, max_days, interval)
    #st.write(f"survey start dates:{survey_starts}")
    #st.write(type(survey_starts))
    for i in range(len(survey_starts)):
        st.write(f"iteration {i}")
        for row in range(len(scores['date'])):
            # check if the value of date for this row is greater than or equal to the start date and less than the next start date
            if (scores.at[row,'date'] >= survey_starts[i]):
                # This throws a key error if the start date of monitoring period earlier than any scores file
                # assign the survey interval
                scores.at[row, 'survey_interval'] = i + 1
    # Order the columns
    scores = scores[['file', 
             'point_id',
             'date',
             'survey_interval',
             'time',
             'start_time',
             'end_time',
             'species',
             'cadence_coo',
             'rattle']]
    # make a clean index column
    scores = scores.reset_index(drop=True)
    st.write(scores)
    
    

    # set run_complete equal to true as if the whole thing had been run
    #run_complete = True
    
    # make a temporary directory for the folders to go into
    big_folder = os.path.join(os.getcwd(), f"{year}_{collab}{region}_clips")  # add on the time period to this?
    # Initialize an empty dataframe for this dataset
    dataset_df = pd.DataFrame()
    st.write(big_folder)

    # Iterate through each point in the point_list
    for point in point_list:
        # Initialize an emtpy dataframe for this point
        keep_df = pd.DataFrame()
        # Initialize a folder relating the class to the location you're looking at
        folder = os.path.join(big_folder, point) #'_topclip_perperiod/' + point
        print("The current point is", point)
        # Check if the location from the file is included in the list of locations of the acoustic data, and if not, nothing happens
        if point not in locs_list:
            # place for future code if the location is not in the list
            #Warning.warn('point ID from scores file not in list from acoustic metadata', UserWarning)
            st.warning('Point not in metadata')
            st.info(f"Point {point} is not in metadata file provided. Please check to ensure this is correct.")
        else:
            # Check if the folder already exists, and if not, create the folder
            if not os.path.exists(folder):
                os.makedirs(folder)
                st.success("Subfolder created")
                # Not sure that this is doing exactly what I want as far as creating a folder - might have to modify this for hugging face but we'll go with it for now
            # Copy over the scores file: Use .copy() to ensure df is a standalone copy and not ust a view of the original dataframe
            df = scores.copy() 
            # Pull out just the values that reflect the current point
            df = df[df['point_id'] == point]

            # Iterate through each class in the CNN model
            for cl in classes:
                # Initialize a counter
                num = 0
        
                # make a sub data frame to work with
                sub_df = df.copy()
                idx = sub_df.groupby(['date', 'survey_interval'])[cl].sort_values(by=[cl],ascending=False)
                # resets the index at the start of the for loop but drops the current value from consideration (double check this)
                sub_df = sub_df.reset_index(drop=True)
                # take the top 10 from each site
                sub_df = sub_df.iloc[:10]
                st.write(sub_df)
                 # LEFT OFF HERE ***********************
                # TO DO: 
                ## FIGURE OUT HOW TO CHAIN GROUP BY AND SORT VALUES TO GET THE TOP SPECIFIED FROM EACH SITE
                ## make a new test dataset that has various survey intervals and point ids 
'''              
_='''
                # Find the index of the top scoring file from each day and each time period for that class
                idx = sub_df.groupby(['date', 'survey_interval'])[cl].idxmax() # go back to Tessa's original code to see how to pull out the top number specified
                
                # Original clip extraction code 
                # take dataframe of scores (sub_df) and sort them by scores (c1) 
                sub_df = sub_df.sort_values(by=['present'],ascending=False)
                # resets the index at the start of the for loop but drops the current value from consideration (double check this)
                sub_df = sub_df.reset_index(drop=True)
                # take the top 10 from each site
                sub_df = sub_df.iloc[:10]
                num += len(sub_df)
                # append the result to dataframe with top scoring clips
                keep_df = pd.concat([keep_df,sub_df])
                '''
_='''
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
    
            # Initialize a counter # LEFT OFF HERE ***********************
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
'''


_=''' # FORMATTING SCORES FILE
# Later should only have to change E: to F: to run on Ery
# Establish the file path for the scores ###### CHANGE THIS BACK #####
### Use the scores data that's already present *******************************
#score_path = f'F:/CNN_Classifier_Files/Model_2.0/Model_Scores/predictions_epoch-10_opso-0-10-1-{year}_{collab}_Audio.csv'
# Establish the file path for where the clips will go
#clips_path = f'F:/Cuckoo_Acoustic_Data/{year}/{year}_{collab}_Data/{year}_{collab}_Clips/'
# Establish the file path for the folder with all the audio files
#audio_path = f'F:/Cuckoo_Acoustic_Data/{year}/{year}_{collab}_Data/{year}_{collab}_Audio/'
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
'''