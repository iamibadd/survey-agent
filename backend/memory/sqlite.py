from langchain.memory import ConversationBufferMemory
from langchain_community.chat_message_histories import SQLChatMessageHistory

from utils.constants import CHAT_HISTORY_KEY, INPUT_KEY
from config.db import engine


# ============================================================
# Retrieve SQL-backed chat history
# ============================================================
def GetHistory(session_id: int):
    """
    Initialize SQLChatMessageHistory for a given session ID.

    Args:
        session_id (int): Unique identifier for the conversation session.

    Returns:
        SQLChatMessageHistory: Configured message history instance that stores
        chat logs in a SQL database (using SQLAlchemy engine).
    """
    history = SQLChatMessageHistory(
        # Ensure session_id is string for DB compatibility
        session_id=str(session_id),
        connection=engine,           # Active SQLAlchemy DB engine
        # Table name constant (e.g., "chat_history")
        table_name=CHAT_HISTORY_KEY
    )

    return history


# ============================================================
# Create LangChain memory backed by SQL message history
# ============================================================
def GetMemory(session_id: int):
    """
    Initialize ConversationBufferMemory with SQLChatMessageHistory as the storage backend.

    This allows LangChain to persist conversation state between interactions,
    making the chat session context-aware and stateful across requests.

    Args:
        session_id (int): Unique identifier for the conversation session.

    Returns:
        ConversationBufferMemory: Configured memory object with SQL persistence.
    """
    history = GetHistory(session_id=session_id)

    memory = ConversationBufferMemory(
        chat_memory=history,         # Store messages using SQL-based history
        return_messages=True,        # Return message objects instead of plain text
        memory_key=CHAT_HISTORY_KEY,  # Key used for retrieving chat history
        input_key=INPUT_KEY,         # Key used for identifying user input field
    )

    return memory


# ============================================================
# Clear chat memory for a given session
# ============================================================
def ClearMemory(session_id: int):
    """
    Clears all stored chat messages for a specific session from the SQL database.
    Useful when deleting a session or resetting conversation history.

    Args:
        session_id (int): Unique identifier for the conversation session.
    """
    try:
        history = GetHistory(session_id=session_id)
        history.clear()  # Removes all stored chat records for this session
    except Exception as e:
        print(f"Failed to clear chat memory for session {session_id}: {e}")
