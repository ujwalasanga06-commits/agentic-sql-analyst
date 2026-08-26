import os
import streamlit as st
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent
from langchain_google_genai import ChatGoogleGenerativeAI

st.set_page_config(page_title="Agentic SQL Analyst", page_icon="📊")
st.title("🤖 Agentic SQL Analyst")

# 1. Database Connection
db_user = "avnadmin"
db_password = "AVNS_BiaiSmKwKGuGiZH25wh"  # మీ Aiven Password ఇక్కడ ఇవ్వండి
db_host = "mysql-36c5aa20-ujwalasanga06-fb74.j.aivencloud.com"
db_port = "22381"
db_name = "defaultdb"

db_uri = f"mysql+mysqlconnector://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

@st.cache_resource
def init_db():
    return SQLDatabase.from_uri(db_uri)

try:
    db = init_db()
    st.sidebar.success("✅ Connected to Aiven Cloud Database!")
except Exception as e:
    st.sidebar.error(f"❌ Connection Failed: {e}")
    st.stop()

# 2. Gemini API Setup
google_api_key = "AIzaSyC3g0qNbrOysUSD3lwSwOQnR6JUFZ9oAOI"  # మీ Gemini API Key ఇక్కడ ఇవ్వండి

llm = ChatGoogleGenerativeAI(
    model="gemini-pro",
    google_api_key=google_api_key,
    temperature=0
)

# 3. Create SQL Agent
agent_executor = create_sql_agent(
    llm=llm,
    db=db,
    agent_type="zero-shot-react-description",
    verbose=True
)

# 4. Search UI
user_query = st.text_input("Ask a question about your database:", placeholder="e.g., Show all tables")

if user_query:
    with st.spinner("AI Agent is writing SQL and fetching data..."):
        try:
            response = agent_executor.run(user_query)
            st.write("### 📈 Analysis Result:")
            st.success(response)
        except Exception as e:
            st.error(f"Error: {e}")
