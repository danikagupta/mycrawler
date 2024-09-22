import streamlit as st
import pandas as pd
import os
from datetime import datetime

from typing import TypedDict, Annotated, List, Dict
from pydantic import BaseModel

SRC_DIR="pdf_pages"
DF_FILE="pdf_text.csv"
DIR_PATH="pdf_txt"
TABLE_DIR_PATH="pdf_tables"
MAX_INPUT_LENGTH=100000

class ExperimentTable(BaseModel):
    experiments: List[Dict[str, str]]

from langchain_openai import ChatOpenAI
from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate, SystemMessagePromptTemplate

def one_llm_extract_table(text_content):
    llmModel = ChatOpenAI(model_name="gpt-4o-mini", max_tokens=3000)
    
    parser = PydanticOutputParser(pydantic_object=ExperimentTable)

    system_template = """You are an AI assistant capable of categorizing a paper as Experimental or Summary.
    
    Please create a table with one row for every experimental result. 
    The columns should be: 
      (1) type of dye 
      (2) type of fungi 
      (3) concentration of dye 
      (4) concentration of fungi 
      (5) method of agitation (shaking, stirring etc.) 
      (6) temperature 
      (7) duration 
      (8) pH 
      (9) decolorization result 
      (10) any additional information. 
    If an experiment explored a range of settings, create one row for every unique combination of settings. 
    If the paper contains figures that have additional information - note that in column 10
    
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

    _input = chat_prompt.format_prompt(text=text_content)
    output = llmModel(_input.to_messages())
    resp = parser.parse(output.content)

    print(f"\n\n* * * * *\nResponse: \n\n{resp}\n\n*********\n")
    st.subheader("Analysis Result:")
    st.table(resp.experiments)
    st.write(f"Response: {resp.experiments}")
    return resp.experiments

def process_file(filename,num_bytes,num_words,num_tokens):
    st.write(f"Processing file {filename} with {num_bytes} bytes, {num_words} words, {num_tokens} tokens")
    fqfn=os.path.join(DIR_PATH,filename)
    with open(fqfn,'r') as f:
        text_content=f.read()
    if(num_tokens>MAX_INPUT_LENGTH):
        char_count=int(MAX_INPUT_LENGTH*num_bytes/num_tokens)
        st.write(f"Truncating text content to {char_count} characters")
        text_content=text_content[:char_count]
    table_response=one_llm_extract_table(text_content)
    return table_response

def write_table_response(filename,table_response):
    st.write(f"Writing table response for {filename} with {len(table_response)} datasize")
    fqfn=os.path.join(TABLE_DIR_PATH,filename)
    df=pd.DataFrame(table_response)
    df.to_csv(fqfn,index=False)



def process_random_file(df):
    condition=(df['status'] == 'processed6') & (df['score']==10) & (df['score2']==10) & (df['study']=='Experimental') & ((df['fungi']=='Yes') | (df['fungi']=='YES')) & (df['match_hash']==0)
    #condition=(df['status'] == 'processed6') & (df['score']==10) & (df['score2']==10) & (df['study']=='Experimental') & ((df['fungi']=='Yes') | (df['fungi']=='YES'))
    #condition=(df['status'] == 'processed6') & (df['score']==10) & (df['score2']==10) & (df['study']=='Experimental') &(df['fungi']=='Yes')
    #condition=(df['status'] == 'processed6') & (df['score']==10) & (df['score2']==10) & (df['study']=='Experimental')
    #condition=(df['status'] == 'processed6') & (df['score']==10) & (df['score2']==10)
    #condition=(df['status'] == 'processed6') & (df['score']==10) 
    #condition=(df['status'] == 'processed6')
    new_status_df = df[condition]
    st.write(f"Processing {new_status_df.shape[0]} rows ")
    st.dataframe(new_status_df)
    if new_status_df.empty:
        print("No rows with status=processed6,score=10,score2=10,study=Experimenal,fungi='Yes',match_hash=0 to process.")
        return df
    
    random_row = new_status_df.sample(n=1)
    index = random_row.index[0]
    filename = random_row['filename'].values[0]
    num_bytes= random_row['bytes'].values[0]
    num_words= random_row['words'].values[0]
    num_tokens= random_row['tokens'].values[0]
    st.write(f"Processing file {filename}: Got {num_bytes} bytes, {num_words} words, {num_tokens} tokens")
    print(f"Processing file {filename}: Got {num_bytes} bytes, {num_words} words, {num_tokens} tokens")
    
    # Call the process_file function on the filename
    table_response = process_file(filename,num_bytes,num_words,num_tokens)

    write_table_response(filename,table_response)
    
 

    df.at[index, 'status'] = 'processed7'
    df.at[index, 'updated'] = pd.Timestamp.now()
    
    return df

df_txt=pd.read_csv(DF_FILE)
    
filecount=st.number_input("Number of files", value=3)
progress_bar=st.progress(0)
progress_text = st.empty()
if st.button("Extract files : Stage 1"):
    start_time = datetime.now()
    for i in range(filecount):
        progress_bar.progress(i/filecount)
        process_random_file(df_txt)
        df_txt.to_csv(DF_FILE,index=False)

        elapsed_time = datetime.now() - start_time
        elapsed_seconds = int(elapsed_time.total_seconds())
        remaining_seconds=int((elapsed_seconds*(filecount-i))/(i+1))
        total_seconds=elapsed_seconds+remaining_seconds
        minutes, seconds = divmod(elapsed_seconds, 60)
        rem_min, rem_sec = divmod(remaining_seconds, 60)
        tot_min, tot_sec = divmod(total_seconds,60)
        progress_text.text(f"Processed {i + 1} of {filecount} files | Time elapsed: {minutes}m {seconds}s ; remaining {rem_min}m {rem_sec}s ; total {tot_min}m {tot_sec}s")
progress_bar.progress(1)
st.title("Completed one run")