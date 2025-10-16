# AI-Guided Dynamic Survey Agent

## Summary

The app features an AI survey agent called "Surveyor" that chats with users, asks adaptive questions to learn their interests, and shows a live ranked list of inferred interests with explanations. The app runs locally, uses a real LLM (`openai/gpt-4o-mini`) via OpenRouter, and saves sessions to a SQLite database. I kept it simple, easy to run, and clear to review, all within the 6-hour timebox. The README explains how it works and my choices in plain English.

## Technology Stack and Key Decisions

- **Backend**: FastAPI – Quick to build, supports async for real-time, and has a nice Swagger UI for testing.
- **Database**: SQLite – Local, lightweight, and easy to set up with no external dependencies.
- **LLM**: OpenRouter with OpenAI gpt-4o-mini – Chosen for its conversational ability and flexibility with a custom API key from openrouter.ai.
- **Other**: LangChain for LLM chaining, SQLAlchemy for ORM, Docker for easy deployment.
- **Frontend**: React with Vite.
  Why this stack? Familiar tools for rapid development, full Python ecosystem, and Docker simplifies running locally.

## How the Conversation Works

The agent, "Surveyor," starts with a user-entered prompt (e.g., "Help me find hobbies"). It greets the user, explains it’s here to learn their interests, and asks a simple question (e.g., "What do you enjoy doing in your free time?"). It adapts questions based on past answers—e.g., if you mention outdoors, it might ask about hiking or camping. After about 5-7 exchanges, it stops or lets you pause/reset. Context is managed by keeping only the last 15 messages in memory, with older ones stored in the database but not sent to the LLM to avoid token overload.

## How Interests Are Determined

Interests are inferred after each user message. The backend sends the chat history to the LLM with a prompt asking for 3-5 high-level interests (e.g., "travel," "fitness") with confidence scores (0.0-1.0) and reasons (e.g., "High confidence because you mentioned hiking"). The results are ranked by confidence, saved to the database, and shown live in the interest panel via API calls.

## Data Design

We store sessions (ID, prompt, consent, paused status) to track conversations, messages (role, content) to save the chat, and interests (name, confidence, rationale) linked to sessions for insights. Why? To keep the chat stateful and show ranked interests. Privacy: Only high-level interests, no sensitive data; consent is required. Retention: Local storage, user can delete sessions via API.

## Interest Ranking

The system ranks interests by LLM-assigned confidence (highest first). Reasons are short and clear, like "Medium confidence because you mentioned outdoors casually." This keeps it simple and understandable, relying on the LLM’s natural analysis of the chat.

## AI Management

1. **Provider: OpenRouter**

   What it means: OpenRouter is the platform you’re using to access an LLM (large language model). Think of it as a gateway that allows you to interact with models like GPT-4o-mini via your own API key.

   Why it matters: Instead of using OpenAI’s API directly, OpenRouter lets you manage access, keys, and usage in one place, often with custom routing and extra features.

2. **Model: OpenAI gpt-4o-mini**

   GPT-4o-mini: This is a smaller, more efficient variant of OpenAI’s GPT-4 series.

   “Mini” means it’s faster, lighter, and cheaper to run than full GPT-4 models.

   Capabilities: It’s optimized for conversational tasks, so it’s good at chatting, summarizing, answering questions, etc.

   Chosen for conversational skills: You picked this model specifically because it handles dialogue naturally and smoothly.

3. **Availability via openrouter.ai with a custom key**

   Custom key: You’re using your own API key, which allows authentication and personalized usage limits.

   Advantage: This gives control over who can use the model and keeps usage separate from public or shared accounts.

4. **Controlled tone**

   System prompt sets “Surveyor”:

   A “system prompt” is like instructions you give the model before any conversation starts.

   In this case, the model’s persona is “Surveyor” — friendly, adaptive, avoids sensitive topics.

   Why it matters: The model won’t suddenly go off-topic or engage in controversial topics. It maintains a consistent tone, which is important for surveys or customer-facing interactions.

5. **Kept manageable by limiting history to 15 messages**

   Message history: The model remembers previous messages in the conversation to provide context.

   Limit to 15: Keeps the memory small, so the model runs faster and avoids performance or token limit issues.

   Effect: Old context is forgotten, so conversations stay concise and responsive.

   . Using concise prompts

   Short and precise instructions are sent to the model to make it answer efficiently and reduce cost.

   Combined with limited history, this ensures smooth and predictable behavior without overwhelming the model.

## Stretch Ideas (Partially Implemented)

- Questions adapt: Seen in the chat flow with follow-ups based on answers.
- Relevant context: Limited to 15 messages for memory efficiency.
- Expand interest: Not implemented but could add a detail endpoint.
- Previous sessions: Not done, but could load summaries from DB.
- Logging: Would track question times for improvement.
- Consistency: Would run same convo multiple times, check interest variation <20%.
- Privacy workflow: Basic consent; could add data sharing later.

## How to Run Locally

1. Clone the repo: `git clone https://github.com/iamibadd/survey-agent.git`
2. Navigate to the project folder: `cd survey-agent`
3. Open the `.env` file in the root folder and replace:
   - `OPENAI_API_KEY=your-key-from-openrouter.ai` (get it from https://openrouter.ai/)
4. Build the Docker container: `docker-compose up --build`
5. Open your browser at http://localhost:8000/docs (use the FastAPI Swagger UI to test endpoints).
6. Total setup time: ~5 minutes if Docker and Docker Compose are installed.

## Short Demo Script (Happy Path)

- Start the app with `docker-compose up` and go to the [app](http://localhost:5173/).
- Start a new session by entering a system prompt, like "Help me discover my hobbies," to set the tone and purpose.
- Review the privacy and consent explanation in the app to understand what data is stored, confirming your consent choice.
- Engage in a chat-style conversation by replying to the agent’s concise, adaptive questions (e.g., respond "I enjoy outdoors" to "What do you enjoy doing in your free time?").
- Watch the live interest panel on the right sidebar under "Ranked Interests" update with ranked interests and short rationales based on your answers.
- Control the flow by clicking the `Pause` button to stop questioning, then `Resume` to continue, or click `Reset` to start over or delete the session.

## One Meaningful Test

A basic end-to-end test (`test_core.py`) uses `requests` to:

- Start a session with prompt "Test hobbies" and consent true.
- Send two messages: "I like outdoors" and "Hiking".
- Check if interests are inferred (asserts at least one interest).
- Verifies messages are stored in the SQLite DB at `/app/data/survey.db`.

_This test runs automatically when the app starts. This proves the core flow: session start → chat → interest inference → persistence._

## Endpoints/External Interfaces

### 1. Start a New Chat Session

- **Endpoint**: `/start-session`
- **Method**: `POST`
- **Description**: Creates a new chat session with an initial user prompt and returns the session ID along with the AI's initial response.
- **Request Body**:
  ```json
  {
    "prompt": "string", // Initial user message to start the session
    "consent": true // User consent for session creation
  }
  ```
- **Response**:
  ```json
  {
    "sessionId": "integer",
    "initialMessage": "string"
  }
  ```
- **Errors**:
  - 422: Invalid request body (e.g., missing or invalid fields).

### 2. Send a Message to the Agent

- **Endpoint**: `/send-message`
- **Method**: `POST`
- **Description**: Sends a user message to an existing session and returns the AI's response. Also updates inferred user interests based on the conversation.
- **Request Body**:
  ```json
  {
    "sessionId": "integer", // ID of the session
    "message": "string" // User's message
  }
  ```
- **Response**:
  ```json
  {
    "agentMessage": "string" // AI's response to the message
  }
  ```
- **Errors**:
  - 404: Session not found or paused.
  - 422: Invalid request body.

### 3. Retrieve Inferred Interests

- **Endpoint**: `/interests/{sessionId}`
- **Method**: `GET`
- **Description**: Retrieves a list of inferred user interests for a specific session, sorted by confidence.
- **Path Parameters**:
  - `sessionId`: Integer ID of the session.
- **Response**:
  ```json
  [
    {
      "name": "string", // Interest name
      "confidence": "float", // Confidence score (0 to 1)
      "rationale": "string" // Explanation for inferred interest
    }
  ]
  ```
- **Errors**:
  - 404: Session not found.

### 4. Pause a Session

- **Endpoint**: `/pause/{sessionId}`
- **Method**: `POST`
- **Description**: Pauses an active session, preventing further messages until resumed.
- **Path Parameters**:
  - `sessionId`: Integer ID of the session.
- **Response**:
  ```json
  {
    "status": "paused"
  }
  ```
- **Errors**:
  - 404: Session not found.

### 5. Resume a Session

- **Endpoint**: `/resume/{sessionId}`
- **Method**: `POST`
- **Description**: Resumes a previously paused session, allowing further messages.
- **Path Parameters**:
  - `sessionId`: Integer ID of the session.
- **Response**:
  ```json
  {
    "status": "resumed"
  }
  ```
- **Errors**:
  - 404: Session not found.

### 6. Retrieve Session Information

- **Endpoint**: `/session/{sessionId}`
- **Method**: `GET`
- **Description**: Retrieves metadata for a specific session, including its ID, paused status, and consent status.
- **Path Parameters**:
  - `sessionId`: Integer ID of the session.
- **Response**:
  ```json
  {
    "id": "integer", // Session ID
    "paused": "boolean", // Whether the session is paused
    "consent": "boolean" // Whether user consent was given
  }
  ```
- **Errors**:
  - 404: Session not found.

### 7. Delete a Session

- **Endpoint**: `/session/{sessionId}`
- **Method**: `DELETE`
- **Description**: Deletes a session and all associated data, including interests and chat history.
- **Path Parameters**:
  - `sessionId`: Integer ID of the session.
- **Response**:
  ```json
  {
    "status": "deleted"
  }
  ```
- **Errors**:
  - 404: Session not found.

### 8. List All Sessions

- **Endpoint**: `/sessions`
- **Method**: `GET`
- **Description**: Retrieves a list of all existing sessions.
- **Response**:
  ```json
  [
    {
      "id": "integer", // Session ID
      "prompt": "string", // Initial prompt
      "paused": "boolean", // Paused status
      "consent": "boolean" // Consent status
    }
  ]
  ```
- **Errors**: None.

### 9. Retrieve Last N Messages

- **Endpoint**: `/sessions/{sessionId}/messages`
- **Method**: `GET`
- **Description**: Retrieves the last `limit` non-empty messages from a session's chat history for display in the frontend.
- **Path Parameters**:
  - `sessionId`: Integer ID of the session.
- **Query Parameters**:
  - `limit`: Integer (default: 10) specifying the maximum number of messages to return.
- **Response**:
  ```bash
  {
    "session_id": "integer",
    "messages": [
      {
        "role": "user" | "agent",
        "content": "string"
      },
      ...
    ]
  }
  ```
- **Errors**:
  - 404: Session not found.

## Notes

- All endpoints require CORS headers, which are enabled for local frontend development (`http://localhost:5173`, `http://127.0.0.1:5173`).
- A custom header `X-Brief-Only: true` is added to every response via middleware.

## Feature Roadmap

- Not completed: Interest expansion, session influence (v2, 2 hours).
- Advanced error handling (v2, 1 hour).
- Privacy workflow (v3, optional).

## Next Steps

- Add more tests.
- Optimize prompts.
- Expand interests endpoint.
- Logging
- Privacy workflow.

## Working demo

Find a working video demo [here](https://www.loom.com/share/1e48239e2d244fecb1dbe71f3067730f?sid=a98b536c-4124-4dd2-8f22-879782a6fb02)

Happy Hacking!
