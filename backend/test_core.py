import requests
import sqlite3

# Start session
res = requests.post("http://localhost:8000/start-session",
                    json={"prompt": "Test hobbies", "consent": True})
session_id = res.json()["sessionId"]

# Send messages
requests.post("http://localhost:8000/send-message",
              json={"sessionId": session_id, "message": "I like outdoors"})
requests.post("http://localhost:8000/send-message",
              json={"sessionId": session_id, "message": "Hiking"})

# Check interests
interests = requests.get(
    f"http://localhost:8000/interests/{session_id}").json()
assert len(interests) > 0, "No interests inferred"

# Check messages in DB (LangChain's message_store table)
conn = sqlite3.connect("sessions.db")
cursor = conn.cursor()
cursor.execute("SELECT * FROM message_store WHERE session_id=?",
               (str(session_id),))
messages = cursor.fetchall()
# Initial + 2 user messages + responses
assert len(messages) >= 3, "Messages not saved in DB"
print("Test passed")
conn.close()
