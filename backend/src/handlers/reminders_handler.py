import json
import os
import boto3
from datetime import datetime
from decimal import Decimal
from boto3.dynamodb.conditions import Key
from services.dynamodb_service import DynamoDBService

def get_cors_headers():
    return {
        'Access-Control-Allow-Origin': 'http://localhost:5173',
        'Access-Control-Allow-Credentials': 'true',
        'Access-Control-Allow-Methods': 'GET,POST,OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type,Authorization,X-Amz-Date,X-Api-Key,X-Amz-Security-Token',
    }

# Lazy-load service
_dynamodb_service = None

def get_dynamodb_service() -> DynamoDBService:
    """Lazily create and cache the DynamoDBService instance."""
    global _dynamodb_service
    if _dynamodb_service is None:
        _dynamodb_service = DynamoDBService()
    return _dynamodb_service

def convert_decimals(obj):
    """Convert Decimal objects to floats for JSON serialization."""
    if isinstance(obj, dict):
        return {k: convert_decimals(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_decimals(i) for i in obj]
    elif isinstance(obj, Decimal):
        return float(obj)
    else:
        return obj

def get_reminders(event, context):
    try:
        if event.get('httpMethod') == 'OPTIONS':
            return {'statusCode': 200, 'headers': get_cors_headers()}
        user_id = event.get('requestContext', {}).get('authorizer', {}).get('claims', {}).get('sub')
        if not user_id:
            return {'statusCode': 400, 'headers': get_cors_headers(), 'body': json.dumps({'error': 'User ID is required'})}
        
        dynamodb_service = get_dynamodb_service()
        reminders = dynamodb_service.get_reminders(user_id)
        
        # Convert Decimal values to floats for JSON serialization
        reminders = convert_decimals(reminders)
        
        return {'statusCode': 200, 'headers': get_cors_headers(), 'body': json.dumps({'reminders': reminders})}
    except Exception as e:
        return {'statusCode': 500, 'headers': get_cors_headers(), 'body': json.dumps({'error': str(e)})}

def set_reminder(event, context):
    try:
        if event.get('httpMethod') == 'OPTIONS':
            return {'statusCode': 200, 'headers': get_cors_headers()}
        user_id = event.get('requestContext', {}).get('authorizer', {}).get('claims', {}).get('sub')
        if not user_id:
            return {'statusCode': 400, 'headers': get_cors_headers(), 'body': json.dumps({'error': 'User ID is required'})}
        
        body = json.loads(event.get('body', '{}'))
        stream_id = body.get('stream_id')
        reminder_days_before = int(body.get('reminder_days_before', 3))
        delivery_method = body.get('delivery_method', 'email')
        
        if not stream_id:
            return {'statusCode': 400, 'headers': get_cors_headers(), 'body': json.dumps({'error': 'stream_id is required'})}
        
        dynamodb_service = get_dynamodb_service()
        
        # Create or update the reminder
        reminder_data = {
            'user_id': user_id,
            'stream_id': stream_id,
            'reminder_days_before': reminder_days_before,
            'delivery_method': delivery_method,
            'updated_at': datetime.utcnow().isoformat()
        }
        
        # Check if reminder already exists to preserve created_at
        existing_reminders = dynamodb_service.get_reminders(user_id)
        existing_reminder = next((r for r in existing_reminders if r['stream_id'] == stream_id), None)
        
        if existing_reminder:
            # Update existing reminder
            dynamodb_service.update_reminder(user_id, stream_id, reminder_data)
        else:
            # Create new reminder
            reminder_data['created_at'] = datetime.utcnow().isoformat()
            dynamodb_service.create_reminder(reminder_data)
        
        return {'statusCode': 200, 'headers': get_cors_headers(), 'body': json.dumps({'message': 'Reminder set'})}
    except Exception as e:
        return {'statusCode': 500, 'headers': get_cors_headers(), 'body': json.dumps({'error': str(e)})} 