import React, { useEffect, useState } from 'react';
import plaidService from '../services/plaidService';
import reminderService, { Reminder } from '../services/reminderService';

interface PlaidMoney {
  amount: number;
  iso_currency_code?: string;
  unofficial_currency_code?: string;
}

interface SubscriptionStream {
  stream_id: string;
  merchant_name: string;
  frequency: string;
  average_amount: number | PlaidMoney;
  last_amount: number | PlaidMoney;
  predicted_next_date: string;
  is_active: boolean;
  transaction_ids: string[];
}

function getAmountValue(val: number | PlaidMoney): number | string {
  if (typeof val === 'object' && val !== null && 'amount' in val) {
    return val.amount;
  }
  if (!isNaN(Number(val))) {
    return Number(val).toFixed(2);
  }
  return val;
}

const Subscriptions: React.FC = () => {
  const [subscriptions, setSubscriptions] = useState<SubscriptionStream[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [reminders, setReminders] = useState<Reminder[]>([]);
  const [reminderInputs, setReminderInputs] = useState<Record<string, number>>({});
  const [saving, setSaving] = useState<Record<string, boolean>>({});

  useEffect(() => {
    const fetchAll = async () => {
      try {
        const [subsData, remindersData] = await Promise.all([
          plaidService.getSubscriptions(),
          reminderService.getReminders(),
        ]);
        setSubscriptions(subsData.outflow_streams || []);
        setReminders(remindersData);
        // Initialize reminderInputs with current values
        const inputs: Record<string, number> = {};
        remindersData.forEach(r => {
          inputs[r.stream_id] = r.reminder_days_before;
        });
        setReminderInputs(inputs);
      } catch (err: any) {
        // Check if it's a 404 "No Plaid items found" error (normal state)
        if (err.response?.status === 404 && err.response?.data?.error === 'No Plaid items found for user') {
          // This is normal - user hasn't linked any bank accounts yet
          setSubscriptions([]);
          setReminders([]);
        } else {
          // This is a real error
          setError('Failed to fetch subscriptions or reminders');
          console.error(err);
        }
      } finally {
        setLoading(false);
      }
    };
    fetchAll();
  }, []);

  const handleReminderInput = (stream_id: string, value: number) => {
    setReminderInputs(inputs => ({ ...inputs, [stream_id]: value }));
  };

  const handleSaveReminder = async (stream_id: string) => {
    setSaving(s => ({ ...s, [stream_id]: true }));
    try {
      const days = reminderInputs[stream_id] ?? 3;
      await reminderService.setReminder(stream_id, days, 'email');
      // Update reminders state
      setReminders(reminders => {
        const idx = reminders.findIndex(r => r.stream_id === stream_id);
        if (idx >= 0) {
          const updated = [...reminders];
          updated[idx] = { ...updated[idx], reminder_days_before: days };
          return updated;
        } else {
          return [...reminders, { user_id: '', stream_id, reminder_days_before: days, delivery_method: 'email' }];
        }
      });
    } catch {
      alert('Failed to save reminder');
    } finally {
      setSaving(s => ({ ...s, [stream_id]: false }));
    }
  };

  if (loading) {
    return <div style={styles.loading}>Loading subscriptions...</div>;
  }
  if (error) {
    return <div style={styles.error}>{error}</div>;
  }
  if (subscriptions.length === 0) {
    return (
      <div style={styles.empty}>
        <div style={styles.emptyTitle}>No Subscriptions Yet</div>
        <div style={styles.emptyMessage}>
          Link your bank account to see your recurring subscriptions and bills.
        </div>
      </div>
    );
  }

  return (
    <div>
      <div style={styles.container}>
        <h3 style={styles.title}>Recurring Subscriptions</h3>
        <div style={styles.grid}>
          {subscriptions.map((sub) => {
            const reminder = reminders.find(r => r.stream_id === sub.stream_id);
            const inputVal = reminderInputs[sub.stream_id] ?? reminder?.reminder_days_before ?? 3;
            return (
              <div key={sub.stream_id} style={styles.card}>
                <h4 style={styles.merchant}>{sub.merchant_name || 'Unknown Merchant'}</h4>
                <div style={styles.details}>
                  <p>Amount: ${getAmountValue(sub.last_amount)}</p>
                  <p>Frequency: {sub.frequency}</p>
                  <p>Next Charge: {sub.predicted_next_date}</p>
                  <p>Status: {sub.is_active ? 'Active' : 'Inactive'}</p>
                  <div style={{ marginTop: '1rem' }}>
                    <label>
                      Reminder (days before):
                      <input
                        type="number"
                        min={1}
                        max={30}
                        value={inputVal}
                        onChange={e => handleReminderInput(sub.stream_id, Number(e.target.value))}
                        style={{ width: 60, marginLeft: 8, marginRight: 8 }}
                        disabled={saving[sub.stream_id]}
                      />
                    </label>
                    <button
                      onClick={() => handleSaveReminder(sub.stream_id)}
                      disabled={saving[sub.stream_id]}
                      style={{ marginLeft: 8 }}
                    >
                      {saving[sub.stream_id] ? 'Saving...' : 'Save'}
                    </button>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

const styles: Record<string, React.CSSProperties> = {
  container: {
    width: '100%',
  },
  title: {
    fontSize: '1.2rem',
    fontWeight: 600,
    color: '#fff',
    marginBottom: '1rem',
  },
  loading: {
    color: '#a0a0a0',
    fontSize: '1rem',
    textAlign: 'center',
    padding: '1rem',
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
    backgroundColor: '#1a1a1a',
    borderRadius: '8px',
    border: '1px solid #333333',
  },
  emptyTitle: {
    fontSize: '1.1rem',
    fontWeight: '500',
    color: '#ffffff',
    marginBottom: '0.5rem',
  },
  emptyMessage: {
    fontSize: '0.9rem',
    color: '#808080',
    lineHeight: '1.4',
  },
  grid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
    gap: '1rem',
  },
  card: {
    backgroundColor: '#333333',
    padding: '1.2rem',
    borderRadius: '8px',
    border: '1px solid #404040',
  },
  merchant: {
    fontSize: '1.1rem',
    fontWeight: 500,
    color: '#fff',
    margin: '0 0 0.5rem 0',
  },
  details: {
    fontSize: '0.95rem',
    color: '#a0a0a0',
    marginTop: '0.5rem',
  },
};

export default Subscriptions; 