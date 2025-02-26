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
    year = st.text_input("Enter the year the data was collected", "")
    if (year.isnumeric()):
        st.success("Success! Year set to:")
        st.markdown(year) # Looks like text or markdown can only handle one input
    else:
        st.warning("You have not input a numeric value for year")


# Try to put in a file selector function
## Might have to work this out later
_ = '''
def file_selector(folder_path='.'):
    filenames = os.listdir(folder_path)
    selected_filename = st.selectbox('Select a file', filenames)
    return os.path.join(folder_path, selected_filename)

filename = file_selector()
st.write('You selected `%s`' % filename)
'''
_='''
def select_folder(): # Create a function called select_folder
    #root = tk.Tk() # Create a tkinter root window and initialize a basic tkinter GUI
    #root.withdraw()  # Hide the root window
    folder_selected = filedialog.askdirectory()  # Open folder selection dialog
    return folder_selected
st.text("Function created")

if st.button("Select Folder"): # Create a button that says "select folder" and if selected, do the following
    folder_path = select_folder() # run the select_folder function
    if folder_path: # if folder_path is TRUE (meaning there are values for it), do the following
        st.session_state["folder_path"] = folder_path # set "folder_path" equal to folder path # WHY IS THIS A STRING?
'''