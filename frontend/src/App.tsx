import React, { useEffect, useState } from 'react';
import { Amplify } from 'aws-amplify';
import { signInWithRedirect, signOut, getCurrentUser } from 'aws-amplify/auth';
import awsConfig from './aws-exports';
import DashboardContent from './components/DashboardContent';

Amplify.configure(awsConfig);

interface User {
  username: string;
  attributes?: {
    email?: string;
    name?: string;
  };
}

const App: React.FC = () => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const checkAuth = async () => {
      try {
        const currentUser = await getCurrentUser();
        setUser(currentUser);
      } catch (error) {
        console.error('Error getting current user:', error);
        setUser(null);
      } finally {
        setLoading(false);
      }
    };

    // Check auth state on mount and after a short delay to handle redirect
    checkAuth();
    const timer = setTimeout(checkAuth, 1000);
    return () => clearTimeout(timer);
  }, []);

  const handleGoogleSignIn = async () => {
    try {
      setLoading(true);
      await signInWithRedirect({ provider: 'Google' });
    } catch (error) {
      console.error('Error signing in with Google:', error);
      setError('Failed to sign in with Google');
      setLoading(false);
    }
  };

  const handleSignOut = async () => {
    try {
      await signOut();
      setUser(null);
    } catch (error) {
      console.error('Error signing out:', error);
      setError('Failed to sign out');
    }
  };

  if (loading) {
    return (
      <div style={styles.container}>
        <div style={styles.loading}>Loading...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div style={styles.container}>
        <div style={styles.errorContainer}>
          <h2 style={styles.errorTitle}>Error</h2>
          <p style={styles.errorMessage}>{error}</p>
          <button 
            onClick={() => setError(null)} 
            style={styles.errorButton}
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  return (
    <div style={styles.container}>
      {!user ? (
        <div style={styles.authContainer}>
          <h1 style={styles.title}>Welcome to Bract</h1>
          <button onClick={handleGoogleSignIn} style={styles.googleButton}>
            Sign in with Google
          </button>
        </div>
      ) : (
        <div style={styles.dashboardContainer}>
          <div style={styles.header}>
            <h1 style={styles.title}>Dashboard</h1>
            <button onClick={handleSignOut} style={styles.signOutButton}>
              Sign Out
            </button>
          </div>
          <DashboardContent username={user.username} />
        </div>
      )}
    </div>
  );
};

const styles: Record<string, React.CSSProperties> = {
  container: {
    minHeight: '100vh',
    width: '100vw',
    backgroundColor: '#1a1a1a',
    color: '#ffffff',
    fontFamily: 'system-ui, -apple-system, sans-serif',
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
  },
  loading: {
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    fontSize: '1.2rem',
    color: '#a0a0a0',
  },
  errorContainer: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    gap: '1rem',
    padding: '2rem',
    backgroundColor: '#242424',
    borderRadius: '12px',
    boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
  },
  errorTitle: {
    fontSize: '1.5rem',
    color: '#ff4444',
    margin: 0,
  },
  errorMessage: {
    fontSize: '1rem',
    color: '#a0a0a0',
    textAlign: 'center',
  },
  errorButton: {
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
  authContainer: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    gap: '2rem',
    padding: '4rem',
    backgroundColor: '#242424',
    borderRadius: '12px',
    boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
    width: 'auto',
    margin: '2rem',
  },
  dashboardContainer: {
    padding: '2rem',
    width: '100%',
    maxWidth: '1400px',
    margin: '0 auto',
  },
  header: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '2rem',
    backgroundColor: '#242424',
    padding: '1.5rem',
    borderRadius: '8px',
    width: '100%',
  },
  title: {
    fontSize: 'clamp(2rem, 4vw, 2.5rem)',
    fontWeight: '600',
    margin: '0',
    color: '#ffffff',
  },
  googleButton: {
    backgroundColor: '#4285F4',
    color: 'white',
    border: 'none',
    padding: '14px 32px',
    borderRadius: '6px',
    fontSize: '1.1rem',
    cursor: 'pointer',
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
    transition: 'all 0.2s ease',
    fontWeight: '500',
    boxShadow: '0 2px 4px rgba(0, 0, 0, 0.1)',
    width: 'auto',
    justifyContent: 'center',
  },
  signOutButton: {
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
};

export default App;
