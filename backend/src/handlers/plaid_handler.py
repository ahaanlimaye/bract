import json
import datetime
from typing import Any, Dict
from services.plaid_service import PlaidService
from services.dynamodb_service import DynamoDBService
from models.plaid_model import PlaidItem, PlaidAccount

# Lazy-load services so that simple OPTIONS calls don't fail during cold-start
_plaid_service = None  # type: PlaidService | None
_dynamodb_service = None  # type: DynamoDBService | None

def get_plaid_service() -> PlaidService:
    """Lazily create and cache the PlaidService instance."""
    global _plaid_service
    if _plaid_service is None:
        _plaid_service = PlaidService()
    return _plaid_service

def get_dynamodb_service() -> DynamoDBService:
    """Lazily create and cache the DynamoDBService instance."""
    global _dynamodb_service
    if _dynamodb_service is None:
        _dynamodb_service = DynamoDBService()
    return _dynamodb_service

def get_cors_headers() -> Dict[str, Any]:
    """Returns CORS headers for API responses."""
    return {
        'Access-Control-Allow-Origin': 'http://localhost:5173',
        'Access-Control-Allow-Credentials': 'true',
        'Access-Control-Allow-Methods': 'GET,POST,OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type,Authorization,X-Amz-Date,X-Api-Key,X-Amz-Security-Token',
    }

def create_link_token(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Lambda handler for creating a Plaid link token."""
    try:
        # Handle preflight request
        if event.get('httpMethod') == 'OPTIONS':
            return {
                'statusCode': 200,
                'headers': get_cors_headers()
            }

        # Get user_id from the event (this will come from Cognito in production)
        user_id = event.get('requestContext', {}).get('authorizer', {}).get('claims', {}).get('sub')
        if not user_id:
            return {
                'statusCode': 400,
                'headers': get_cors_headers(),
                'body': json.dumps({'error': 'User ID is required'})
            }

        # Create link token
        response = get_plaid_service().create_link_token(user_id)
        
        return {
            'statusCode': 200,
            'headers': get_cors_headers(),
            'body': json.dumps(response)
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': get_cors_headers(),
            'body': json.dumps({'error': str(e)})
        }

def exchange_token(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Lambda handler for exchanging a public token for an access token."""
    try:
        # Handle preflight request
        if event.get('httpMethod') == 'OPTIONS':
            return {
                'statusCode': 200,
                'headers': get_cors_headers()
            }

        # Get user_id from the event
        user_id = event.get('requestContext', {}).get('authorizer', {}).get('claims', {}).get('sub')
        if not user_id:
            return {
                'statusCode': 400,
                'headers': get_cors_headers(),
                'body': json.dumps({'error': 'User ID is required'})
            }

        # Parse request body
        body = json.loads(event.get('body', '{}'))
        public_token = body.get('public_token')
        institution_id = body.get('institution_id')
        institution_name = body.get('institution_name')
        
        if not all([public_token, institution_id, institution_name]):
            return {
                'statusCode': 400,
                'headers': get_cors_headers(),
                'body': json.dumps({'error': 'Missing required fields'})
            }

        # Exchange token
        response = get_plaid_service().exchange_public_token(public_token)
        
        # Create and store PlaidItem
        plaid_item = PlaidItem(
            user_id=user_id,
            item_id=response['item_id'],
            access_token=response['access_token'],
            institution_id=institution_id,
            institution_name=institution_name,
            created_at=datetime.datetime.utcnow(),
            updated_at=datetime.datetime.utcnow()
        )
        get_dynamodb_service().create_plaid_item(plaid_item)

        # Get accounts from Plaid and store them
        print("Getting accounts from Plaid")
        accounts = get_plaid_service().get_accounts(response['access_token'])
        for account_data in accounts:
            print("Account")
            print(account_data)
            account = PlaidAccount(
                account_id=account_data['account_id'],
                user_id=user_id,
                item_id=response['item_id'],
                name=account_data['name'],
                official_name=account_data.get('official_name'),
                type=account_data['type'],
                subtype=account_data.get('subtype'),
                mask=account_data.get('mask'),
                created_at=datetime.datetime.utcnow(),
                updated_at=datetime.datetime.utcnow()
            )
            print(account)
            get_dynamodb_service().create_account(account)
            print("Stored account")

        return {
            'statusCode': 200,
            'headers': get_cors_headers(),
            'body': json.dumps({
                'message': 'Successfully linked account',
                'item_id': response['item_id']
            })
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': get_cors_headers(),
            'body': json.dumps({'error': str(e)})
        }

def get_accounts(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Lambda handler for retrieving a user's linked accounts."""
    try:
        # Handle preflight request
        if event.get('httpMethod') == 'OPTIONS':
            return {
                'statusCode': 200,
                'headers': get_cors_headers()
            }

        # Get user_id from the event
        user_id = event.get('requestContext', {}).get('authorizer', {}).get('claims', {}).get('sub')
        if not user_id:
            return {
                'statusCode': 400,
                'headers': get_cors_headers(),
                'body': json.dumps({'error': 'User ID is required'})
            }

        # Get accounts from DynamoDB
        accounts = get_dynamodb_service().get_accounts(user_id)
        
        # Format accounts for response
        accounts_data = [{
            'account_id': account.account_id,
            'name': account.name,
            'official_name': account.official_name,
            'type': account.type,
            'subtype': account.subtype,
            'mask': account.mask
        } for account in accounts]
        
        return {
            'statusCode': 200,
            'headers': get_cors_headers(),
            'body': json.dumps({
                'accounts': accounts_data
            })
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': get_cors_headers(),
            'body': json.dumps({'error': str(e)})
        }

def convert_dates(obj):
    if isinstance(obj, dict):
        return {k: convert_dates(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_dates(i) for i in obj]
    elif isinstance(obj, (datetime.date, datetime.datetime)):
        return obj.isoformat()
    else:
        return obj

def get_subscriptions(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Lambda handler for fetching recurring subscriptions for the user."""
    try:
        # Handle preflight request
        if event.get('httpMethod') == 'OPTIONS':
            return {
                'statusCode': 200,
                'headers': get_cors_headers()
            }

        # Get user_id from the event
        user_id = event.get('requestContext', {}).get('authorizer', {}).get('claims', {}).get('sub')
        if not user_id:
            return {
                'statusCode': 400,
                'headers': get_cors_headers(),
                'body': json.dumps({'error': 'User ID is required'})
            }

        # Get the user's Plaid items (bank connections)
        plaid_items = get_dynamodb_service().get_plaid_items(user_id)
        if not plaid_items:
            return {
                'statusCode': 404,
                'headers': get_cors_headers(),
                'body': json.dumps({'error': 'No Plaid items found for user'})
            }

        # For now, just use the first Plaid item (could be extended to all)
        access_token = plaid_items[0].access_token

        # Fetch recurring transactions (subscriptions) from Plaid
        subscriptions = get_plaid_service().get_recurring_transactions(access_token)
        subscriptions = convert_dates(subscriptions)

        return {
            'statusCode': 200,
            'headers': get_cors_headers(),
            'body': json.dumps(subscriptions)
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': get_cors_headers(),
            'body': json.dumps({'error': str(e)})
        } 