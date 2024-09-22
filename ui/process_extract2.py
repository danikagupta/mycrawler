import streamlit as st
import pandas as pd
import os
from datetime import datetime

from typing import TypedDict, Annotated, List, Dict
from pydantic import BaseModel

COMBINED_DF_FILE="pdf_extract.csv"
TABLE_DIR_PATH="pdf_tables"

def combine_csv_files(directory_path=TABLE_DIR_PATH, output_file=COMBINED_DF_FILE):
    # List to store individual dataframes
    dfs = []
    stvis = st.empty()
    # Loop through all files in the directory
    for filename in os.listdir(directory_path):
        stvis.text(f"Processing {filename}")
        if filename.endswith('.txt'):
            file_path = os.path.join(directory_path, filename)
            df = pd.read_csv(file_path)
            df['source_file'] = filename
            dfs.append(df)

    # Combine all dataframes
    combined_df = pd.concat(dfs, ignore_index=True)

    # Save the combined dataframe to a new CSV file
    combined_df.to_csv(output_file, index=False)

    print(f"Combined CSV saved to {output_file}")

if st.button("Combine CSV files"):
    combine_csv_files()


