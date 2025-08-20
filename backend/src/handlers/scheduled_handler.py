import json
import os
import boto3
from datetime import datetime
from decimal import Decimal
from typing import Dict, Any, List
from services.plaid_service import PlaidService
from services.dynamodb_service import DynamoDBService

# Lazy-load services
_plaid_service = None
_dynamodb_service = None

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

def convert_for_dynamodb(obj):
    """Convert objects to DynamoDB-compatible types."""
    if isinstance(obj, dict):
        return {k: convert_for_dynamodb(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_for_dynamodb(i) for i in obj]
    elif isinstance(obj, (datetime.date, datetime.datetime)):
        return obj.isoformat()
    elif isinstance(obj, float):
        return Decimal(str(obj))  # Convert float to Decimal
    else:
        return obj

def sync_subscriptions(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Scheduled Lambda function to sync subscriptions for all users.
    This function runs daily to keep the reminders table up-to-date.
    """
    try:
        print("Starting subscription sync for all users...")
        
        plaid_service = get_plaid_service()
        dynamodb_service = get_dynamodb_service()
        
        # Get all users with Plaid items
        all_users = dynamodb_service.get_all_users_with_plaid_items()
        print(f"Found {len(all_users)} users with Plaid items")
        
        total_subscriptions_synced = 0
        total_new_subscriptions = 0
        errors = []
        
        for user_id in all_users:
            try:
                print(f"Processing user: {user_id}")
                
                # Get user's Plaid items
                plaid_items = dynamodb_service.get_plaid_items(user_id)
                if not plaid_items:
                    print(f"No Plaid items found for user {user_id}")
                    continue
                
                # Process each Plaid item (bank connection)
                for plaid_item in plaid_items:
                    try:
                        print(f"Processing Plaid item {plaid_item.item_id} for user {user_id}")
                        
                        # Get current subscriptions from Plaid
                        current_subscriptions = plaid_service.get_recurring_transactions(plaid_item.access_token)
                        
                        # Get existing reminders for this user
                        existing_reminders = dynamodb_service.get_reminders(user_id)
                        existing_stream_ids = {reminder['stream_id'] for reminder in existing_reminders}
                        
                        # Process each subscription stream
                        for stream in current_subscriptions.get('outflow_streams', []):
                            stream_id = stream['stream_id']
                            total_subscriptions_synced += 1
                            
                            # Check if this is a new subscription
                            if stream_id not in existing_stream_ids:
                                total_new_subscriptions += 1
                                print(f"New subscription found: {stream_id} for user {user_id}")
                                
                                # Create a default reminder for new subscriptions
                                default_reminder = {
                                    'user_id': user_id,
                                    'stream_id': stream_id,
                                    'reminder_days_before': 3,  # Default to 3 days
                                    'delivery_method': 'email',
                                    'created_at': datetime.utcnow().isoformat(),
                                    'updated_at': datetime.utcnow().isoformat(),
                                    'merchant_name': stream.get('merchant_name', 'Unknown'),
                                    'last_amount': convert_for_dynamodb(stream.get('last_amount', {})),
                                    'frequency': stream.get('frequency', 'monthly')
                                }
                                
                                dynamodb_service.create_reminder(default_reminder)
                                print(f"Created default reminder for stream {stream_id}")
                            
                            # Update existing reminder with latest subscription data
                            else:
                                # Update the reminder with latest subscription info
                                update_data = {
                                    'merchant_name': stream.get('merchant_name', 'Unknown'),
                                    'last_amount': convert_for_dynamodb(stream.get('last_amount', {})),
                                    'frequency': stream.get('frequency', 'monthly'),
                                    'updated_at': datetime.utcnow().isoformat()
                                }
                                dynamodb_service.update_reminder(user_id, stream_id, update_data)
                                print(f"Updated reminder for stream {stream_id}")
                        
                        # Handle inflow streams (income) if needed
                        for stream in current_subscriptions.get('inflow_streams', []):
                            # You can add logic here to handle income streams
                            # For now, we'll just log them
                            print(f"Income stream found: {stream['stream_id']} for user {user_id}")
                            
                    except Exception as e:
                        error_msg = f"Error processing Plaid item {plaid_item.item_id} for user {user_id}: {str(e)}"
                        print(error_msg)
                        errors.append(error_msg)
                
            except Exception as e:
                error_msg = f"Error processing user {user_id}: {str(e)}"
                print(error_msg)
                errors.append(error_msg)
        
        # Log summary
        summary = {
            'total_users_processed': len(all_users),
            'total_subscriptions_synced': total_subscriptions_synced,
            'total_new_subscriptions': total_new_subscriptions,
            'errors': errors,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        print("Subscription sync completed:")
        print(json.dumps(summary, indent=2))
        
        return {
            'statusCode': 200,
            'body': json.dumps(summary)
        }
        
    except Exception as e:
        error_msg = f"Fatal error in subscription sync: {str(e)}"
        print(error_msg)
        return {
            'statusCode': 500,
            'body': json.dumps({'error': error_msg})
        } 