import streamlit as st
import os


def process_one_file(pdfbytes,name="Unknown"):
    output_dir = "raw_pdf"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    output_path1 = os.path.join(output_dir, f'{name}')
    with open(output_path1, 'wb') as f:
        f.write(pdfbytes)
        

st.header("Upload PDF files")
uploaded_files=st.file_uploader("Upload PDF file",type="pdf", accept_multiple_files=True)
if st.button("Upload") and uploaded_files is not None:
    for uploaded_file in uploaded_files:
        process_one_file(uploaded_file.read(),uploaded_file.name)
        st.write(f"Uploaded {uploaded_file.name}")
st.divider()