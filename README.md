# Web Chatbot with LangGraph & Gemini
A smart chatbot that fetches real-time web results using SERPAPI, summarizes them using Gemini, and tracks conversation history in SQLite — all orchestrated via LangGraph.

# How It Works
User Query → taken via Streamlit chat UI

LangGraph Workflow:

sanitize_query

search_web using SERPAPI

summarize_web via Gemini API

refine_answer

insert_chat into SQLite DB

Final response shown with steps + snippets + flow.

🛠 Tools Used
🧠 LangGraph: Clean modular flow with visual debugging

🌐 SERPAPI: Real-time Google search results

🔎 Gemini API: Summarizes fetched content

💬 Streamlit: Interactive frontend

🗃 SQLite: Stores past chats

✅ Why This is Better
Web-connected: Pulls live info, not static answers

Stateful & Visual: LangGraph enables structured, explainable flows

Persistent History: View/search old chats instantly

Modular Design: Easy to add steps or improve logic

🧪 Run It
pip install -r requirements.txt
streamlit run app.py







