interface Props {
  onConsent: () => void;
}

const PrivacyModal: React.FC<Props> = ({ onConsent }) => (
  <div
    style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      background: 'rgba(0, 0, 0, 0.6)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 1000,
    }}
  >
    <div
      style={{
        background: '#fff',
        padding: '2rem',
        borderRadius: '12px',
        maxWidth: '420px',
        textAlign: 'center',
        boxShadow: '0 4px 12px rgba(0,0,0,0.2)',
      }}
    >
      <h2 style={{ marginBottom: '1rem', color: '#222' }}>Privacy Notice</h2>
      <p style={{ color: '#555', fontSize: '14px', lineHeight: '1.6' }}>
        We store your <strong>prompt</strong>, <strong>messages</strong>,
        <strong> interests</strong>, and <strong>consent</strong> locally for
        session continuity. You can reset anytime to delete your data. No data
        is shared externally.
      </p>
      <button
        onClick={onConsent}
        style={{
          marginTop: '1.5rem',
          background: '#1976d2',
          color: '#fff',
          border: 'none',
          padding: '10px 20px',
          borderRadius: '8px',
          cursor: 'pointer',
          fontSize: '15px',
          fontWeight: 500,
          transition: 'background 0.2s ease-in-out',
        }}
        onMouseOver={(e) => (e.currentTarget.style.background = '#1256a1')}
        onMouseOut={(e) => (e.currentTarget.style.background = '#1976d2')}
      >
        I Consent
      </button>
    </div>
  </div>
);

export default PrivacyModal;
