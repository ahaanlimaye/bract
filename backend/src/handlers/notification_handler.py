import json
import os
import boto3
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, Any, List
from services.dynamodb_service import DynamoDBService

# Lazy-load service
_dynamodb_service = None

def get_dynamodb_service() -> DynamoDBService:
    """Lazily create and cache the DynamoDBService instance."""
    global _dynamodb_service
    if _dynamodb_service is None:
        _dynamodb_service = DynamoDBService()
    return _dynamodb_service

def convert_decimals(obj):
    """Convert Decimal objects to floats for processing."""
    if isinstance(obj, dict):
        return {k: convert_decimals(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_decimals(i) for i in obj]
    elif isinstance(obj, Decimal):
        return float(obj)
    else:
        return obj

def send_reminders(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Scheduled Lambda function to send email reminders for upcoming subscriptions.
    This function runs daily to check for subscriptions due within the reminder period.
    """
    try:
        print("Starting subscription reminder check...")
        
        dynamodb_service = get_dynamodb_service()
        ses = boto3.client('ses', region_name='us-east-1')
        from_email = os.environ.get('FROM_EMAIL', 'notifications@yourdomain.com')
        
        # Get all users with reminders
        all_users = dynamodb_service.get_all_users_with_reminders()
        print(f"Found {len(all_users)} users with reminders")
        
        total_emails_sent = 0
        errors = []
        
        for user_id in all_users:
            try:
                print(f"Processing reminders for user: {user_id}")
                
                # Get user's reminders
                reminders = dynamodb_service.get_reminders(user_id)
                reminders = convert_decimals(reminders)
                
                # Get user's email from Cognito (you'll need to implement this)
                user_email = get_user_email(user_id)
                if not user_email:
                    print(f"No email found for user {user_id}")
                    continue
                
                # Check which reminders should be sent today
                today = datetime.utcnow().date()
                reminders_to_send = []
                
                for reminder in reminders:
                    try:
                        # Calculate when this subscription is due
                        # For now, we'll use a simple approach based on frequency
                        # In a real implementation, you'd want to track actual due dates
                        frequency = reminder.get('frequency', 'monthly')
                        last_amount = reminder.get('last_amount', {})
                        
                        # Simple logic: if it's been about a month since last payment, send reminder
                        # This is a simplified approach - you'd want more sophisticated logic
                        reminder_days = reminder.get('reminder_days_before', 3)
                        
                        # For demo purposes, let's send reminders for all subscriptions
                        # In production, you'd check actual due dates
                        reminders_to_send.append({
                            'merchant_name': reminder.get('merchant_name', 'Unknown'),
                            'amount': last_amount.get('amount', 0),
                            'currency': last_amount.get('currency', 'USD'),
                            'reminder_days': reminder_days
                        })
                        
                    except Exception as e:
                        error_msg = f"Error processing reminder {reminder.get('stream_id')} for user {user_id}: {str(e)}"
                        print(error_msg)
                        errors.append(error_msg)
                
                # Send email if there are reminders
                if reminders_to_send:
                    try:
                        email_content = create_reminder_email(reminders_to_send)
                        
                        response = ses.send_email(
                            Source=from_email,
                            Destination={
                                'ToAddresses': [user_email]
                            },
                            Message={
                                'Subject': {
                                    'Data': f'Subscription Reminders - {len(reminders_to_send)} upcoming payments',
                                    'Charset': 'UTF-8'
                                },
                                'Body': {
                                    'Html': {
                                        'Data': email_content,
                                        'Charset': 'UTF-8'
                                    }
                                }
                            }
                        )
                        
                        total_emails_sent += 1
                        print(f"Sent reminder email to {user_email} for {len(reminders_to_send)} subscriptions")
                        
                    except Exception as e:
                        error_msg = f"Error sending email to user {user_id}: {str(e)}"
                        print(error_msg)
                        errors.append(error_msg)
                
            except Exception as e:
                error_msg = f"Error processing user {user_id}: {str(e)}"
                print(error_msg)
                errors.append(error_msg)
        
        # Log summary
        summary = {
            'total_users_processed': len(all_users),
            'total_emails_sent': total_emails_sent,
            'errors': errors,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        print("Reminder check completed:")
        print(json.dumps(summary, indent=2))
        
        return {
            'statusCode': 200,
            'body': json.dumps(summary)
        }
        
    except Exception as e:
        error_msg = f"Fatal error in reminder check: {str(e)}"
        print(error_msg)
        return {
            'statusCode': 500,
            'body': json.dumps({'error': error_msg})
        }

def get_user_email(user_id: str) -> str:
    """
    Get user's email from Cognito.
    For now, we'll return a placeholder. In production, you'd query Cognito.
    """
    # TODO: Implement actual Cognito user lookup
    # For now, return a placeholder email for testing
    return f"user-{user_id}@example.com"

def create_reminder_email(reminders: List[Dict[str, Any]]) -> str:
    """Create HTML email content for subscription reminders."""
    
    reminders_html = ""
    for reminder in reminders:
        amount = reminder.get('amount', 0)
        currency = reminder.get('currency', 'USD')
        merchant = reminder.get('merchant_name', 'Unknown')
        
        reminders_html += f"""
        <tr style="border-bottom: 1px solid #eee;">
            <td style="padding: 12px 0;">{merchant}</td>
            <td style="padding: 12px 0; text-align: right;">{currency} {amount:.2f}</td>
        </tr>
        """
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Subscription Reminders</title>
    </head>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px;">
            <h1 style="color: #2c3e50; margin-bottom: 20px;">📅 Subscription Reminders</h1>
            
            <p style="margin-bottom: 20px;">
                You have <strong>{len(reminders)} subscription(s)</strong> coming up for renewal soon.
            </p>
            
            <div style="background-color: white; border-radius: 8px; padding: 20px; margin-bottom: 20px;">
                <h2 style="color: #2c3e50; margin-bottom: 15px;">Upcoming Payments</h2>
                
                <table style="width: 100%; border-collapse: collapse;">
                    <thead>
                        <tr style="border-bottom: 2px solid #3498db;">
                            <th style="text-align: left; padding: 12px 0; color: #2c3e50;">Service</th>
                            <th style="text-align: right; padding: 12px 0; color: #2c3e50;">Amount</th>
                        </tr>
                    </thead>
                    <tbody>
                        {reminders_html}
                    </tbody>
                </table>
            </div>
            
            <div style="background-color: #e8f4fd; border-left: 4px solid #3498db; padding: 15px; margin-bottom: 20px;">
                <p style="margin: 0; color: #2c3e50;">
                    <strong>💡 Tip:</strong> Review these subscriptions and consider cancelling any you no longer use to save money!
                </p>
            </div>
            
            <p style="color: #7f8c8d; font-size: 14px; margin-top: 30px;">
                This is an automated reminder from your Bract subscription management platform.
            </p>
        </div>
    </body>
    </html>
    """
    
    return html_content 