import os
import plaid
from plaid.api import plaid_api
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.model.products import Products
from plaid.model.country_code import CountryCode
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.accounts_get_request import AccountsGetRequest

class PlaidService:
    def __init__(self):
        self.client_id = os.getenv('PLAID_CLIENT_ID')
        self.secret = os.getenv('PLAID_SECRET')
        self.env = os.getenv('PLAID_ENV', 'sandbox')
        
        # Map environment strings to Plaid Environment objects
        # Plaid only supports Sandbox and Production environments
        env_map = {
            'sandbox': plaid.Environment.Sandbox,
            'development': plaid.Environment.Sandbox,  # Development maps to Sandbox
            'production': plaid.Environment.Production
        }
        
        configuration = plaid.Configuration(
            host=env_map.get(self.env, plaid.Environment.Sandbox),
            api_key={
                'clientId': self.client_id,
                'secret': self.secret,
            }
        )
        
        api_client = plaid.ApiClient(configuration)
        self.client = plaid_api.PlaidApi(api_client)

    def create_link_token(self, user_id: str) -> dict:
        """Create a link token for Plaid Link initialization."""
        request = LinkTokenCreateRequest(
            products=[Products("transactions")],  # Remove "auth" product - not authorized in production
            client_name="Bract",
            country_codes=[CountryCode("US")],
            language="en",
            user=LinkTokenCreateRequestUser(
                client_user_id=user_id
            )
        )
        
        response = self.client.link_token_create(request)
        # Plaid returns expiration as datetime; convert to ISO 8601 string for JSON serialization
        expiration = response.expiration.isoformat() if hasattr(response.expiration, "isoformat") else str(response.expiration)
        return {
            'link_token': response.link_token,
            'expiration': expiration
        }

    def exchange_public_token(self, public_token: str) -> dict:
        """Exchange a public token for an access token."""
        request = ItemPublicTokenExchangeRequest(
            public_token=public_token
        )
        
        response = self.client.item_public_token_exchange(request)
        return {
            'access_token': response.access_token,
            'item_id': response.item_id
        }

    def get_accounts(self, access_token: str) -> list:
        """Get all accounts for a given access token."""
        request = AccountsGetRequest(access_token=access_token)
        response = self.client.accounts_get(request)
        
        accounts = []
        for account in response.accounts:
            accounts.append({
                'account_id': account.account_id,
                'name': account.name,
                'official_name': account.official_name,
                'type': account.type,
                'subtype': account.subtype,
                'mask': account.mask
            })
        
        return accounts

    def get_transactions(self, access_token: str, start_date: str, end_date: str) -> dict:
        """Get transactions for a given access token and date range."""
        # This will be implemented later when we set up transaction processing
        pass 

    def get_recurring_transactions(self, access_token: str, account_ids: list = None) -> dict:
        """Fetch recurring transactions (subscriptions) using Plaid's /transactions/recurring/get endpoint."""
        request_data = {"access_token": access_token}
        if account_ids:
            request_data["account_ids"] = account_ids
        
        response = self.client.transactions_recurring_get(request_data)
        
        # Filter out non-subscription streams (credit card payments, bank transfers, etc.)
        filtered_outflow_streams = self.filter_subscription_streams(response.outflow_streams)
        
        # Return both outflow_streams (subscriptions/bills) and inflow_streams (salary, etc)
        return {
            "outflow_streams": [stream.to_dict() for stream in filtered_outflow_streams],
            "inflow_streams": [stream.to_dict() for stream in response.inflow_streams],
        } 

    def filter_subscription_streams(self, streams: list) -> list:
        """Filter out non-subscription recurring transactions like credit card payments and bank transfers."""
        filtered_streams = []
        
        for stream in streams:
            stream_dict = stream.to_dict()
            
            # Skip credit card payments
            if (stream_dict.get('personal_finance_category', {}).get('detailed') == 'LOAN_PAYMENTS_CREDIT_CARD_PAYMENT' or
                'credit card' in stream_dict.get('description', '').lower() or
                'chase card' in stream_dict.get('description', '').lower()):
                continue
            
            # Skip bank transfers
            if (stream_dict.get('personal_finance_category', {}).get('detailed') == 'TRANSFER_OUT_ACCOUNT_TRANSFER' or
                'transfer' in stream_dict.get('description', '').lower() or
                'sav' in stream_dict.get('description', '').lower()):
                continue
            
            # Skip ATM withdrawals
            if 'atm' in stream_dict.get('description', '').lower():
                continue
            
            # Keep everything else (actual subscriptions)
            filtered_streams.append(stream)
        
        return filtered_streams 