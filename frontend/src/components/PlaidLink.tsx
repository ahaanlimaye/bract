import React, { useEffect, useState, useCallback, useRef } from 'react';
import { usePlaidLink, PlaidLinkOnSuccess } from 'react-plaid-link';
import plaidService from '../services/plaidService';

interface PlaidLinkProps {
  onSuccess?: () => void;
  onExit?: () => void;
}

const PlaidLink: React.FC<PlaidLinkProps> = ({ onSuccess, onExit }) => {
  const [linkToken, setLinkToken] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const isInitialized = useRef(false);

  const fetchLinkToken = useCallback(async () => {
    try {
      const { link_token } = await plaidService.createLinkToken();
      setLinkToken(link_token);
    } catch (err) {
      console.error('Error creating link token:', err);
      setError('Failed to initialize Plaid Link. Please try again later.');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    // Prevent multiple initializations
    if (!isInitialized.current) {
      isInitialized.current = true;
      fetchLinkToken();
    }
    
    return () => {
      // Cleanup if component unmounts
      isInitialized.current = false;
    };
  }, [fetchLinkToken]);

  const onSuccessCallback: PlaidLinkOnSuccess = async (publicToken, metadata) => {
    try {
      if (!metadata.institution) {
        throw new Error('No institution information available');
      }
      
      await plaidService.exchangePublicToken(
        publicToken,
        metadata.institution.institution_id,
        metadata.institution.name
      );
      onSuccess?.();
    } catch (err) {
      console.error('Error exchanging public token:', err);
      setError('Failed to link account. Please try again.');
    }
  };

  const { open, ready } = usePlaidLink({
    token: linkToken,
    onSuccess: onSuccessCallback,
    onExit: onExit,
    // Prevent multiple script loads
    onLoad: () => console.log('Plaid Link loaded'),
  });

  if (loading) {
    return (
      <div style={styles.loadingContainer}>
        <div style={styles.loadingText}>Loading Plaid Link...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div style={styles.errorContainer}>
        <div style={styles.errorText}>{error}</div>
        <button
          onClick={() => {
            setError(null);
            setLoading(true);
            fetchLinkToken();
          }}
          style={styles.retryButton}
        >
          Try Again
        </button>
      </div>
    );
  }

  return (
    <button
      onClick={() => open()}
      disabled={!ready}
      style={styles.button}
    >
      Link Bank Account
    </button>
  );
};

const styles: Record<string, React.CSSProperties> = {
  loadingContainer: {
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    padding: '1rem',
  },
  loadingText: {
    color: '#a0a0a0',
    fontSize: '1rem',
  },
  errorContainer: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    gap: '1rem',
    padding: '1rem',
  },
  errorText: {
    color: '#ff4444',
    fontSize: '1rem',
    textAlign: 'center',
  },
  retryButton: {
    backgroundColor: '#333333',
    color: '#ffffff',
    border: '1px solid #404040',
    padding: '8px 16px',
    borderRadius: '6px',
    fontSize: '0.9rem',
    cursor: 'pointer',
    transition: 'all 0.2s ease',
    fontWeight: '500',
  },
  button: {
    backgroundColor: '#4285F4',
    color: 'white',
    border: 'none',
    padding: '12px 24px',
    borderRadius: '6px',
    fontSize: '1rem',
    cursor: 'pointer',
    transition: 'all 0.2s ease',
    fontWeight: '500',
    boxShadow: '0 2px 4px rgba(0, 0, 0, 0.1)',
    width: 'auto',
    justifyContent: 'center',
  },
};

export default PlaidLink; 