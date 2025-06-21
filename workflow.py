import networkx as nx
import matplotlib.pyplot as plt

# Define LangGraph-style nodes and edges
G = nx.DiGraph()
G.add_edges_from([
    ("user_query", "sanitize_query"),
    ("sanitize_query", "search_web"),
    ("search_web", "summarize_web"),
    ("summarize_web", "refine_answer"),
    ("refine_answer", "insert_chat"),
    ("insert_chat", "END")
])

# Plotting
plt.figure(figsize=(4, 8))
pos = nx.spring_layout(G, seed=42)  # You can try other layouts too
nx.draw(G, pos, with_labels=True, node_size=3000, node_color="lightblue", font_size=10, font_weight='bold', edge_color="gray")
plt.title("🔁 LangGraph - Chatbot Web Search Flow")
plt.savefig("chatbot_workflow.png")
plt.tight_layout()
plt.show()
plt.savefig("chatbot_workflow.png")
