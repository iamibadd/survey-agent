interface Props {
  onPause: () => void;
  paused: boolean;
  onReset: () => void;
  disabled?: boolean;
}

const Controls: React.FC<Props> = ({ onPause, paused, onReset, disabled }) => (
  <div
    style={{
      display: 'flex',
      justifyContent: 'center',
      gap: '1rem',
      marginTop: '1.5rem',
    }}
  >
    <button
      onClick={onPause}
      disabled={disabled}
      style={{
        background: paused ? '#4caf50' : '#f44336',
        color: '#fff',
        border: 'none',
        padding: '10px 18px',
        borderRadius: '8px',
        cursor: disabled ? 'not-allowed' : 'pointer',
        fontSize: '15px',
        fontWeight: 500,
        opacity: disabled ? 0.6 : 1,
        transition: 'all 0.2s ease-in-out',
      }}
      onMouseOver={(e) => !disabled && (e.currentTarget.style.opacity = '0.8')}
      onMouseOut={(e) => !disabled && (e.currentTarget.style.opacity = '1')}
    >
      {paused ? 'Resume' : 'Pause'}
    </button>

    <button
      onClick={onReset}
      disabled={disabled}
      style={{
        background: '#1976d2',
        color: '#fff',
        border: 'none',
        padding: '10px 18px',
        borderRadius: '8px',
        cursor: disabled ? 'not-allowed' : 'pointer',
        fontSize: '15px',
        fontWeight: 500,
        opacity: disabled ? 0.6 : 1,
        transition: 'all 0.2s ease-in-out',
      }}
      onMouseOver={(e) => !disabled && (e.currentTarget.style.opacity = '0.8')}
      onMouseOut={(e) => !disabled && (e.currentTarget.style.opacity = '1')}
    >
      Reset
    </button>
  </div>
);

export default Controls;
