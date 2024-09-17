import streamlit as st
import pandas as pd
import os
from datetime import datetime

def process_filenames_from_directory(directory_path, df):
    # Get the list of all filenames in the directory
    filenames = os.listdir(directory_path)
    
    # Get the current time for new entries
    current_time = datetime.now()
    
    # Collect new entries in a list of dictionaries
    new_entries = []
    
    for filename in filenames:
        if filename not in df['filename'].values:
            new_entries.append({
                'filename': filename,
                'status': 'new',
                'comments': '',
                'created': current_time,
                'updated': current_time
            })
    
    # If there are new entries, concatenate them to the original dataframe
    if new_entries:
        new_df = pd.DataFrame(new_entries)
        df = pd.concat([df, new_df], ignore_index=True)
    
    return df

def process_names(file_path, df):
    with open(file_path, 'r') as file:
        names = file.readlines()
    
    # Clean the names (removing any newline characters)
    names = [name.strip() for name in names]
    
    # Get the current time for new entries
    current_time = datetime.now()
    
    # Iterate through each name and update the dataframe if necessary
    for name in names:
        if name not in df['filename'].values:
            new_entry = {
                'filename': name,
                'status': 'new',
                'comments': '',
                'created': current_time,
                'updated': current_time
            }
            df = df.append(new_entry, ignore_index=True)
    
    return df



SRC_DIR="pdf_pages"
DF_FILE="pdf_text.csv"
DIR_PATH="pdf_txt"

df_txt=pd.DataFrame(columns=["filename","status","result","created","updated"])
if os.path.exists(DF_FILE):
    df_txt=pd.read_csv(DF_FILE)
    


if st.button("Initialize"):
    df_txt=process_filenames_from_directory(DIR_PATH, df_txt)
    df_txt.to_csv(DF_FILE,index=False)
    st.dataframe(df_txt)
