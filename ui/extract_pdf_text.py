import os
import PyPDF2
from pathlib import Path
import random
import argparse
import streamlit as st

def extract_text_from_pdf(pdf_path):
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ''
            for page in reader.pages:
                text += page.extract_text()
        return text
    except Exception as e:
        st.write(f"Error extracting text from PDF: {e}")
        return f"PDF ERROR: {e} for file {pdf_path}"
    
def get_pdfs_to_process(pdf_dirs, txt_dir):
    existing_txt_files = set(os.path.splitext(f)[0] for f in os.listdir(txt_dir) if f.lower().endswith('.txt'))
    
    pdfs_to_process = []
    for pdf_dir in pdf_dirs:
        for f in os.listdir(pdf_dir):
            if f.lower().endswith('.pdf'):
                pdf_name = os.path.splitext(f)[0]
                if pdf_name not in existing_txt_files:
                    pdfs_to_process.append(os.path.join(pdf_dir, f))
    
    return pdfs_to_process

# def process_pdf_dir(pdf_dir, txt_dir, limit=None):
#     # Create txt_dir if it doesn't exist
#     Path(txt_dir).mkdir(parents=True, exist_ok=True)

#     # Get all PDF files and shuffle the list
#     pdf_files = [f for f in os.listdir(pdf_dir) if f.lower().endswith('.pdf')]
#     random.shuffle(pdf_files)

#     # Apply limit if specified
#     if limit is not None:
#         pdf_files = pdf_files[:limit]

#     for filename in pdf_files:
#         pdf_path = os.path.join(pdf_dir, filename)
#         txt_filename = os.path.splitext(filename)[0] + '.txt'
#         txt_path = os.path.join(txt_dir, txt_filename)

#         if not os.path.exists(txt_path):
#             st.write(f"Processing: {filename}")
#             text = extract_text_from_pdf(pdf_path)
#             with open(txt_path, 'w', encoding='utf-8') as txt_file:
#                 txt_file.write(text)
#             st.write(f"Created: {txt_filename}")
#         else:
#             st.write(f"Skipped: {filename} (TXT file already exists)")


def process_pdf_dirs(pdf_dirs, txt_dir, limit=None):
    Path(txt_dir).mkdir(parents=True, exist_ok=True)

    pdfs_to_process = get_pdfs_to_process(pdf_dirs, txt_dir)
    random.shuffle(pdfs_to_process)

    if limit is not None:
        pdfs_to_process = pdfs_to_process[:limit]

    total_files = len(pdfs_to_process)
    
    # Create a progress bar
    progress_bar = st.sidebar.progress(0)
    status_text = st.sidebar.empty()

    for i, pdf_path in enumerate(pdfs_to_process):
        filename = os.path.basename(pdf_path)
        txt_filename = os.path.splitext(filename)[0] + '.txt'
        txt_path = os.path.join(txt_dir, txt_filename)

        if not os.path.exists(txt_path):
            st.write(f"Processing: {filename}")
            text = extract_text_from_pdf(pdf_path)
            with open(txt_path, 'w', encoding='utf-8') as txt_file:
                txt_file.write(text)
            st.write(f"Created: {txt_filename}")
        else:
            st.write(f"Skipped: {filename} (TXT file already exists)")

        # Update progress bar and status text
        progress = (i + 1) / total_files
        progress_bar.progress(progress)
        status_text.text(f"Processed {i+1}/{total_files} files")

    st.sidebar.success(f"Completed processing {total_files} files!")

def process_pdfs():
    filecount=st.number_input('Enter the number of files to process',min_value=1,value=100)
    if st.button("Start processing"):
        pdf_directories = ["raw_pdf","processed_pdf"] 
        pdf_directories = ["raw_pdf"]  # The other directory was already processed
        txt_directory = "pdf_txt"  
        process_pdf_dirs(pdf_directories, txt_directory,filecount)
        st.write("Processing complete")

process_pdfs()