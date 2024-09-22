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

class StudyReason(BaseModel):
    study: str
    reason: str

from langchain_openai import ChatOpenAI
from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate, SystemMessagePromptTemplate

def one_llm_classify_relevance(text_content):
    llmModel = ChatOpenAI(model_name="gpt-4o-mini", max_tokens=3000)
    
    parser = PydanticOutputParser(pydantic_object=StudyReason)

    system_template = """You are an AI assistant capable of categorizing a paper as Experimental or Summary.
    
    Please review the user's paper and return a Yes/No answer to this question: 
    Does this paper contain new experiments on fungi based remediation or is it summarizing the results of other papers?
    
    Study should be:
      Experimental if the paper contains new experiments on fungi based remediation, 
      Summary if it summarizes the results of other papers.
      Neither  otherwise.
 
    Also return the Reason for the classification.
    
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

    #print(f"\n\n* * * * *\nResponse: \n\n{resp}\n\n*********\n")
    #st.subheader("Analysis Result:")
    #st.write(f"Fungi: {resp.study}\n Reason2: {resp.reason}")
    return resp.study, resp.reason

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
    # Filter rows where status is 'processed4'
    new_status_df = df[df['status'] == 'processed4']
    
    # If there are no rows with status 'new', return the dataframe as is
    if new_status_df.empty:
        print("No rows with status 'processed4' to process.")
        return df
    
    # Pick a random row from the filtered dataframe
    random_row = new_status_df.sample(n=1)
    
    # Get the index of the random row
    index = random_row.index[0]
    
    # Extract the filename of the random row
    filename = random_row['filename'].values[0]
    
    # Call the process_file function on the filename
    study,reason = process_file(filename)
    
    # Update the row with the return value from the function and update the 'updated' time
    df.at[index, 'study'] = study
    df.at[index, 'studyReason'] = reason
    df.at[index, 'status'] = 'processed5'
    df.at[index, 'updated'] = pd.Timestamp.now()
    
    return df

df_txt=pd.read_csv(DF_FILE)
  
filecount=st.number_input("Number of files", value=3)
progress_bar=st.progress(0)
progress_text = st.empty()
if st.button("Process files : Stage 5"):
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