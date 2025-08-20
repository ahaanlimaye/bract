import axios from 'axios';
import { fetchAuthSession } from 'aws-amplify/auth';

const API_BASE_URL = (import.meta as ImportMeta & { env: Record<string, string> }).env.VITE_API_URL || 'http://localhost:3000';

export interface Reminder {
  user_id: string;
  stream_id: string;
  reminder_days_before: number;
  delivery_method: string;
}

class ReminderService {
  private static instance: ReminderService;
  private constructor() {}

  public static getInstance(): ReminderService {
    if (!ReminderService.instance) {
      ReminderService.instance = new ReminderService();
    }
    return ReminderService.instance;
  }

  private async getAuthHeaders() {
    const session = await fetchAuthSession();
    const { accessToken, idToken } = session.tokens ?? {};
    const jwt = (accessToken ?? idToken)?.toString();
    return {
      Authorization: `Bearer ${jwt}`,
    };
  }

  async getReminders(): Promise<Reminder[]> {
    const headers = await this.getAuthHeaders();
    const response = await axios.get(`${API_BASE_URL}/reminders`, { headers });
    return response.data.reminders;
  }

  async setReminder(stream_id: string, reminder_days_before: number, delivery_method: string = 'email'): Promise<void> {
    const headers = await this.getAuthHeaders();
    await axios.post(
      `${API_BASE_URL}/reminders`,
      { stream_id, reminder_days_before, delivery_method },
      { headers }
    );
  }
}

export default ReminderService.getInstance(); 