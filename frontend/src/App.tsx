import { useState, useEffect, useRef } from 'react';
import ChatWindow from './components/ChatWindow';
import InterestPanel from './components/InterestPanel';
import Controls from './components/Controls';
import PrivacyModal from './components/PrivacyModal';
import axios from 'axios';
import './App.css';

interface Session {
  id: number;
  prompt: string;
  paused?: boolean;
}

function App() {
  const [sessions, setSessions] = useState<Session[]>([]);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [prompt, setPrompt] = useState('');
  const [messages, setMessages] = useState<{ role: 'user' | 'agent'; content: string }[]>([]);
  const [interests, setInterests] = useState<{ name: string; confidence: number; rationale: string }[]>([]);
  const [paused, setPaused] = useState(false);
  const [showPrivacy, setShowPrivacy] = useState(false);

  const API_ENDPOINT = "http://127.0.0.1:8000";
  const pollRef = useRef<NodeJS.Timeout | null>(null);

  // Fetch all sessions
  const fetchSessions = async () => {
    try {
      const res = await axios.get(`${API_ENDPOINT}/sessions`);
      setSessions(res.data);
    } catch (error) {
      console.error('Error fetching sessions:', error);
    }
  };

  useEffect(() => {
    fetchSessions();
    return () => stopPolling();
  }, []);

// When clicking "Start New Session" button
const handleStartClick = () => {
  if (!prompt) return;
  setShowPrivacy(true); // show modal first
};

// When user consents
const handleConsent = async () => {
  setShowPrivacy(false);
  await startSession(); // now create the session
};

// Start the session
const startSession = async () => {
  if (!prompt) return;
  try {
    const res = await axios.post(`${API_ENDPOINT}/start-session`, { prompt, consent: true });
    const newSessionId = res.data.sessionId;

    stopPolling();
    setSessionId(newSessionId.toString());
    setMessages([{ role: 'agent', content: res.data.initialMessage }]);
    setPaused(false);
    fetchSessions();
    startPolling(newSessionId);
    setPrompt('');
  } catch (error) {
    console.error('Error starting session:', error);
  }
};

  // Select an existing session
  const selectSession = async (id: string) => {
  stopPolling();
  setSessionId(id);
  setInterests([]);
  setMessages([]);

  try {
    // Fetch session info
    const sessionRes = await axios.get(`${API_ENDPOINT}/session/${id}`);
    setPaused(sessionRes.data.paused);

    // Fetch messages
    const res = await axios.get(`${API_ENDPOINT}/sessions/${id}/messages`);
    const loadedMessages = res.data.messages || [];
    setMessages(loadedMessages);

    // Start polling only if not paused
    if (!sessionRes.data.paused) {
      startPolling(id);
    }
  } catch (error) {
    console.error('Error loading chat session:', error);
  }
};

  // Send a message
  const sendMessage = async (message: string) => {
    if (!sessionId) return;

    if (paused) {
      alert('⚠️ This session is currently paused. Please resume it before sending messages.');
      return;
    }

    try {
      setMessages((prev) => [...prev, { role: 'user', content: message }]);
      const res = await axios.post(`${API_ENDPOINT}/send-message`, { sessionId, message });
      setMessages((prev) => [...prev, { role: 'agent', content: res.data.agentMessage }]);
    } catch (error) {
      console.error('Error sending message:', error);
    }
  };

  // Poll interests
  const startPolling = (id: string) => {
    stopPolling();
    pollRef.current = setInterval(async () => {
      if (paused) return;
      try {
        const res = await axios.get(`${API_ENDPOINT}/interests/${id}`);
        setInterests(res.data);
      } catch (error) {
        console.error('Error polling interests:', error);
      }
    }, 3000);
  };

  const stopPolling = () => {
    if (pollRef.current) {
      clearInterval(pollRef.current);
      pollRef.current = null;
    }
  };

  // Pause/Resume the session
  const togglePause = async () => {
    if (!sessionId) return;

    try {
      if (paused) {
        // Resume session
        await axios.post(`${API_ENDPOINT}/resume/${sessionId}`);
        setPaused(false);
        startPolling(sessionId); // restart polling
      } else {
        // Pause session
        await axios.post(`${API_ENDPOINT}/pause/${sessionId}`);
        setPaused(true);
        stopPolling(); // stop polling
      }

      fetchSessions(); // refresh sidebar sessions
    } catch (error) {
      console.error('Error toggling pause state:', error);
    }
  };

  // Reset session completely
  const resetSession = async () => {
    if (!sessionId) return;

    const confirmReset = window.confirm(
      "⚠️ Are you sure you want to reset this session?\nThis will permanently delete all messages and session data. You’ll need to start a new session afterward."
    );

    if (!confirmReset) return; // user cancelled

    try {
      await axios.delete(`${API_ENDPOINT}/session/${sessionId}`);
      stopPolling();

      setSessionId(null);
      setMessages([]);
      setInterests([]);
      setPrompt('');
      setPaused(false);

      fetchSessions();
    } catch (error) {
      console.error('Error resetting session:', error);
    }
  };

  return (
    <div className="app-container">
      {showPrivacy && (
        <PrivacyModal onConsent={handleConsent} />
      )}

      {/* Sidebar */}
      <aside className="sidebar">
        <h2>💬 Chat Sessions</h2>
        <input
          className="prompt-input"
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder="Enter system prompt..."
        />
        <button
        className="start-btn"
        onClick={handleStartClick}
        disabled={!prompt}
      >
          ➕ Start New Session
        </button>

        <div className="session-list">
          {sessions.map((s) => (
            <div
              key={s.id}
              className={`session-item ${sessionId === s.id.toString() ? 'active' : ''}`}
              onClick={() => selectSession(s.id.toString())}
            >
              <strong>Session #{s.id}</strong>
              <p className="session-prompt">{s.prompt}</p>
              {s.paused && <span className="paused-label">⏸️ Paused</span>}
            </div>
          ))}
        </div>
      </aside>

      {/* Chat Section */}
      <main className="chat-area">
        <ChatWindow messages={messages} onSend={sendMessage} paused={paused} />
        <Controls
        onPause={togglePause}
        paused={paused}
        onReset={resetSession}
/>
      </main>

      {/* Right-side Interest Panel */}
      <InterestPanel interests={interests} />
    </div>
  );
}

export default App;
