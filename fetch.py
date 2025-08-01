# app.py
import streamlit as st
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
from prompts import get_prompt
from langchain_groq import ChatGroq
import os
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate

# Set the page configuration
st.set_page_config(
    page_title="Eduplus Industry Feedback Summarization",
    page_icon="📊",
    layout="centered",
    initial_sidebar_state="auto",
)

# Load environment variables for API key
load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")

# Database setup
DATABASE_FILE = "feedback_data.db"

# Create a connection to SQLite database
def init_db():
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    # Create table to store feedback data
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_name TEXT,
            student_name TEXT,
            viit_mentor_name TEXT,
            feedback_data TEXT
        )
    """)
    conn.commit()
    return conn

# Save feedback data to the database
def save_to_db(conn, company_name, student_name, viit_mentor_name, feedback_data):
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO feedback (company_name, student_name, viit_mentor_name, feedback_data)
        VALUES (?, ?, ?, ?)
    """, (company_name, student_name, viit_mentor_name, feedback_data))
    conn.commit()

# Fetch feedback data from the database
def fetch_from_db(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM feedback")
    return cursor.fetchall()

# Initialize database
conn = init_db()

# Streamlit App
st.title("Eduplus Industry Feedback Summarization")
st.write("Upload a CSV file to generate and store summaries. You can also fetch stored data.")

# File uploader
uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

if uploaded_file:
    st.write("File uploaded successfully!")
    data_dict = pd.read_csv(uploaded_file).to_dict(orient='list')

    # Extract unique company names, student names, and VIIT mentor names
    company_names = list(set(data_dict.get('Name of The Company', [])))
    student_names = list(set(data_dict.get('Name of The Student', [])))
    mentor_names = list(set(data_dict.get('Faculty Mentor from VIIT', [])))

    # Dropdown for summary options
    summary_option = st.selectbox(
        "Select a summary type",
        ["Select an option", "Overall Summary", "Company-wise Summary", "Student-wise Summary", "VIIT-Mentor-wise Summary"]
    )
    
    additional_input = None
    if summary_option == "Company-wise Summary":
        additional_input = st.selectbox("Select a company for the summary", company_names)
    elif summary_option == "Student-wise Summary":
        additional_input = st.selectbox("Select a student for the summary", student_names)
    elif summary_option == "VIIT-Mentor-wise Summary":
        additional_input = st.selectbox("Select a VIIT mentor for the summary", mentor_names)

    # Load LLM
    def load_llm():
        return ChatGroq(temperature=0.4, model_name="llama3-8b-8192", api_key=groq_api_key)

    llm = load_llm()

    if summary_option != "Select an option" and (not additional_input or additional_input.strip()):
        prompt_text = get_prompt(summary_option, data_dict, additional_input)
        st.write(f"Selected Option: {summary_option}")

        prompt_template = ChatPromptTemplate.from_messages(
            [
                ("system", "You are a helpful assistant that summarizes feedback data for university internship programs."),
                ("human", "{input}"),
                ("system", "Here is the feedback data: {feedback_data}. Provide a structured summary based on this data."),
            ]
        )

        input_data = {"input": f"Summarize the feedback data for {summary_option}.", "feedback_data": prompt_text}
        chain = prompt_template | llm

        if st.button("Generate Summary"):
            st.write("Summarizing feedback data...")
            response = chain.invoke(input_data)
            response_content = getattr(response, 'content', str(response))
            cleaned_response = response_content.replace("\n\n", "\n").replace("\n", "\n\n")

            st.write("Summary:")
            st.write(cleaned_response)

            # Save feedback data to the database
            save_to_db(conn, summary_option, additional_input or "All", "N/A", cleaned_response)
            st.success("Summary saved to the database!")

# Fetch data button
if st.button("Fetch Stored Data"):
    st.write("Fetching stored data from the database...")
    stored_data = fetch_from_db(conn)
    if stored_data:
        st.write("Stored Feedback Summaries:")
        for record in stored_data:
            st.write(f"ID: {record[0]}, Company: {record[1]}, Student: {record[2]}, Mentor: {record[3]}")
            st.write(f"Summary: {record[4]}")
            st.write("---")
    else:
        st.write("No data found in the database.")
