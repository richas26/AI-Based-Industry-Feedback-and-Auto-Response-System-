# app.py
import streamlit as st
import pandas as pd
from prompts import get_prompt
from langchain_groq import ChatGroq
import os
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate

# Set the page configuration (light theme with white background)
st.set_page_config(
    page_title="Eduplus Industry Feedback Summarization",
    page_icon="📊",
    layout="centered",
    initial_sidebar_state="auto",
)

# Load environment variables for API key
load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")

# Load LLM
def load_llm():
    return ChatGroq(temperature=0.4, model_name="llama3-8b-8192", api_key=groq_api_key)

# Extract data from the CSV file
def csv_to_dict(file_path):
    df = pd.read_csv(file_path)
    return df.to_dict(orient='list')

# Streamlit App
st.title("Eduplus Industry Feedback Summarization")
st.write("Upload a CSV file to generate a summary.")

# File uploader
uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

# If a file is uploaded
if uploaded_file:
    st.write("File uploaded successfully!")
    
    # Read the CSV data
    data_dict = csv_to_dict(uploaded_file)

    # Extract unique company names, student names, and VIIT mentor names
    company_names = list(set(data_dict['Name of The Company']))
    student_names = list(set(data_dict['Name of The Student']))
        # Check if 'Faculty Mentor from VIIT' column exists and handle missing columns
    if 'Faculty Mentor from VIIT' in data_dict:
        mentor_names = list(set(data_dict['Faculty Mentor from VIIT']))
    elif 'Faculty Mentor from VIIT ' in data_dict:  # Check for potential extra space
        mentor_names = list(set(data_dict['Faculty Mentor from VIIT ']))
    else:
        mentor_names = []
        st.error("The column 'Faculty Mentor from VIIT' is missing in the uploaded CSV.")

    # Dropdown for summary options
    summary_option = st.selectbox(
        "Select a summary type",
        ["Select an option", "Overall Summary", "Company-wise Summary", "Student-wise Summary", "VIIT-Mentor-wise Summary"]
    )
    
    # Dropdown for additional input based on the selected option
    additional_input = None
    if summary_option == "Company-wise Summary":
        additional_input = st.selectbox("Select a company for the summary", company_names)
    elif summary_option == "Student-wise Summary":
        additional_input = st.selectbox("Select a student for the summary", student_names)
    elif summary_option == "VIIT-Mentor-wise Summary":
        additional_input = st.selectbox("Select a VIIT mentor for the summary", mentor_names)

    # Load the LLM
    llm = load_llm()

    if summary_option != "Select an option" and (not additional_input or additional_input.strip()):
        # Generate a prompt based on the selected summary option and additional input
        prompt_text = get_prompt(summary_option, data_dict, additional_input)
        print(prompt_text)
        
        # Display the selected option and prompt
        st.write(f"Selected Option: {summary_option}")
        
        # Define the prompt template
        prompt_template = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are a helpful assistant that summarizes feedback data for university internship programs."
                ),
                ("human", "{input}"),
                (
                    "system",
                    "Here is the feedback data: {feedback_data}. Provide a structured summary based on this data."
                ),
            ]
        )
        
        # Prepare input data for the prompt
        input_data = {
            "input": f"Summarize the feedback data for {summary_option}.",
            "feedback_data": prompt_text
        }

        # Connect the prompt to the LLM and invoke the chain
        chain = prompt_template | llm
        
        # Send the prompt to the LLM for summarization
        if st.button("Generate Summary"):
            st.write("Summarizing feedback data...")
            
            response = chain.invoke(input_data)
            
            # Extract the content from the response
            if hasattr(response, 'content'):
                response_content = response.content
            else:
                response_content = str(response)  # Fallback to converting to string if no content attribute

            # Clean up the response
            cleaned_response = response_content.replace("\n\n", "\n").replace("\n", "\n\n")
            
            st.write("Summary:")
            st.write(cleaned_response)  # Display LLM response (summary)
