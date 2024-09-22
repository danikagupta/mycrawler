import streamlit as st
import pandas as pd
import os
from datetime import datetime

SRC_DIR="pdf_pages"
DF_FILE="pdf_text.csv"
DIR_PATH="pdf_txt"
MAX_INPUT_LENGTH=100000

import hashlib

def compute_md5_hash(input_string: str) -> str:
    md5_hasher = hashlib.md5()
    encoded_string = input_string.encode('utf-8')
    md5_hasher.update(encoded_string)
    md5_hash = md5_hasher.hexdigest()

    return md5_hash


def process_file(filename):
    st.write(f"Processing file {filename}")
    fqfn=os.path.join(DIR_PATH,filename)
    with open(fqfn,'r') as f:
        text_content=f.read()
    md5_hash=compute_md5_hash(text_content)
    print(f"Processing file {filename}")
    return md5_hash

def process_random_file(df):
    # Filter rows where status is 'processed3'
    new_status_df = df[df['status'] == 'processed5']
    
    # If there are no rows with status 'new', return the dataframe as is
    if new_status_df.empty:
        print("No rows with status 'processed2' to process.")
        return df
    
    # Pick a random row from the filtered dataframe
    random_row = new_status_df.sample(n=1)
    
    # Get the index of the random row
    index = random_row.index[0]
    
    # Extract the filename of the random row
    filename = random_row['filename'].values[0]
    
    # Call the process_file function on the filename
    md5_hash = process_file(filename)
    df.at[index, 'md5'] = "MD5" # Fake value; to ensure that the column exists. We will overwrite later.
    md5_count = (df['md5'] == md5_hash).sum()
    
    # Update the row with the return value from the function and update the 'updated' time
    df.at[index, 'md5'] = md5_hash
    df.at[index, 'match_hash'] = md5_count

    df.at[index, 'status'] = 'processed6'
    df.at[index, 'updated'] = pd.Timestamp.now()
    
    return df



df_txt=pd.read_csv(DF_FILE)
    
filecount=st.number_input("Number of files", value=3)
progress_bar=st.progress(0)
progress_text = st.empty()
if st.button("Process files : Stage 6"):
    start_time = datetime.now()
    for i in range(filecount):
        progress_bar.progress(i/filecount)
        process_random_file(df_txt)
        df_txt.to_csv(DF_FILE,index=False)

        elapsed_time = datetime.now() - start_time
        elapsed_seconds = int(elapsed_time.total_seconds())
        minutes, seconds = divmod(elapsed_seconds, 60)
        progress_text.text(f"Processed {i + 1} of {filecount} files | Time elapsed: {minutes}m {seconds}s")
progress_bar.progress(1)
st.title("Completed one run")