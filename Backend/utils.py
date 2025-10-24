import os
from fastapi import UploadFile
import openai
import threading
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

UPLOAD_FOLDER = "storage"




from pathlib import Path
from llama_parse import LlamaParse

LLAMA_CLOUD_API_KEY = ""
os.environ["LLAMA_CLOUD_API_KEY"] = ""

API_KEY = ""
client = openai.OpenAI(api_key=API_KEY)

MODEL = "gpt-4.1"
thread_local = threading.local()

def get_llm_client():
    """Get thread-local LLM client to ensure thread safety"""
    if not hasattr(thread_local, 'llm'):
        thread_local.llm = ChatOpenAI(
            model=MODEL,
            temperature=0.0,
            api_key=API_KEY
        )
    return thread_local.llm


def save_pdf_file(file: UploadFile) -> str:
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    with open(file_path, "wb") as buffer:
        buffer.write(file.file.read())
    return file_path


def get_instruction_prompt():
    return """
        You are an expert career coach and resume analyst. Given the candidate resume and job description, provide a detailed JSON response containing the following fields:
        make sure to include only the following things in the json. Here's a example json
        json
        {
          "compatibility_score": "<Score the candidate's compatibility with the job from 0 to 100. only give the number. Don't give any other things here.>",
          "ATS_Format_Score": "ATS Format Score for this Resume from 0 to 100. This Score should only be calculated on other basic except the skills. This score will signify how much ATS compatible this resume is on the basis of formatting, layouts, file format, keywords used etc.",
          "missing_skills_and_recommendations": [
            {
              "1": "<Name or description>",
              "recommendation": "<How to bridge this gap, such as courses or projects>"
            }
            .......
          ],
          "ats_compatibility_analysis": [
            "<Identify and explain Applicant Tracking System (ATS) compatibility issues. Provide actionable improvements for better scanning.>"
          ]
        }
        
        Instructions:
        * For compatibility_score, provide a numeric score.
        * For missing_skills_and_recommendations, list each critical missing skill or experience along with an actionable recommendation.
        * For ats_compatibility_analysis, list specific ATS-related issues and concrete suggestions.
        * Only return the JSON format as shown above, with no additional commentary.
        * make sure to follow the above example format.
    """

def get_content_prompt(resume, job_description):
    return f'''
         Resume:
         {resume}
    
        
    
        Job Description:
        {job_description}
    '''


def analyze_pdf_content(file_path: str, job_description: str) -> str:
    print(f'parsing using llama parser')
    parser = LlamaParse(result_type="markdown")
    document = parser.load_data(file_path)

    full_text = ""
    for i, doc in enumerate(document, start=1):
        full_text += doc.text
        full_text += "\n\n--- ---\n\n"

    print(f'extracting text from file')
    text_files_dir = "text_files"
    # os.makedirs(text_files_dir, exist_ok=True)
    base_name = 'resume'
    text_file_name = f"{base_name}.txt"
    text_file_path = os.path.join(text_files_dir, text_file_name)

    # Step 1: Write extracted text to the file
    with open(text_file_path, "w", encoding="utf-8") as f:
        f.write(full_text)
    print(f"📁 Saved extracted text to '{text_file_path}'")

    # Step 2: Read the text back from the file
    with open(text_file_path, "r", encoding="utf-8") as f:
        resume = f.read()

    print('calling openai ')
    messages = [
        SystemMessage(content=get_instruction_prompt()),
        HumanMessage(content=get_content_prompt(resume, job_description))
    ]
    response = get_llm_client().invoke(messages)
    print('response got')
    print(response)
    chat_response = response.content
    print('openai responded')
    print('****************************************')
    print(chat_response)
    print('****************************************')


    return chat_response