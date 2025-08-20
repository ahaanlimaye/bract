import os
from datetime import datetime
from typing import List, Dict, Any
import boto3
from boto3.dynamodb.conditions import Key
from models.plaid_model import PlaidItem, PlaidAccount

class DynamoDBService:
    def __init__(self):
        self.dynamodb = boto3.resource('dynamodb')
        self.items_table = self.dynamodb.Table(os.getenv('PLAID_ITEMS_TABLE'))
        self.accounts_table = self.dynamodb.Table(os.getenv('PLAID_ACCOUNTS_TABLE'))
        self.reminders_table = self.dynamodb.Table(os.getenv('SUBSCRIPTION_REMINDERS_TABLE'))

    def create_plaid_item(self, item: PlaidItem) -> None:
        """Store a new Plaid item in DynamoDB."""
        self.items_table.put_item(
            Item={
                'user_id': item.user_id,
                'item_id': item.item_id,
                'access_token': item.access_token,
                'institution_id': item.institution_id,
                'institution_name': item.institution_name,
                'created_at': item.created_at.isoformat(),
                'updated_at': item.updated_at.isoformat(),
                'status': item.status
            }
        )

    def get_plaid_items(self, user_id: str) -> List[PlaidItem]:
        """Retrieve all Plaid items for a user."""
        response = self.items_table.query(
            KeyConditionExpression=Key('user_id').eq(user_id)
        )
        
        items = []
        for item in response.get('Items', []):
            items.append(PlaidItem(
                user_id=item['user_id'],
                item_id=item['item_id'],
                access_token=item['access_token'],
                institution_id=item['institution_id'],
                institution_name=item['institution_name'],
                created_at=datetime.fromisoformat(item['created_at']),
                updated_at=datetime.fromisoformat(item['updated_at']),
                status=item['status']
            ))
        return items

    def create_account(self, account: PlaidAccount) -> None:
        self.accounts_table.put_item(
            Item={
                'user_id': account.user_id,
                'account_id': account.account_id,
                'item_id': account.item_id,
                'name': account.name,
                'official_name': account.official_name,
                'type': str(account.type) if account.type is not None else None,
                'subtype': str(account.subtype) if account.subtype is not None else None,
                'mask': account.mask,
                'created_at': account.created_at.isoformat(),
                'updated_at': account.updated_at.isoformat()
            }
        )

    def get_accounts(self, user_id: str) -> List[PlaidAccount]:
        """Retrieve all accounts for a user."""
        response = self.accounts_table.query(
            KeyConditionExpression=Key('user_id').eq(user_id)
        )
        
        accounts = []
        for item in response.get('Items', []):
            accounts.append(PlaidAccount(
                account_id=item['account_id'],
                user_id=item['user_id'],
                item_id=item['item_id'],
                name=item['name'],
                official_name=item.get('official_name'),
                type=item['type'],
                subtype=item.get('subtype'),
                mask=item.get('mask'),
                created_at=datetime.fromisoformat(item['created_at']),
                updated_at=datetime.fromisoformat(item['updated_at'])
            ))
        return accounts

    def create_accounts(self, user_id: str, item_id: str, accounts: List[dict]) -> None:
        """Store multiple Plaid accounts in DynamoDB."""
        print("Accounts from Plaid:", accounts)
        for account_data in accounts:
            print("Account data:", account_data)
            try:
                account = PlaidAccount(
                    account_id=account_data['account_id'],
                    user_id=user_id,
                    item_id=item_id,
                    name=account_data['name'],
                    official_name=account_data.get('official_name'),
                    type=account_data['type'],
                    subtype=account_data.get('subtype'),
                    mask=account_data.get('mask'),
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                print("PlaidAccount created:", account)
                self.create_account(account)
                print("Account stored in DynamoDB")
            except Exception as e:
                print("Error creating/storing PlaidAccount:", e)

    def get_all_users_with_plaid_items(self) -> List[str]:
        """Get all unique user IDs that have Plaid items."""
        try:
            # Scan the items table to get all users
            response = self.items_table.scan(
                ProjectionExpression='user_id',
                Select='SPECIFIC_ATTRIBUTES'
            )
            
            # Extract unique user IDs
            user_ids = set()
            for item in response.get('Items', []):
                user_ids.add(item['user_id'])
            
            # Handle pagination if needed
            while 'LastEvaluatedKey' in response:
                response = self.items_table.scan(
                    ProjectionExpression='user_id',
                    Select='SPECIFIC_ATTRIBUTES',
                    ExclusiveStartKey=response['LastEvaluatedKey']
                )
                for item in response.get('Items', []):
                    user_ids.add(item['user_id'])
            
            return list(user_ids)
        except Exception as e:
            print(f"Error getting all users with Plaid items: {e}")
            return []

    def get_reminders(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all reminders for a user."""
        try:
            response = self.reminders_table.query(
                KeyConditionExpression=Key('user_id').eq(user_id)
            )
            return response.get('Items', [])
        except Exception as e:
            print(f"Error getting reminders for user {user_id}: {e}")
            return []

    def create_reminder(self, reminder_data: Dict[str, Any]) -> None:
        """Create a new reminder."""
        try:
            self.reminders_table.put_item(Item=reminder_data)
        except Exception as e:
            print(f"Error creating reminder: {e}")
            raise

    def update_reminder(self, user_id: str, stream_id: str, update_data: Dict[str, Any]) -> None:
        """Update an existing reminder."""
        try:
            # Build update expression
            update_expression = "SET "
            expression_attribute_values = {}
            
            for key, value in update_data.items():
                update_expression += f"#{key} = :{key}, "
                expression_attribute_values[f":{key}"] = value
            
            # Remove trailing comma and space
            update_expression = update_expression.rstrip(", ")
            
            # Build expression attribute names
            expression_attribute_names = {f"#{key}": key for key in update_data.keys()}
            
            self.reminders_table.update_item(
                Key={
                    'user_id': user_id,
                    'stream_id': stream_id
                },
                UpdateExpression=update_expression,
                ExpressionAttributeNames=expression_attribute_names,
                ExpressionAttributeValues=expression_attribute_values
            )
        except Exception as e:
            print(f"Error updating reminder for user {user_id}, stream {stream_id}: {e}")
            raise

    def get_all_users_with_reminders(self) -> List[str]:
        """Get all unique user IDs that have reminders."""
        try:
            # Scan the reminders table to get all users
            response = self.reminders_table.scan(
                ProjectionExpression='user_id',
                Select='SPECIFIC_ATTRIBUTES'
            )
            
            # Extract unique user IDs
            user_ids = set()
            for item in response.get('Items', []):
                user_ids.add(item['user_id'])
            
            # Handle pagination if needed
            while 'LastEvaluatedKey' in response:
                response = self.reminders_table.scan(
                    ProjectionExpression='user_id',
                    Select='SPECIFIC_ATTRIBUTES',
                    ExclusiveStartKey=response['LastEvaluatedKey']
                )
                for item in response.get('Items', []):
                    user_ids.add(item['user_id'])
            
            return list(user_ids)
        except Exception as e:
            print(f"Error getting all users with reminders: {e}")
            return [] 