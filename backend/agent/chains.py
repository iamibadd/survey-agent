from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder, PromptTemplate
from langchain.schema.runnable import RunnablePassthrough, RunnableLambda
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser

from llms.openai import OpenAIChatModel, OpenAIChatConfig
from memory.sqlite import GetMemory
from utils.constants import CHAT_HISTORY_KEY, AGENT_SYSTEM_PROMPT, AGENT_INFER_PROMPT, MAX_HISTORY_MESSAGES


# Initialize the OpenAI chat model with custom configuration
config = OpenAIChatConfig(temperature=0.7)
model = OpenAIChatModel(config)


# =============================
# Conversation Chain Definition
# =============================
def get_conversation_chain(session_id: int):
    # Define the conversation prompt structure:
    # - System message (defines agent’s role and behavior)
    # - Chat history (previous messages)
    # - Human message (latest user input)
    prompt = ChatPromptTemplate.from_messages([
        ("system", AGENT_SYSTEM_PROMPT),
        MessagesPlaceholder(CHAT_HISTORY_KEY),
        ("human", "{input}")
    ])

    # Load session-based memory object (handles chat history persistence)
    memory = GetMemory(session_id)

    # ----------------------------
    # Helper function: Retrieve limited chat history
    # ----------------------------
    def get_limited_history(_):
        # Load chat history from memory
        history = memory.load_memory_variables({}).get(CHAT_HISTORY_KEY, [])
        # Only return the most recent N messages (to limit token usage)
        return history[-MAX_HISTORY_MESSAGES:]

    # ----------------------------
    # Helper function: Save user message into memory
    # ----------------------------
    def save_user_message(user_input):
        # Extract the text content from different possible structures
        if isinstance(user_input, dict):
            user_text = user_input.get(
                "input") or user_input.get("message") or ""
        else:
            user_text = str(user_input).strip()

        # Save only non-empty messages to memory
        if user_text:
            memory.save_context({"input": user_text}, {"output": ""})
        return user_input

    # ----------------------------
    # Helper function: Save AI message into memory
    # ----------------------------
    def save_ai_message(ai_output):
        # Extract text content depending on object type
        if hasattr(ai_output, "content"):
            ai_text = ai_output.content.strip()
        else:
            ai_text = str(ai_output).strip()

        # Save only non-empty AI responses
        if ai_text:
            memory.save_context({"input": ""}, {"output": ai_text})
        return ai_output

    """
    LCEL Chain Execution Flow:
    --------------------------
    1. "input" → RunnableLambda(save_user_message)
       - Saves user message to memory before processing.
    2. "chat_history" → RunnableLambda(get_limited_history)
       - Fetches only the recent N chat messages for context.
    3. "purpose" → RunnablePassthrough()
       - Placeholder for future extensions (e.g., intent classification).
    4. prompt → Combines system message, chat history, and input.
    5. model → Sends formatted message to LLM for response.
    6. RunnableLambda(save_ai_message)
       - Saves AI-generated output back into memory.
    
    Overall pipeline:
    user input → memory + context → prompt → LLM → AI response → memory update
    """

    chain = (
        {
            "input": RunnableLambda(save_user_message),
            "chat_history": RunnableLambda(get_limited_history),
            "purpose": RunnablePassthrough(),
        }
        | prompt
        | model
        | RunnableLambda(save_ai_message)
    )

    return chain


# =============================
# Interest Inference Chain
# =============================
def get_infer_chain():
    # Build a prompt for inferring structured data (like interests)
    prompt = ChatPromptTemplate.from_template(AGENT_INFER_PROMPT)

    # Define LCEL chain: prompt → LLM → structured JSON parser
    chain = (
        prompt
        | model
        | JsonOutputParser()  # Converts model output into JSON format
    )

    return chain

# =============================
# Short Prompt Generator
# =============================


def prompt_generator_chain():
    # Define a text template that instructs the model to generate
    # a short summary or one-liner based on a user-provided query.
    # The `{prompt}` variable will be replaced dynamically with the actual query at runtime.
    template = "Generate a short summary or one-liner based on the following user query: {prompt}"

    # Create a LangChain prompt object from the above template.
    # This object manages how input variables (like {prompt}) are formatted
    # and passed into the model.
    prompt_template = PromptTemplate.from_template(template)

    # Combine (pipe) the prompt template with the model to form a "chain".
    # The chain represents a complete sequence of operations:
    #   1. Take user input and fill it into the template.
    #   2. Send the resulting prompt to the model.
    #   3. Return the model's generated output in string format.
    #
    # The `|` operator is LangChain's way of composing modular steps into a runnable pipeline.
    chain = prompt_template | model | StrOutputParser()

    # Return the constructed chain so it can be invoked later
    # with specific input data (e.g., {"prompt": "Explain blockchain in one line"}).
    return chain
