# prompts.py

# prompts.py

def get_prompt(option, data_dict, additional_input=None):
    """
    Generates a specific prompt based on the user's selected option and additional input.
    """
    if option == "Overall Summary":
        return overall_summary_prompt(data_dict)
    elif option == "Company-wise Summary":
        return company_summary_prompt(data_dict, additional_input)
    elif option == "Student-wise Summary":
        return student_summary_prompt(data_dict, additional_input)
    elif option == "VIIT-Mentor-wise Summary":
        return viit_mentor_summary_prompt(data_dict, additional_input)
    
def overall_summary_prompt(data_dict):

    company_names = data_dict['Name of The Company'] 
    # Remove duplicates by converting the list to a set, then sort and join into a comma-separated string
    unique_company_names = list(set(company_names))
    student_names = data_dict['Name of The Student']
    company_count=len(unique_company_names)
    student_count=len(student_names)
    prompt = f"""
    Provide a comprehensive overall summary based on the following internship feedback data:
    {data_dict}
    You must not use or generate any data or text based on information outside of this provided context. Only refer to the data provided in this input.

    Ensure the output is structured and covers the following aspects:
    # Output format:
    1. **Number of Students (Total Count)**:{student_count}
    2. **Number of Companies (Total Count)**:{company_count}
    3. **Overall Strengths of the Students:** 
    4. **Overall Weaknesses of  of the Students:**
        - Summarize weaknesses or areas for improvement. Look for common trends in feedback.
    5. **Additional Observations/Insights**:
        - Mention any standout observations or trends in the feedback, if applicable.

    """
    return prompt

def company_summary_prompt(data_dict, company_name):
    """
    Creates a company-wise summary prompt for the LLM.
    """
    company_column = data_dict['Name of The Company']
    
    # Initialize a dictionary to hold filtered feedback data for the selected company
    company_feedback = {key: [] for key in data_dict.keys()}
    
    # Iterate through each row and check if the company name matches
    for idx, company in enumerate(company_column):
        if company == company_name:
            for key in data_dict.keys():
                company_feedback[key].append(data_dict[key][idx])  # Append data for all matching rows
    
    # Count number of students working for the selected company
    student_count = len(company_feedback['Name of The Student'])
    # Join names of students working for the selected company into a comma-separated string
    student_names = ', '.join(company_feedback['Name of The Student'])
    
    prompt = f"""
    Provide a summary for the company '{company_name}' based on the following internship feedback data:
    {company_feedback}
    You must not use or generate any data or text based on information outside of this provided context. Only refer to the data provided in this input.

    Summarize strengths and weaknesses of interns working for this company.
    
    Output format:
    1. **Number of students (give count of students working for selected company)**: 
    2. **Names of students (give names of students working for selected company)**: 
    3. **Faculty Mentor from this company:**
    4. **Faculty Mentor from this company from VIIT:**
    5. **Email-id of Faculty Mentor from this company from VIIT:**
    6. **Overall strengths:**
    7. **Overall weaknesses:**
    8. **Overall Summary:**
    """
    return prompt


def student_summary_prompt(data_dict, student_name):
    """
    Creates a student-wise summary prompt for the LLM.
    """
    student_column = data_dict['Name of The Student']
    
    # Filter rows where the student name matches
    student_feedback = {key: [] for key in data_dict.keys()}
    
    for idx, student in enumerate(student_column):
        if student == student_name:
            for key in data_dict.keys():
                student_feedback[key].append(data_dict[key][idx])
    
    prompt = f"""
    Provide a summary for the student '{student_name}' based on the following internship feedback data:
    {student_feedback}
    Summarize the student's performance, strengths, and areas for improvement.
    """
    return prompt

def viit_mentor_summary_prompt(data_dict, mentor_name):
    """
    Creates a VIIT-Mentor-wise summary prompt for the LLM.
    """
    mentor_column = data_dict['Faculty Mentor from VIIT ']
    
    # Filter rows where the mentor name matches
    mentor_feedback = {key: [] for key in data_dict.keys()}
    
    for idx, mentor in enumerate(mentor_column):
        if mentor == mentor_name:
            for key in data_dict.keys():
                mentor_feedback[key].append(data_dict[key][idx])
    
    prompt = f"""
    Provide a summary for the VIIT Mentor '{mentor_name}' based on the following internship feedback data:
    {mentor_feedback}
    Summarize the mentor's involvement, feedback, and performance trends across students they supervised.
    """
    return prompt






