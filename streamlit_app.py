import streamlit as st
import requests
import pandas as pd

# Constants
API_URL = "http://127.0.0.1:8000/analyze"

st.set_page_config(page_title="StatBot Pro", layout="wide", page_icon="📊")

st.title("📊 StatBot Pro: Autonomous Data Analyst")
st.markdown("Upload a CSV file and ask questions in natural language. The AI will write Pandas code to analyze it and generate charts.")

# Sidebar for file upload
with st.sidebar:
    st.header("1. Upload Data")
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
    
    if uploaded_file:
        st.success("File uploaded successfully!")
        # Preview the data
        df_preview = pd.read_csv(uploaded_file)
        st.subheader("Data Preview")
        st.dataframe(df_preview.head(3))

# Main Chat Interface
st.header("2. Ask Questions")

# Initialize chat history in session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message.get("chart_url"):
            st.image(message["chart_url"])

# User Input
if prompt := st.chat_input("e.g., 'What is the average sale price grouped by Location?'"):
    if not uploaded_file:
        st.error("Please upload a CSV file in the sidebar first.")
    else:
        # 1. Add user message to UI
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # 2. Call the FastAPI backend
        with st.chat_message("assistant"):
            with st.spinner("Analyzing data and generating code..."):
                try:
                    # Reset file pointer to beginning before sending
                    uploaded_file.seek(0)
                    
                    files = {"file": (uploaded_file.name, uploaded_file, "text/csv")}
                    data = {"query": prompt}
                    
                    response = requests.post(API_URL, files=files, data=data)
                    
                    if response.status_code == 200:
                        result = response.json()
                        answer = result.get("response")
                        chart_url = result.get("chart_url")

                        # Display text response
                        st.markdown(answer)
                        
                        # Display chart if one was generated
                        if chart_url:
                            st.image(chart_url)

                        # Save to history
                        st.session_state.messages.append({
                            "role": "assistant", 
                            "content": answer,
                            "chart_url": chart_url
                        })
                    else:
                        st.error(f"Backend Error: {response.text}")
                
                except requests.exceptions.ConnectionError:
                    st.error("Could not connect to the backend. Is FastAPI running on port 8000?")