import os
import streamlit as st
from openai import OpenAI
import mysql.connector
import pandas as pd

st.set_page_config(page_title="Agentic SQL Analyst - Grok", page_icon="🤖")
st.title("🤖 Agentic SQL Analyst (Powered by Grok)")

# Render/Railway Environment Variable నుండి కీ ని సేకరిస్తుంది
grok_api_key = os.getenv("GROK_API_KEY")

if not grok_api_key:
    st.error("⚠️ GROK_API_KEY లభించలేదు! Render Variables లో GROK_API_KEY ని యాడ్ చేయండి")
    st.stop()

# Grok Client ಕಾన్ఫిగర్ చేయడం
client = OpenAI(
    api_key=grok_api_key,
    base_url="https://api.x.ai/v1",
)

# Database Connection (AIVEN Credentials ఉంటే వాడటానికి)
def run_sql_query(query):
    try:
        db_host = os.getenv("AIVEN_HOST")
        db_user = os.getenv("AIVEN_USER")
        db_pass = os.getenv("AIVEN_PASSWORD")
        db_port = os.getenv("AIVEN_PORT", 3306)
        db_name = os.getenv("AIVEN_DB")

        if db_host and db_user and db_pass:
            conn = mysql.connector.connect(
                host=db_host,
                user=db_user,
                password=db_pass,
                port=int(db_port),
                database=db_name
            )
            df = pd.read_sql(query, conn)
            conn.close()
            return df, None
        else:
            return None, "Database Credentials లభించలేదు (లేదా మోక్ క్వెరీ మోడ్)."
    except Exception as e:
        return None, str(e)

# User Query Input
user_prompt = st.text_input("Ask a question about your database:", placeholder="Show all tables")

if user_prompt:
    try:
        with st.spinner("Grok AI క్వెరీని తయారుచేస్తోంది..."):
            response = client.chat.completions.create(
                model="grok-4.6",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert SQL analyst. Convert plain English to a SQL query. Output ONLY raw SQL query code, without markdown formatting or markdown backticks."
                    },
                    {"role": "user", "content": user_prompt}
                ]
            )
            
            clean_sql = response.choices[0].message.content.strip().replace("```sql", "").replace("```", "").strip()
            
            st.subheader("Generated SQL Query:")
            st.code(clean_sql, language="sql")

            # Database క్వెరీ ఎగ్జిక్యూషన్
            df, err = run_sql_query(clean_sql)
            if df is not None:
                st.subheader("Query Results:")
                st.dataframe(df)

    except Exception as e:
        st.error(f"Grok API ఎర్రర్: {str(e)}")
