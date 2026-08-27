import streamlit as st
import mysql.connector
import google.generativeai as genai
import pandas as pd

st.title("🤖 Agentic SQL Analyst")

# 1. Database Connection
@st.cache_resource
def init_db():
    return mysql.connector.connect(
        host="mysql-36c5aa20-ujwalasanga06-fb74.j.aivencloud.com",
        user="avnadmin",
        password="AVNS_BiaiSmKwKGuGiZH25wh",
        database="defaultdb",
        port=22381
    )

try:
    db = init_db()
    st.sidebar.success("Connected to Aiven Cloud Database!")
except Exception as e:
    st.sidebar.error(f"Connection Failed: {e}")
    st.stop()

# 2. Gemini API Setup
google_api_key = "AQ.Ab8RN6J4qn3G01DFbW6IJF7VTGcyTrqGG-mQRtJw_UP-VQQfYQ"
genai.configure(api_key=google_api_key)
model = genai.GenerativeModel('gemini-3.7-flash')

# 3. Search UI
user_query = st.text_input("Ask a question about your database:", placeholder="e.g., show all tables")

if user_query:
    with st.spinner("AI Agent is writing SQL and fetching data..."):
        try:
            prompt = f"Convert this natural language request into a pure MySQL query: '{user_query}'. Return ONLY the raw SQL query with no markdown formatting, no backticks, and no extra text."
            sql_response = model.generate_content(prompt)
            sql_query = sql_response.text.strip().replace("```sql", "").replace("```", "").strip()
            
            st.write(f"**Generated SQL:** `{sql_query}`")
            
            cursor = db.cursor()
            cursor.execute(sql_query)
            
            if cursor.description:
                columns = [col[0] for col in cursor.description]
                results = cursor.fetchall()
                df = pd.DataFrame(results, columns=columns)
                st.write("### Analysis Result:")
                st.dataframe(df)
            else:
                db.commit()
                st.success("Query executed successfully!")
                
        except Exception as e:
            st.error(f"Error: {e}")
