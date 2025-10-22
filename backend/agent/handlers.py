from langchain_core.messages import HumanMessage

from memory.sqlite import GetMemory
from .chains import get_conversation_chain, get_infer_chain, prompt_generator_chain


# =======================================
# Get Agent Response (Main conversation)
# =======================================
async def get_agent_response(session_id: int, purpose: str, user_input: str):
    # Create a conversation chain tied to the current user session
    chain = get_conversation_chain(session_id)

    # Invoke the chain asynchronously:
    # - 'input': user message
    # - 'purpose': optional context for customizing AI behavior
    result = await chain.ainvoke({"input": user_input, "purpose": purpose})

    # Return only the AI’s text output (content)
    return result.content


# =======================================
# Infer Interests (Extract structured insights)
# =======================================
async def get_infer_interests(session_id: int):
    # Retrieve chat memory object for the given session
    memory = GetMemory(session_id)

    # Access stored messages (both human and AI)
    history = memory.chat_memory.messages

    # Convert chat history into a readable plain-text format
    # Example:
    #   Human: Hello
    #   AI: Hi there! How can I assist you today?
    history_str = "\n".join(
        [f"{'Human' if isinstance(m, HumanMessage) else 'AI'}: {m.content}" for m in history]
    )

    try:
        # Initialize the interest inference chain
        chain = get_infer_chain()

        # Pass formatted chat history to the model for interest extraction
        result = await chain.ainvoke({"history": history_str})

        # Return parsed inference result (JSON or structured data)
        return result

    except Exception as e:
        # Log and handle inference errors gracefully
        print("Error inferring interests:", e)
        return []


# =============================
# Short Prompt Generator
# =============================
async def prompt_generator(prompt):
    try:
        chain = prompt_generator_chain()

        result = await chain.ainvoke({"prompt": prompt})
        return result
    except Exception as e:
        # Log and handle prompt generation errors gracefully
        err = f"Error generating prompt = {e}"
        print("Error generating prompt:", e)
        return err
