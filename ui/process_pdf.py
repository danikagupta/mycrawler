import streamlit as st
import os
from pdf2image import convert_from_bytes
from PIL import Image
import io
import base64

from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, AIMessage, SystemMessage

RAW_PDF_DIR = "raw_pdf"
PDF_PAGES_DIR = "pdf_pages"

def encode_image_path(png_path):
    with Image.open(png_path) as image:
        # Convert image to bytes
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode()
    
def encode_multiple_images(images):
    msg=HumanMessage(content=[
        {
            "type": "image_url",
            "image_url": {"url": f"data:image/png;base64,{base64_image}"}
            } for base64_image in images
            ])
    return msg

def select_one_pdf():
    # Get the list of papers - this will be a list of directories under pdf_pages
    papers = os.listdir(RAW_PDF_DIR)
    paper = st.selectbox("Select paper", papers,key="processs-one-pdf")
    return paper

def save_pdf_pages(paper):
    fqfn = os.path.join(RAW_PDF_DIR, paper)
    st.write(f"Processing {fqfn}")
    output_dir = os.path.join(PDF_PAGES_DIR, paper)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    with open(fqfn, 'rb') as f:
        pdfbytes = f.read()
    images=convert_from_bytes(pdfbytes)
    for i, image in enumerate(images):
        fname=os.path.join(output_dir, f"{i+1:03}.png")
        image.save(fname)
        st.write("Saved: ", fname)

def onerun_llm_pages(paper, pages,model):
    dir=os.path.join("pdf_pages",paper)
    images = [os.path.join(dir,page) for page in pages]
    encoded_images = [encode_image_path(image) for image in images]
    st.sidebar.image(images[0], caption=f'Front Page', use_column_width=True)

    default_question="""
    (1) We need to make a list of references cited in this paper.
    (2) Create a table with 
      (a) One row for every reference cited in the paper
      (b) the columns listing the title, authors, publication year, and publication venue. Also include URL if available.
      (c) Put any additional information in a Notes column.
      (d) Put the complete citation in APA format in a separate column.

    (3) Only return the table with no additional information - no preamble or concluding remarks.
    (4) Please be thorough. Ensure that you have captured all references cited in the paper.
    """
    question=st.text_area("Ask question",value=default_question)
    if st.button("Run Analysis"):
        #st.write("You asked: ", question)
        chat = ChatOpenAI(model_name="gpt-4o-mini", max_tokens=3000)

        messages = [
            SystemMessage(content="You are an AI assistant capable of analyzing images and text."),
            HumanMessage(content=[
                {
                    "type": "text",
                    "text": f"Analyze the following images and respond to the user's prompt: {question}"
                }
            ]),
            encode_multiple_images(encoded_images)
        ]

        response = chat(messages)
        print(f"\n\n* * * * *\nResponse: \n\n{response}\n\n*********\n")
        #st.write(response)
        st.subheader("Analysis Result:")
        st.write(response.content)
        return response.content

def process_one_pdf(paper):
    pages = os.listdir(os.path.join(PDF_PAGES_DIR, paper))
    pages.sort()
    rc=onerun_llm_pages(paper, pages, model="gpt-4o-mini")
    with open("output.txt","w") as f:
        f.write(rc)    


st.header("Process a PDF file")
paper=select_one_pdf()
save_pdf_pages(paper)
process_one_pdf(paper)