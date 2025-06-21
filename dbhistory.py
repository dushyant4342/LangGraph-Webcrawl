import sqlite3

# Connect to the database
conn = sqlite3.connect("chat_history.db")
c = conn.cursor()

# Fetch all past chats
c.execute("SELECT id, query, answer FROM chat ORDER BY id DESC limit 2")
rows = c.fetchall()

# Print the history
for row in rows:
    print(f"ID: {row[0]}\nQuery: {row[1]}\nAnswer: {row[2]}\n{'--'*50}")