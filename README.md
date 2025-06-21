Frontend (Streamlit)
User inputs query

Output shows live web result + summary + citations


LangGraph Workflow
Start
  ↓
[Check Query Type] 
  ↓
[SERPAPI/Firecrawl Web Search]
  ↓
[Parse & Chunk Web Content]
  ↓
[Summarize via Gemini]
  ↓
[Return Answer]

Components Needed
Task	                        Tool / API
Web search + crawl	         🔥 Firecrawl API
LangGraph node logic	       ✅ Custom Python functions
Summarization	              🧠 Gemini API (via LangChain Tool)
LangGraph orchestration	    🧩 State + Edge-based routing
Chat UI	                     🖥️ Streamlit


📦 LangGraph Nodes
Node Name	              Role
check_query_type	    Route fact-based vs chit-chat (optional)
search_web	Call      SERP_API/Firecrawl to fetch URLs + content
process_chunks	      Clean, chunk content
summarize_web	        Use Gemini to answer
return_answer	        Send response to frontend