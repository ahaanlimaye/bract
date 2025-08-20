import axios from 'axios';
import { fetchAuthSession } from 'aws-amplify/auth';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:3000';

export interface PlaidAccount {
  account_id: string;
  name: string;
  official_name?: string;
  type: string;
  subtype?: string;
  mask?: string;
}

class PlaidService {
  private static instance: PlaidService;
  private constructor() {}

  public static getInstance(): PlaidService {
    if (!PlaidService.instance) {
      PlaidService.instance = new PlaidService();
    }
    return PlaidService.instance;
  }

  private async getAuthHeaders() {
    const session = await fetchAuthSession();
    const { accessToken, idToken } = session.tokens ?? {};
    const jwt = (accessToken ?? idToken)?.toString();
    return {
      Authorization: `Bearer ${jwt}`,
    };
  }

  async createLinkToken(): Promise<{ link_token: string; expiration: string }> {
    const headers = await this.getAuthHeaders();
    const response = await axios.post(
      `${API_BASE_URL}/plaid/link-token`,
      {},
      { headers }
    );
    return response.data;
  }

  async exchangePublicToken(publicToken: string, institutionId: string, institutionName: string): Promise<{ item_id: string }> {
    const headers = await this.getAuthHeaders();
    const response = await axios.post(
      `${API_BASE_URL}/plaid/exchange-token`,
      {
        public_token: publicToken,
        institution_id: institutionId,
        institution_name: institutionName,
      },
      { headers }
    );
    return response.data;
  }

  async getAccounts(): Promise<PlaidAccount[]> {
    const headers = await this.getAuthHeaders();
    const response = await axios.get(`${API_BASE_URL}/plaid/accounts`, { headers });
    return response.data.accounts;
  }

  async getSubscriptions(): Promise<any> {
    const headers = await this.getAuthHeaders();
    const response = await axios.get(
      `${API_BASE_URL}/subscriptions`,
      { headers }
    );
    return response.data;
  }
}

export default PlaidService.getInstance(); 