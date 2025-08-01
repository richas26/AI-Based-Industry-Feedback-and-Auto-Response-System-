import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os
from dotenv import load_dotenv
from prompts import get_prompt
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

# Load environment variables for API key
load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")

# Set the page configuration
st.set_page_config(
    page_title="Eduplus Feedback and Analysis",
    page_icon="📊",
    layout="centered",
    initial_sidebar_state="auto",
)

# Load LLM
def load_llm():
    return ChatGroq(temperature=0.4, model_name="llama3-8b-8192", api_key=groq_api_key)

# Convert CSV to dictionary
def csv_to_dict(file_path):
    df = pd.read_csv(file_path)
    return df.to_dict(orient='list')

# App section 1: Feedback Summarization
def feedback_summarization():
    st.title("Eduplus Industry Feedback Summarization")
    st.write("Upload a CSV file to generate a summary.")
    
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
    
    if uploaded_file:
        st.write("File uploaded successfully!")
        data_dict = csv_to_dict(uploaded_file)
        
        company_names = list(set(data_dict.get('Name of The Company', [])))
        student_names = list(set(data_dict.get('Name of The Student', [])))
        
        # Handle potential column mismatches for VIIT mentor names
        if 'Faculty Mentor from VIIT' in data_dict:
            mentor_names = list(set(data_dict['Faculty Mentor from VIIT']))
        elif 'Faculty Mentor from VIIT ' in data_dict:  # Check for trailing spaces
            mentor_names = list(set(data_dict['Faculty Mentor from VIIT ']))
        else:
            mentor_names = []
            st.error("The column 'Faculty Mentor from VIIT' is missing in the uploaded CSV.")
        
        # Summary dropdown
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
        
        llm = load_llm()
        
        if summary_option != "Select an option" and (not additional_input or additional_input.strip()):
            prompt_text = get_prompt(summary_option, data_dict, additional_input)
            
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
            
            input_data = {
                "input": f"Summarize the feedback data for {summary_option}.",
                "feedback_data": prompt_text
            }
            
            chain = prompt_template | llm
            
            if st.button("Generate Summary"):
                st.write("Summarizing feedback data...")
                response = chain.invoke(input_data)
                cleaned_response = response.content.replace("\n\n", "\n").replace("\n", "\n\n") if hasattr(response, 'content') else str(response)
                st.write("Summary:")
                st.write(cleaned_response)

# App section 2: Performance Analysis
def performance_analysis():
    st.title("Student and Company Performance Analysis")
    data = pd.read_csv("Industry Mentor Feedback Form (AY 2023-24).csv")
    
    st.sidebar.header("Filters")
    companies = data['Name of The Company'].unique()
    selected_company = st.sidebar.selectbox("Select a Company", companies)
    
    filtered_data = data[data['Name of The Company'] == selected_company]
    students_in_company = filtered_data['Name of The Student'].unique()
    selected_student = st.sidebar.selectbox("Select a Student (Optional)", ['All'] + list(students_in_company))
    
    st.header(f"Analysis for {selected_company}")
    
    if not filtered_data.empty:
        # Skill averages plot
        st.subheader("Skill Averages of Students in the Company")
        numeric_cols = [
            'i) Communication & Presentation Skills',
            'ii) Confidence level',
            'iii) Creativity',
            'iv) Planning & Organizational skills',
            'v) Adaptability',
            'vi) Knowledge',
            'vii) Attitude & Behaviour at work',
            'viii) Analytical Skills',
            'ix) Societal Understanding',
            'x) Ethics',
            'xi) Team Work'
        ]
        skill_means = filtered_data[numeric_cols].mean()
        fig1, ax1 = plt.subplots(figsize=(8, 6))
        ax1.bar(skill_means.index, skill_means, color='skyblue')
        ax1.set_title('Average Skills Across Students', fontsize=14)
        ax1.set_xticklabels(skill_means.index, rotation=45, ha='right')
        ax1.set_ylabel('Average Score')
        st.pyplot(fig1)
        
        # Hiring insights
        st.subheader("Hiring Insights for the Selected Company")
        if '4. Will you consider the student to be absorbed in your organization (if chance given)?' in filtered_data.columns:
            hire_yes_count = filtered_data['4. Will you consider the student to be absorbed in your organization (if chance given)?'].str.strip().str.lower().value_counts().get('yes', 0)
            st.write(f"Students Considered for Hiring: **{hire_yes_count}**")
        
        # Rehire feedback
        st.subheader("Company's Feedback on Rehiring VIIT Students")
        if 'Would you like to take VIIT students again in next year?' in filtered_data.columns:
            rehire_yes_count = filtered_data['Would you like to take VIIT students again in next year?'].str.strip().str.lower().value_counts().get('yes', 0)
            st.write(f"Positive Responses (Yes): **{rehire_yes_count}**")
        
        # Pie chart for student performance
        st.subheader("Overall Performance of Students")
        filtered_data['Overall Performance'] = filtered_data[numeric_cols].mean(axis=1)
        student_averages = filtered_data.groupby('Name of The Student')['Overall Performance'].mean()
        fig2, ax2 = plt.subplots(figsize=(8, 6))
        ax2.pie(student_averages, labels=student_averages.index, autopct='%1.1f%%', startangle=90, colors=plt.cm.tab20.colors)
        ax2.set_title("Overall Performance of Students", fontsize=14)
        st.pyplot(fig2)
    
    if selected_student != 'All':
        st.header(f"Performance of {selected_student}")
        student_data = filtered_data[filtered_data['Name of The Student'] == selected_student]
        if not student_data.empty:
            student_performance = student_data[numeric_cols].T
            student_performance.columns = ['Rating']
            st.bar_chart(student_performance)

# Main app logic
tab1, tab2 = st.tabs(["Feedback Summarization", "Performance Analysis"])
with tab1:
    feedback_summarization()
with tab2:
    performance_analysis()
