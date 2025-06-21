import os
import logging
import requests
import streamlit as st
import sqlite3
from dotenv import load_dotenv
from typing import TypedDict, List
from langgraph.graph import StateGraph, END

load_dotenv()
SERPAPI_KEY = os.getenv("SERPAPI_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_URL = (
    f"https://generativelanguage.googleapis.com/v1beta/"
    f"models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Chatbot")

# DB setup
conn = sqlite3.connect("chat_history.db")
c = conn.cursor()
c.execute("""
    CREATE TABLE IF NOT EXISTS chat (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        query TEXT,
        answer TEXT
    )
""")
conn.commit()

class ChatState(TypedDict):
    query: str
    web_content: str
    final_answer: str
    steps: List[str]

def perform_serpapi_search(query: str) -> str:
    url = "https://serpapi.com/search"
    params = {
        "engine": "google",
        "q": query,
        "api_key": SERPAPI_KEY,
        "num": 2
    }
    res = requests.get(url, params=params)
    res.raise_for_status()
    data = res.json()
    snippets = [r.get("snippet") for r in data.get("organic_results", []) if r.get("snippet")]
    return "\n\n".join(snippets)

def sanitize_query(state: ChatState) -> ChatState:
    logger.info("🧹 Sanitizing query")
    state["query"] = state["query"].strip().lower()
    state["steps"].append("Sanitized query")
    return state

def search_web(state: ChatState) -> ChatState:
    logger.info("🌐 Searching web via SerpAPI")
    snippets = perform_serpapi_search(state["query"])
    state["web_content"] = snippets
    state["steps"].append("Fetched web content")
    return state

def refine_answer(state: ChatState) -> ChatState:
    logger.info("🪄 Refining answer")
    state["final_answer"] = state["final_answer"] + "\n\n(Refined by Gemini)"
    state["steps"].append("Refined summary")
    return state


def summarize_web(state: ChatState) -> ChatState:
    logger.info("🧠 Summarizing via Gemini")
    state["steps"].append("Step 2: Gemini summary")
    prompt = f"Question: {state['query']}\nContent:\n{state['web_content']}"
    body = {"contents": [{"parts": [{"text": prompt}]}]}
    try:
        res = requests.post(
            GEMINI_URL, headers={"Content-Type": "application/json"}, json=body
        )
        res.raise_for_status()
        state["final_answer"] = res.json()["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
        logger.error(f"Gemini error: {e}")
        state["steps"].append("❌ Gemini summary failed")
        state["final_answer"] = "Sorry, no answer available."
    return state


workflow = StateGraph(ChatState)
workflow.add_node("sanitize_query", sanitize_query)
workflow.add_node("search_web", search_web)
workflow.add_node("summarize_web", summarize_web)
workflow.add_node("refine_answer", refine_answer)

workflow.set_entry_point("sanitize_query")

workflow.add_edge("sanitize_query", "search_web")
workflow.add_edge("search_web", "summarize_web")
workflow.add_edge("summarize_web", "refine_answer")
workflow.add_edge("refine_answer", END)

app = workflow.compile()

st.set_page_config(page_title="Web Chatbot", page_icon="🔍", layout="centered", initial_sidebar_state="auto")
st.markdown("""
    <style>
        html, body, [class*="css"]  {
            background-color: white !important;
            color: black !important;
        }
    </style>
""", unsafe_allow_html=True)

st.title("🔎 Chatbot with Web Search")

# Sidebar tools used
with st.sidebar:
    st.header("🛠 Tools Used")
    st.markdown("""
    - **LangGraph**: State machine for workflow
    - **SERPAPI**: Google search results
    - **Gemini API**: Summarization
    - **Streamlit**: UI framework
    - **SQLite**: Chat history storage
    """)

# Display chat history
st.subheader("💬 Chat History")
c.execute("SELECT query, answer FROM chat ORDER BY id DESC")
rows = c.fetchall()
for query, answer in rows:
    with st.chat_message("user"):
        st.markdown(query)
    with st.chat_message("assistant"):
        st.markdown(answer)

# Chat input
if prompt := st.chat_input("Ask me anything..."):
    st.chat_message("user").markdown(prompt)

    state = {
        "query": prompt,
        "web_content": "",
        "final_answer": "",
        "steps": [],
    }

    result = app.invoke(state)
    result["steps"].append("Step 2: Gemini summary completed")

    # Store in DB
    c.execute("INSERT INTO chat (query, answer) VALUES (?, ?)", (prompt, result["final_answer"]))
    conn.commit()

    with st.chat_message("assistant"):
        st.markdown(result["final_answer"])

    with st.expander("📋 Process Steps"):
        for s in result["steps"]:
            st.write(s)

    with st.expander("🌐 Snippets"):
        st.code(result["web_content"], language="text")

    with st.expander("📊 LangGraph Flow"):
        st.code("sanitize_query → search_web → summarize_web → refine_answer → insert_intodb → END", language="text")

