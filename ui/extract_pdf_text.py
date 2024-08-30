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

def process_pdf_dir(pdf_dir, txt_dir, limit=None):
    # Create txt_dir if it doesn't exist
    Path(txt_dir).mkdir(parents=True, exist_ok=True)

    # Get all PDF files and shuffle the list
    pdf_files = [f for f in os.listdir(pdf_dir) if f.lower().endswith('.pdf')]
    random.shuffle(pdf_files)

    # Apply limit if specified
    if limit is not None:
        pdf_files = pdf_files[:limit]

    for filename in pdf_files:
        pdf_path = os.path.join(pdf_dir, filename)
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

def process_pdfs():
    filecount=st.number_input('Enter the number of files to process',min_value=1,value=10)
    if st.button("Start processing"):
        pdf_directory = "raw_pdf"  # Replace with your PDF directory path
        txt_directory = "pdf_txt"  # Replace with your TXT directory path
        process_pdf_dir(pdf_directory, txt_directory,filecount)

process_pdfs()