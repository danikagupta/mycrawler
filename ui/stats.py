import streamlit as st
import os

def count_files_in_top_level_directories(cwd=None):
    if cwd is None:
        cwd = os.getcwd()  # Use the current working directory if not specified
    
    file_counts = {}

    # List all items in the current working directory
    for item in os.listdir(cwd):
        item_path = os.path.join(cwd, item)
        if os.path.isdir(item_path):  # Check if the item is a directory
            # Count the number of files in this top-level directory
            #file_count = sum([len(files) for r, d, files in os.walk(item_path) if r == item_path])
            file_count = len([f for f in os.listdir(item_path)])
            file_counts[item] = file_count

    return file_counts

def compute_stats():
    st.write("Computing stats")
    statlist={}
    co = count_files_in_top_level_directories()
    #st.dataframe(co)
    statlist['Raw PDFs']=co['raw_pdf']  
    statlist['Processed PDFs']=co['processed_pdf']
    statlist['PDF Text']=co['pdf_txt']
    statlist['Raw References']=co['raw_references']
    statlist['Downloaded Refs']=co['downloaded_ref']
    statlist['Errored Refs']=co['errored_ref']
    return statlist



stats=compute_stats()
st.dataframe(stats)