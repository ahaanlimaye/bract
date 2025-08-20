import React, { useEffect, useState } from 'react';
import plaidService, { PlaidAccount } from '../services/plaidService';

const LinkedAccounts: React.FC = () => {
  const [accounts, setAccounts] = useState<PlaidAccount[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchAccounts = async () => {
      try {
        const fetchedAccounts = await plaidService.getAccounts();
        setAccounts(fetchedAccounts);
      } catch (err) {
        setError('Failed to fetch accounts');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchAccounts();
  }, []);

  if (loading) {
    return <div style={styles.loading}>Loading accounts...</div>;
  }

  if (error) {
    return <div style={styles.error}>{error}</div>;
  }

  if (accounts.length === 0) {
    return <div style={styles.empty}>No linked accounts found.</div>;
  }

  return (
    <div style={styles.container}>
      <div style={styles.grid}>
        {accounts.map((account) => (
          <div
            key={account.account_id}
            style={styles.accountCard}
          >
            <h3 style={styles.accountName}>{account.name}</h3>
            {account.official_name && (
              <p style={styles.officialName}>{account.official_name}</p>
            )}
            <div style={styles.accountDetails}>
              <p style={styles.detail}>Type: {account.type}</p>
              {account.subtype && <p style={styles.detail}>Subtype: {account.subtype}</p>}
              {account.mask && <p style={styles.detail}>Last 4: {account.mask}</p>}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

const styles: Record<string, React.CSSProperties> = {
  container: {
    width: '100%',
  },
  loading: {
    textAlign: 'center',
    color: '#a0a0a0',
    fontSize: '1rem',
    padding: '2rem',
  },
  error: {
    color: '#ff4444',
    fontSize: '1rem',
    textAlign: 'center',
    padding: '1rem',
  },
  empty: {
    color: '#a0a0a0',
    fontSize: '1rem',
    textAlign: 'center',
    padding: '2rem',
  },
  grid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
    gap: '1rem',
    marginTop: '1rem',
  },
  accountCard: {
    backgroundColor: '#333333',
    padding: '1.5rem',
    borderRadius: '8px',
    border: '1px solid #404040',
    transition: 'all 0.2s ease',
  },
  accountName: {
    fontSize: '1.2rem',
    fontWeight: '600',
    margin: '0 0 0.5rem 0',
    color: '#ffffff',
  },
  officialName: {
    fontSize: '0.9rem',
    color: '#a0a0a0',
    margin: '0 0 1rem 0',
  },
  accountDetails: {
    marginTop: '1rem',
  },
  detail: {
    fontSize: '0.9rem',
    color: '#a0a0a0',
    margin: '0.25rem 0',
  },
};

export default LinkedAccounts; 