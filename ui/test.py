import streamlit as st

from langchain_community.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, AIMessage, SystemMessage

import json
import os

def test_ref_json():
    with open("output.txt") as f:
        content = f.read()

    chat = ChatOpenAI(model_name="gpt-4o-mini", max_tokens=3000)

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

    paper = "paper_name"

    response = chat(messages)  
    st.write(response.content)
    print(response.content)
    clean_response=response.content.strip()
    clean_response=clean_response.replace("`", "")
    if clean_response.startswith("json"):
        clean_response = clean_response[5:]
    try:
        json_data = json.loads(clean_response)
        for i,record in enumerate(json_data):
            fname=os.path.join(OUTPUT_DIR, f"{paper}_{i:02}.txt")
            with open(fname,"w") as f:
                f.write(json.dumps(record))
    except Exception as e:
        print("Error parsing JSON: ", e)
        with open("output_error.txt","w") as f:
            f.write(response.content)



test_ref_json()