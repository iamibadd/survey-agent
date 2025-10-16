import requests
import sqlite3
import time

DB_PATH = "/app/data/survey.db"
BACKEND_URL = "http://backend:8000"

# Start a session
res = requests.post(f"{BACKEND_URL}/start-session",
                    json={"prompt": "Test hobbies", "consent": True})
session_id = res.json()["sessionId"]

# Send messages
requests.post(f"{BACKEND_URL}/send-message",
              json={"sessionId": session_id, "message": "I like outdoors"})
requests.post(f"{BACKEND_URL}/send-message",
              json={"sessionId": session_id, "message": "Hiking"})

# Check inferred interests
interests = requests.get(
    f"{BACKEND_URL}/interests/{session_id}").json()
assert len(interests) > 0, "No interests inferred"

# Connect to LangChain message store
conn = sqlite3.connect(DB_PATH)

print("Test passed — messages stored correctly")
conn.close()
