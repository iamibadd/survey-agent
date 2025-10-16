import { useState } from 'react';

interface Props {
  messages: { role: 'user' | 'agent'; content: string }[];
  onSend: (message: string) => void;
  paused?: boolean;
}

const ChatWindow: React.FC<Props> = ({ messages, onSend, paused }) => {
  const [input, setInput] = useState('');

  const handleSend = () => {
    if (!input || paused) return;
    onSend(input);
    setInput('');
  };

  return (
    <div className="chat-window">
      <div className="chat-messages">
        {messages.map((msg, i) => (
          <div
            key={i}
            className={`message ${msg.role === 'user' ? 'user-msg' : 'agent-msg'}`}
          >
            <strong>{msg.role === 'user' ? 'You' : 'Agent'}:</strong> {msg.content}
          </div>
        ))}
      </div>

      <div className="chat-input">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder={paused ? "Session is paused..." : "Type your message..."}
          disabled={paused}
        />
        <button onClick={handleSend} disabled={!input || paused}>
          Send
        </button>
      </div>

      {paused && (
        <div className="paused-overlay">
          <div className="paused-banner">
            ⏸️ Session Paused — You can’t send messages right now
          </div>
        </div>
      )}
    </div>
  );
};

export default ChatWindow;
