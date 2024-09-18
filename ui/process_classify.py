import streamlit as st
import pandas as pd
import os
from datetime import datetime

from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, AIMessage, SystemMessage

from typing import TypedDict, Annotated, List, Dict
from pydantic import BaseModel


SRC_DIR="pdf_pages"
DF_FILE="pdf_text.csv"
DIR_PATH="pdf_txt"
MAX_INPUT_LENGTH=100000

class PaperScore(BaseModel):
    score: int
    reason: str

from langchain_openai import ChatOpenAI
from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate, SystemMessagePromptTemplate

def one_llm_classify_relevance(text_content):
    llmModel = ChatOpenAI(model_name="gpt-4o-mini", max_tokens=3000)
    
    parser = PydanticOutputParser(pydantic_object=PaperScore)

    system_template = """You are an AI assistant capable of categorizing the text as being relevant to a domain.
    Please review the user's paper and return - on a scale of 1-10 whether the paper is relevant to mycoremediation.
    Score should be 1 if the paper is not relevant at all.
    Score should be 10 if the paper is primarily about mycoremediation.
    Also return the Reason for the score.
    
    {format_instructions}
    """
    human_template = "{text}"

    chat_prompt = ChatPromptTemplate(
        messages=[
            SystemMessagePromptTemplate.from_template(system_template),
            HumanMessagePromptTemplate.from_template(human_template)
        ],
        input_variables=["text"],
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )

    _input = chat_prompt.format_prompt(text=text_content[:MAX_INPUT_LENGTH])
    output = llmModel(_input.to_messages())
    resp = parser.parse(output.content)

    print(f"\n\n* * * * *\nResponse: \n\n{resp}\n\n*********\n")
    st.subheader("Analysis Result:")
    st.write(f"Score: {resp.score}\n Reason: {resp.reason}")
    return resp.score, resp.reason


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

def process_file(filename):
    # Placeholder logic for processing the file
    # In reality, this would contain the logic you want to apply
    st.write(f"Processing file {filename}")
    with open(os.path.join(DIR_PATH,filename),'r') as f:
        text_content=f.read()
    score,reason = one_llm_classify_relevance(text_content)
    print(f"Processing file {filename}")
    return score,reason

def process_random_file(df):
    # Filter rows where status is 'new'
    new_status_df = df[df['status'] == 'new']
    
    # If there are no rows with status 'new', return the dataframe as is
    if new_status_df.empty:
        print("No rows with status 'new' to process.")
        return df
    
    # Pick a random row from the filtered dataframe
    random_row = new_status_df.sample(n=1)
    
    # Get the index of the random row
    index = random_row.index[0]
    
    # Extract the filename of the random row
    filename = random_row['filename'].values[0]
    
    # Call the process_file function on the filename
    score,reason = process_file(filename)
    
    # Update the row with the return value from the function and update the 'updated' time
    df.at[index, 'comments'] = reason
    df.at[index, 'score'] = score
    df.at[index, 'status'] = 'processed'
    df.at[index, 'updated'] = pd.Timestamp.now()
    
    return df



df_txt=pd.DataFrame(columns=["filename","status","result","created","updated"])
if os.path.exists(DF_FILE):
    df_txt=pd.read_csv(DF_FILE)
    
if st.button("Initialize"):
    df_txt=process_filenames_from_directory(DIR_PATH, df_txt)
    df_txt.to_csv(DF_FILE,index=False)
    st.dataframe(df_txt)

st.divider()
filecount=st.number_input("Number of files", value=10)
progress_bar=st.progress(0)
progress_text = st.empty()
if st.button("Process files"):
    for i in range(filecount):
        progress_bar.progress(i/filecount)
        process_random_file(df_txt)
        df_txt.to_csv(DF_FILE,index=False)
        progress_text.text(f"Processed {i + 1} of {filecount} files")
progress_bar.progress(1)
st.title("Completed one run")
    
