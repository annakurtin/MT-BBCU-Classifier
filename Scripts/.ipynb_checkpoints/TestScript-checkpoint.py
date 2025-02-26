'''
Test file

This is to test setting up a new github and streamlit for the AI model

This script has resources and other useful things
'''

# Streamlit setup https://github.com/ddobrinskiy/streamlit-jupyter
import streamlit as st

#from streamlit_jupyter import StreamlitPatcher, tqdm

import tkinter as tk

from tkinter import filedialog

# StreamlitPatcher().jupyter() 

st.title("Example")

# %% 99_example.ipynb 5
st.markdown(
    """

This is a test page demonstrating the use of `streamlit_jupyter`.

If you're seeing this in jupyter, then it's working!

Add in more text!

"""
)
# Magic comments means that things in triple comments are still displayed so that you can use markdown syntax without having to specify

# Streamlet basics from https://www.geeksforgeeks.org/a-beginners-guide-to-streamlit/
_ = """
# Header
st.header("This is a header") 

# Subheader
st.subheader("This is a subheader")

# Can also do headers and subheaders in mMarkdown
st.markdown("## This is a markdown header")
st.markdown("### This is a markdown subheader")
"""
# Printing out different warnings
st.success("The operation was a success")
st.info("Here is some basic information to know")
st.warning("Warning: This isn't doing what you think it is!")
#st.error("Error: we were not able to carry this out")
# Exception - This has been added later
#exp = MiscError("Trying to do something that you can't")
#st.exception(exp)
# After an error is raised nothing else will run!!!!!

# Write text
st.write("Text with write")
# Writing python inbuilt function range()
st.write(range(10))

# Display Images

# import Image from pillow to open images
#from PIL import Image
#img = Image.open("streamlit.png")
# display image using streamlit
# width is used to set the width of an image
#st.image(img, width=200)


_ = """
# checkbox
# check if the checkbox is checked
# title of the checkbox is 'Show/Hide'
if st.checkbox("Show/Hide A Thing"):
    # display the text if the checkbox returns True value
    st.text("Showing the widget")

# radio button
# first argument is the title of the radio button
# second argument is the options for the radio button
collab = st.radio("Select Collaborator: ", ('UMBEL', 'FWP'))

# conditional statement to print 
# show the result using the success function
if (collab == 'UMBEL'):
    st.success("Collaborator set to UMBEL")
elif (collab == 'FWP'):
    st.success("Collaborator set to FWP")
else: 
    st.warning("No Collaborator Selected")
"""

'''
## Ok, now let's apply it to our use case

Adding in more!
'''

# Combine these:
if st.checkbox("Would you like to specify a collaborator?"):
    collab = st.radio("Select Collaborator: ", ('UMBEL', 'FWP'))
    if (collab == 'UMBEL'):
        st.success("Collaborator set to UMBEL")
    elif (collab == 'FWP'):
        st.success("Collaborator set to FWP")

# Selection box
# first argument takes the titleof the selectionbox
# second argument takes options
hobby = st.selectbox("Hobbies: ",
                     ['Dancing', 'Reading', 'Sports'])

# print the selected hobby
st.write("Your hobby is: ", hobby)

# multi select box

# first argument takes the box title
# second argument takes the options to show
hobbies = st.multiselect("Hobbies: ",
                         ['Dancing', 'Reading', 'Sports'])

# write the selected options
st.write("You selected", len(hobbies), 'hobbies')

# Create a button, that when clicked, shows a text
if(st.button("Click Here to Begin Processing")):
    st.text("Let's Go!")

# Text Input
# save the input text in the variable 'year'
# first argument shows the title of the text input box
# second argument displays a default text inside the text input area
year = st.text_input("Enter the year the data was collected", "Type Here ...")

# display the name when the submit button is clicked
# .title() is used to get the input text string
if(st.button('Submit')):
    result = year.title()
    st.success(result)

_ = '''
def select_folder(): # Create a function called select_folder
    root = tk.Tk() # Create a tkinter root window and initialize a basic tkinter GUI
    root.withdraw()  # Hide the root window
    folder_selected = filedialog.askdirectory()  # Open folder selection dialog
    return folder_selected
st.text("Function created") 

if st.button("Select Folder"): # Create a button that says "select folder" and if selected, do the following
    folder_path = select_folder() # run the select_folder function
    if folder_path: # if folder_path is TRUE (meaning there are values for it), do the following
        st.session_state["folder_path"] = folder_path # set "folder_path" equal to folder path # WHY IS THIS A STRING?

# Display selected folder path
folder_path = st.session_state.get("folder_path", "")

#folder_path = "F:/Audio_Files"
st.text_input(label = "Selected Folder Path:", value = folder_path)
'''