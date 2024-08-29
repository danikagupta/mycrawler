import streamlit as st
import os
from pdf2image import convert_from_bytes
from PIL import Image
import io
import base64
import json

import shutil

import PyPDF2

from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, AIMessage, SystemMessage

import random

RAW_PDF_DIR = "raw_pdf"
PDF_PAGES_DIR = "pdf_pages"

def move_file(source_path, destination_dir):
    if not os.path.exists(destination_dir):
        os.makedirs(destination_dir)
    destination_path = os.path.join(destination_dir, os.path.basename(source_path))
    shutil.move(source_path, destination_path)
    print(f"File {source_path} moved to {destination_path}")



def select_one_pdf():
    # Get the list of papers - this will be a list of directories under pdf_pages
    papers = os.listdir(RAW_PDF_DIR)
    paper = st.selectbox("Select paper", papers,key="processs-one-pdf")
    return paper

def select_random_pdf():
    # Get the list of papers - this will be a list of directories under pdf_pages
    papers = os.listdir(RAW_PDF_DIR)
    paper = random.choice(papers)
    return paper

def pdf_to_text(uploaded_file):
    pdfReader = PyPDF2.PdfReader(uploaded_file)
    count = len(pdfReader.pages)
    text=""
    for i in range(count):
        page = pdfReader.pages[i]
        text=text+page.extract_text()
    return text

def extract_text_from_pdf(paper):
    fqfn = os.path.join(RAW_PDF_DIR, paper)
    st.write(f"Processing {fqfn}")
    with open(fqfn, 'rb') as f:
        pdfbytes = f.read()
    text=pdf_to_text(fqfn)
    return text


def onerun_llm_text(paper, text_content,model):

    default_question="""
    (1) We need to make a list of references cited in this paper.
    (2) Create a table with 
      (a) One row for every reference cited in the paper
      (b) the columns listing the title, authors, publication year, and publication venue. Also include URL if available.
      (c) Put any additional information in a Notes column.


    (3) Only return the table with no additional information - no preamble or concluding remarks.
    (4) Please be thorough. Ensure that you have captured all references cited in the paper.
    """

    # Removed "      (d) Put the complete citation in APA format in a separate column."
    question=default_question

    #st.write("You asked: ", question)
    chat = ChatOpenAI(model_name="gpt-4o")

    messages = [
        SystemMessage(content="You are an AI assistant capable of analyzing images and text."),
        HumanMessage(content=[
            {
                "type": "text",
                "text": f"""Respond to the user's ask: 
                {question}
                based on the following text block:
                {text_content[-100000:]}  
                """
            }
        ]),
    ]

    response = chat(messages)
    print(f"\n\n* * * * *\nResponse: \n\n{response}\n\n*********\n")
    #st.write(response)
    st.subheader("Analysis Result:")
    st.write(response.content)
    return response.content
    
def create_ref_json_files(paper,rc):
    #with open("output.txt") as f:
    #    content = f.read()
    content=rc

    chat = ChatOpenAI(model_name="gpt-4o")

    messages = [
        SystemMessage(content="You are an AI assistant capable of precisely formatting text to JSON."),
        HumanMessage(content=[
            {
                "type": "text",
                "text": f"""Given the following text block containing a table:: 
                {content}
                Convert this table into a JSON object with an array of dictionaries, where each dictionary represents a row of data. 
                The keys should be the column headers, and the values should be the corresponding cell values. 
                Return only the JSON object, without any additional text or explanation.
                """
            }
        ]),
    ]

    OUTPUT_DIR = "raw_references"
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    paper_name = paper.replace(".pdf","")

    response = chat(messages)  
    #st.write(response.content)
    print(response.content)
    clean_response=response.content.strip()
    clean_response=clean_response.replace("`", "")
    if clean_response.startswith("json"):
        clean_response = clean_response[5:]
    try:
        json_data = json.loads(clean_response)
        for i,record in enumerate(json_data):
            fname=os.path.join(OUTPUT_DIR, f"{paper_name}_{i:03}.txt")
            st.write(f"Adding file {fname}")
            with open(fname,"w") as f:
                f.write(json.dumps(record))
    except Exception as e:
        print("Error parsing JSON: ", e)
        with open("output_error.txt","w") as f:
            f.write(response.content)

def process_one_pdf(paper,text_content):
    rc=onerun_llm_text(paper, text_content, model="gpt-4o-mini")
    if rc is not None:
        with open("output.txt","w") as f:
            f.write(rc)
        create_ref_json_files(paper,rc)
        move_file(os.path.join(RAW_PDF_DIR, paper), "processed_pdf")
    else:
        st.write("Error in response from AI model")
        move_file(os.path.join(RAW_PDF_DIR, paper), "error_pdf")    


def named_run():
    st.header("Process a PDF file")
    paper=select_one_pdf()
    if st.button("Run Analysis"):
        txt=extract_text_from_pdf(paper)
        with st.expander("Text"):
            st.write(txt)
        process_one_pdf(paper,txt)

def bulk_run():
    st.header("Process multiple PDF files")
    filecount=st.number_input("Number of files to process",min_value=1,step=1)
    if st.button("Run Bulk Analysis"):
        for i in range(filecount):
            paper=select_random_pdf()
            txt=extract_text_from_pdf(paper)
            #with st.expander(f"Text: {i+1}"):
            #    st.write(txt)
            process_one_pdf(paper,txt)



bulk_run()
st.divider()
named_run()
st.divider()
