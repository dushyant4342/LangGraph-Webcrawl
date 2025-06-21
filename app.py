# chatbot_web_search.py

import os
import logging
import requests
import streamlit as st
from dotenv import load_dotenv
from typing import TypedDict, List
from langgraph.graph import StateGraph, END
#from web import run as web_run

from duckduckgo_search import DDGS


import requests

SERPAPI_KEY = os.getenv("SERPAPI_KEY")


load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_URL = (
    f"https://generativelanguage.googleapis.com/v1beta/"
    f"models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Chatbot")

class ChatState(TypedDict):
    query: str
    web_content: str
    final_answer: str
    steps: List[str]

def perform_duckduckgo_search(query: str) -> str:
    with DDGS() as ddgs:
        results = ddgs.text(query, region='wt-wt', safesearch='Moderate', max_results=5)
        snippets = [r["body"] for r in results if "body" in r]
        return "\n\n".join(snippets)

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
workflow.add_node("summarize_web", summarize_web)
workflow.set_entry_point("summarize_web")
workflow.add_edge("summarize_web", END)
app = workflow.compile()

st.set_page_config(page_title="Web Chatbot", page_icon="🔍")
st.markdown("<style>body{background-color:white;color:black;}</style>", unsafe_allow_html=True)
st.title("🔎 Chatbot with Web Search")

user_query = st.text_input("Ask me anything:")

if st.button("Search") and user_query:
    st.write("🔎 Searching web with SERP_API...")
    snippets = perform_serpapi_search(user_query)

    state = {
        "query": user_query,
        "web_content": snippets,
        "final_answer": "",
        "steps": ["Step 1: Web search via DuckDuckGo completed"],
    }

    result = app.invoke(state)
    result["steps"].append("Step 2: Gemini summary completed")

# if st.button("Search") and user_query:
#     st.write("🔎 Searching web...")
#     search_results = web_run({
#         "search_query": [{"q": user_query, "recency": 1, "domains": None}]
#     })
#     snippets = "\n\n".join(hit["snippet"] for hit in search_results["search_query_results"])

#     state = {
#         "query": user_query,
#         "web_content": snippets,
#         "final_answer": "",
#         "steps": ["Step 1: Web search completed"],
#     }

    result = app.invoke(state)
    result["steps"].append("Step 2: Gemini summary completed")

    st.subheader("📋 Steps")
    for s in result["steps"]:
        st.write(s)

    st.subheader("📚 Answer")
    st.write(result["final_answer"])

    st.subheader("🌐 Snippets")
    st.code(result["web_content"], language="text")
