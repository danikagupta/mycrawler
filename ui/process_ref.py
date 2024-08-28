import streamlit as st

import requests
import json
import os
from urllib.parse import quote_plus

import shutil

RAW_PDF_DIR = "raw_pdf"
RAW_REF_DIR = "raw_references"

def move_file(source_path, destination_dir):
    if not os.path.exists(destination_dir):
        os.makedirs(destination_dir)
    destination_path = os.path.join(destination_dir, os.path.basename(source_path))
    shutil.move(source_path, destination_path)
    print(f"File {source_path} moved to {destination_path}")

def search_and_download_paper(paper_info, serp_api_key):
    # Construct the search query
    title = paper_info['Title']
    authors = paper_info['Authors']
    year = paper_info['Year']
    query = f"{title} {authors} {year} filetype:pdf"
    
    # SERP API endpoint
    url = "https://api.serpstack.com/search"
    
    # Parameters for the SERP API request
    params = {
        "access_key": serp_api_key,
        "query": query,
        "num": 5,  # Number of results to retrieve
    }
    
    try:
        # Make the API request
        response = requests.get(url, params=params)
        response.raise_for_status()
        search_results = response.json()
        
        # Check if we have any organic results
        if 'organic_results' in search_results and search_results['organic_results']:
            for result in search_results['organic_results']:
                pdf_url = result.get('url')
                if pdf_url and pdf_url.lower().endswith('.pdf'):
                    # Attempt to download the PDF
                    pdf_response = requests.get(pdf_url)
                    if pdf_response.status_code == 200:
                        # Generate a filename
                        filename = f"{quote_plus(title)}_{year}.pdf"
                        fqfn = os.path.join(RAW_PDF_DIR, filename)
                        
                        # Save the PDF
                        with open(fqfn, 'wb') as f:
                            f.write(pdf_response.content)
                        st.write(f"PDF downloaded successfully: {filename}")
                        return filename
            
            st.write(f"No suitable PDF link found in the search results for {title}.")
        else:
            st.write(f"No search results found for {title}.")
    
    except requests.RequestException as e:
        print(f"An error occurred during the search: {e}")
    
    return None

# Example usage
serp_api_key = st.secrets["SERPSTACK_API_KEY"]


def example_run():
    paper_info = {
        "Title": "Decolorization of triphenylmethane azo dyes by Citrobacter sp.",
        "Authors": "An SY, Min SK, Cha JH, Choi YL, Cho YS, Kim CH, Lee YC",
        "Year": 2002,
        "Publication Venue": "Bioresource Technology",
        "URL": "N/A",
        "Notes": "N/A",
        "APA Citation": "An, S. Y., Min, S. K., Cha, J. H., Choi, Y. L., Cho, Y. S., Kim, C. H., & Lee, Y. C. (2002). Decolorization of triphenylmethane azo dyes by Citrobacter sp. Bioresour. Technol, 121: 1037-1040."
    }

    downloaded_file = search_and_download_paper(paper_info, serp_api_key)

    if downloaded_file:
        print(f"File downloaded: {downloaded_file}")
    else:
        print("Unable to download the paper.")

def main_run():
    # Pick a random file from RAW_REF_DIR
    files = os.listdir(RAW_REF_DIR)
    file = st.selectbox("Select a reference file", files)
    if st.button("Download PDF") and file is not None:
        with open(os.path.join(RAW_REF_DIR, file)) as f:
            paper_info = json.load(f)
        
        downloaded_file = search_and_download_paper(paper_info, serp_api_key)
        if downloaded_file:
            st.write(f"File downloaded: {downloaded_file}")
            move_file(os.path.join(RAW_REF_DIR, file), "downloaded_ref")
        else:
            st.write("Unable to download the paper.")
            move_file(os.path.join(RAW_REF_DIR, file), "errored_ref")

main_run()
    
