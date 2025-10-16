import React from 'react';

interface Props {
  interests: { name: string; confidence: number; rationale: string }[];
}

const InterestPanel: React.FC<Props> = ({ interests }) => (
  <div
    style={{
      width: '300px',
      backgroundColor: '#f9fafb',
      borderLeft: '1px solid #e5e7eb',
      padding: '1.5rem',
      display: 'flex',
      flexDirection: 'column',
      gap: '1rem',
      boxShadow: 'inset 0 0 6px rgba(0,0,0,0.05)',
      overflowY: 'auto',
      height: '80vh',
      borderRadius: '0 12px 12px 0',
    }}
  >
    <h3 style={{ marginBottom: '0.5rem', color: '#111827', fontSize: '1.2rem', fontWeight: 600 }}>
      🧠 Ranked Interests
    </h3>

    {interests.length === 0 ? (
      <p style={{ color: '#6b7280', fontStyle: 'italic', fontSize: '0.9rem' }}>
        No interests detected yet...
      </p>
    ) : (
      <ul
        style={{
          listStyle: 'none',
          padding: 0,
          margin: 0,
          display: 'flex',
          flexDirection: 'column',
          gap: '1rem',
        }}
      >
        {interests.map((int, i) => (
          <li
            key={i}
            style={{
              backgroundColor: '#ffffff',
              borderRadius: '12px',
              padding: '1rem',
              boxShadow: '0 2px 6px rgba(0,0,0,0.05)',
              border: '1px solid #e5e7eb',
            }}
          >
            <div
              style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                marginBottom: '0.5rem',
              }}
            >
              <strong style={{ color: '#111827', fontSize: '1rem' }}>{int.name}</strong>
              <span style={{ color: '#4f46e5', fontWeight: 600 }}>
                {(int.confidence * 100).toFixed(0)}%
              </span>
            </div>

            {/* Confidence Bar */}
            <div
              style={{
                height: '6px',
                borderRadius: '4px',
                backgroundColor: '#e5e7eb',
                marginBottom: '0.6rem',
                overflow: 'hidden',
              }}
            >
              <div
                style={{
                  width: `${int.confidence * 100}%`,
                  height: '100%',
                  backgroundColor: '#4f46e5',
                  transition: 'width 0.4s ease',
                }}
              ></div>
            </div>

            <p
              style={{
                color: '#374151',
                fontSize: '0.9rem',
                lineHeight: 1.4,
                margin: 0,
              }}
            >
              {int.rationale}
            </p>
          </li>
        ))}
      </ul>
    )}
  </div>
);

export default InterestPanel;
