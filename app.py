
import streamlit as st
import requests
import json

# ==========================================
# 1. MOCK DATABASE (JSON/Dictionary)
# ==========================================
# This acts as our database for the hackathon MVP. 
# It contains mock data of textbook availability around UM.
UM_DATABASE = {
    "Calculus 101": {
        "New": 150.00,
        "Used_Seniors": 50.00,
        "UM_Library_Copies": 2,
        "Digital_PDF": "Not Available"
    },
    "Introduction to Programming": {
        "New": 120.00,
        "Used_Seniors": 80.00,
        "UM_Library_Copies": 0,
        "Digital_PDF": "Free on UM OpenSource"
    },
    "Business Management": {
        "New": 90.00,
        "Used_Seniors": "Out of Stock",
        "UM_Library_Copies": 5,
        "Digital_PDF": "Not Available"
    }
}

# ==========================================
# 2. Z.AI MODEL INTEGRATION FUNCTION
# ==========================================
def call_zai_api(user_syllabus, database_context):
    # Fetch the key securely from secrets.toml
    try:
        API_KEY = st.secrets["ZAI_API_KEY"]
    except KeyError:
        return "Error: API Key not found. Please check your secrets configuration."
    
    ENDPOINT_URL = "https://api.z.ai/v1/chat/completions"
    
    # The Prompt Engineering (Crucial for judging)
    system_prompt = """
    You are EduShare UM, a financial advisor AI for Universiti Malaya students.
    Your goal is to help students get their required textbooks for the absolute lowest cost possible.
    Analyze the student's requested books against the provided UM Database.
    Prioritize Free (Library/PDF) > Used > New.
    Output a clear, step-by-step purchasing strategy and calculate the total estimated cost.
    """
    
    user_prompt = f"Student's Required Books:\n{user_syllabus}\n\nUM Database Availability:\n{json.dumps(database_context)}"

    # Standard API Request Payload (Adjust based on exact Z.AI documentation)
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "z-ai-glm", # Replace with the specific model name given by organizers
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.3 # Low temperature for logical, consistent financial outputs
    }

    try:
        # --- FOR MVP / IF API IS NOT YET CONNECTED ---
        # If you haven't received the API key yet, comment out the request below 
        # and uncomment the mock response to test your UI.
        
        # response = requests.post(ENDPOINT_URL, headers=headers, json=payload)
        # response_data = response.json()
        # return response_data['choices'][0]['message']['content']
        
        # MOCK RESPONSE (Delete this block once you plug in the real API)
        return """
        **🎓 EduShare UM Strategy:**
        1. **Introduction to Programming:** Do not buy this! It is available for free on the UM OpenSource portal. (Cost: RM 0)
        2. **Calculus 101:** Rent this from the UM Library immediately. There are 2 copies left. If you miss it, buy it used from a senior. (Cost: RM 0 - RM 50)
        3. **Business Management:** Borrow from the library (5 copies available). (Cost: RM 0)
        
        **Total Estimated Cost:** RM 0.00 (Savings of RM 360.00 compared to buying new!)
        """
    except Exception as e:
        return f"Error connecting to Z.AI API: {e}"

# ==========================================
# 3. STREAMLIT FRONTEND UI
# ==========================================
st.set_page_config(page_title="EduShare UM", page_icon="📚")

st.title("📚 EduShare UM")
st.subheader("Smart Textbook & Resource Optimizer")
st.write("Stop wasting money on new textbooks! Paste your course syllabus or book list below, and our AI will find the cheapest way for you to get them around the Universiti Malaya campus.")

# Input Form
with st.form("syllabus_form"):
    student_input = st.text_area(
        "Paste your required books/courses here:",
        placeholder="E.g., I need books for Calculus 101 and Introduction to Programming."
    )
    
    submit_button = st.form_submit_button(label="Find My Books 🔍")

# Output Section
if submit_button:
    if not student_input.strip():
        st.warning("Please enter your required books first!")
    else:
        with st.spinner("Analyzing UM Library and Senior listings via Z.AI..."):
            # Call the AI function
            ai_strategy = call_zai_api(student_input, UM_DATABASE)
            
            # Display results
            st.success("Analysis Complete!")
            st.markdown("### Your Procurement Strategy")
            st.info(ai_strategy)
            
            st.caption("Powered by Z.AI GLM")
