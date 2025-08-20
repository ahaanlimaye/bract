import React, { useState } from 'react';
import PlaidLink from './PlaidLink';
import LinkedAccounts from './LinkedAccounts';
import Subscriptions from './Subscriptions';

interface DashboardContentProps {
  username: string;
}

const DashboardContent: React.FC<DashboardContentProps> = ({ username }) => {
  const [refreshAccounts, setRefreshAccounts] = useState(false);

  const handleLinkSuccess = () => {
    setRefreshAccounts(prev => !prev); // Toggle to trigger re-fetch
  };

  return (
    <div style={styles.content}>
      <p style={styles.welcomeText}>Welcome, {username}</p>
      <div style={styles.plaidSection}>
        <div style={styles.plaidHeader}>
          <h2 style={styles.sectionTitle}>Bank Accounts</h2>
          <PlaidLink onSuccess={handleLinkSuccess} />
        </div>
        <div style={styles.accountsContainer}>
          <LinkedAccounts key={refreshAccounts.toString()} />
        </div>
        <div style={styles.subscriptionsSection}>
          <Subscriptions />
        </div>
      </div>
    </div>
  );
};

const styles: Record<string, React.CSSProperties> = {
  content: {
    backgroundColor: '#242424',
    borderRadius: '8px',
    padding: '2rem',
    minHeight: '400px',
    width: '100%',
  },
  welcomeText: {
    fontSize: '1.2rem',
    color: '#a0a0a0',
    marginBottom: '2rem',
  },
  plaidSection: {
    display: 'flex',
    flexDirection: 'column',
    gap: '1.5rem',
  },
  plaidHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  sectionTitle: {
    fontSize: '1.5rem',
    fontWeight: '600',
    color: '#ffffff',
    margin: '0',
  },
  accountsContainer: {
    backgroundColor: '#1a1a1a',
    borderRadius: '8px',
    padding: '1.5rem',
  },
  subscriptionsSection: {
    marginTop: '2rem',
    backgroundColor: '#232323',
    borderRadius: '8px',
    padding: '1.5rem',
  },
};

export default DashboardContent; 