import streamlit as st
import tkinter as tk
from tkinter import filedialog

'''
# This is my attempt at setting up a basic GUI interface like I would be with my project data

Get familiar with accepting user input, assigning it to variables, etc, with the hopes that I'll be able to get it to accept a file input
'''

# Set a button to begin processing
# Initialize session state for the button
if "processing_started" not in st.session_state:
    st.session_state["processing_started"] = False

# Define what happens when button is clicked
if st.button("Click here to begin processing"):
    st.session_state["processing_started"] = True

# Show additional UI elements only if processing has started
if st.session_state["processing_started"]:
    st.text("Let's go!")

    # Ask for the collaborator input
    _="""
    if st.checkbox("Would you like to specify a collaborator?"):
        collab = st.radio("Select Collaborator: ", ('UMBEL', 'FWP'))
        if (collab == 'UMBEL'):
            st.success("Collaborator set to UMBEL")
        elif (collab == 'FWP'):
            st.success("Collaborator set to FWP")"""

    collab = st.radio("Select Collaborator: ", ('UMBEL', 'FWP'))
    if (collab == 'UMBEL'):
        st.success("Collaborator set to UMBEL")
    elif (collab == 'FWP'):
        st.success("Collaborator set to FWP")

    # Get an input for year
    year = st.text_input("Enter the year the data was collected", "Type Here ...")
    if (year.isnumeric()):
        st.success("Year is",year)
    else:
        st.warning("You have not input a numeric value for year")