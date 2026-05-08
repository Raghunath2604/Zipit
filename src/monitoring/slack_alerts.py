import json
import boto3
import urllib3
import os

def lambda_handler(event, context):
    """Lambda function to send Slack alerts"""
    
    # Parse CloudWatch alarm
    message = json.loads(event['Records'][0]['Sns']['Message'])
    alarm_name = message['AlarmName']
    new_state = message['NewStateValue']
    reason = message['NewStateReason']
    
    # Slack webhook URL (store in environment variable)
    slack_webhook = os.environ.get('SLACK_WEBHOOK_URL')
    
    if not slack_webhook:
        print("SLACK_WEBHOOK_URL not configured")
        return {'statusCode': 400, 'body': 'Webhook not configured'}
    
    # Create Slack message
    slack_message = {
        "text": f"🚨 MLOps Alert: {alarm_name}",
        "attachments": [
            {
                "color": "danger" if new_state == "ALARM" else "good",
                "fields": [
                    {
                        "title": "Status",
                        "value": new_state,
                        "short": True
                    },
                    {
                        "title": "Reason",
                        "value": reason,
                        "short": False
                    }
                ]
            }
        ]
    }
    
    # Send to Slack
    http = urllib3.PoolManager()
    response = http.request(
        'POST',
        slack_webhook,
        body=json.dumps(slack_message),
        headers={'Content-Type': 'application/json'}
    )
    
    return {
        'statusCode': 200,
        'body': json.dumps('Alert sent to Slack')
    }