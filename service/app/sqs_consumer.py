import json
from app.app_logger import appLogger
from app.db import get_db_session
from app.db_repo import insert_email_log, insert_email_summary, update_email_log_as_done
from app.env import AWS_ACCESS_KEY_ID, AWS_REGION, AWS_SECRET_ACCESS_KEY, SNS_QUEUE_URL
from app.ses_repo import send_email_with_attachments
import boto3
from app.email_processor import process_email

def receive_messages(sqs_client):
    appLogger.debug("[EmailSnap]Polling messages from SQS")
    response = sqs_client.receive_message(
        QueueUrl=SNS_QUEUE_URL,
        MessageAttributeNames=['All'],
        MaxNumberOfMessages=5,
        WaitTimeSeconds=20
    )
    return response

def delete_message(sqs_client, receipt_handle):
    sqs_client.delete_message(
        QueueUrl=SNS_QUEUE_URL,
        ReceiptHandle=receipt_handle
    )

def process_sqs_messages():
    if AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY:
        sqs_client = boto3.client("sqs", region_name=AWS_REGION, aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
    else:
        sqs_client = boto3.client("sqs", region_name=AWS_REGION)
    
    appLogger.debug("[EmailSnap]Starting the SQS consumer loop")
    while True:
        
        appLogger.debug("[EmailSnap]Processing a new SQS message")
        
        response = receive_messages(sqs_client)
        messages = response.get('Messages', [])
        print (f"Received {len(messages)} messages")
        for message in messages:
            message_id = message.get('MessageId')
            receipt_handle = message.get('ReceiptHandle')
            with get_db_session() as db:
                    insert_email_log(db, message_id)
            try: 
                email_id = get_email_id_from_sns_message(message)
                if email_id is None:
                    continue
                
                print (f"Email id: {email_id}")
                
                summary = process_email(email_id)
                json_summary = json.loads(summary.summary)
                with get_db_session() as db:
                    appLogger.debug(f"[EmailSnap]Inserting email summary to db: {json_summary}")
                    insert_email_summary(db, email_id, message_id, json_summary)
                        
                appLogger.debug(f"[EmailSnap]Deleting message with id: {email_id}")
                delete_message(sqs_client, receipt_handle)
                
                with get_db_session() as db:
                    update_email_log_as_done(db, message_id)
                    
                send_email_with_attachments(summary)
                
            except Exception as e:
                appLogger.debug(f"Error processing message: {e}")
                delete_message(sqs_client, receipt_handle)
                continue
                
        print (f"Processed {len(messages)} messages")

def get_email_id_from_sns_message(message):
    email_id = None
    try:
        body_string = message.get('Body')
        if body_string is None:
            return None
        body_json = json.loads(body_string)
        message_string = body_json.get('Message')
        if message_string is None:
            return None
        message_json = json.loads(message_string)
        if message_json is None:
            return None
        email_id = message_json.get('mail').get('messageId')
    except Exception as e:
        appLogger.debug(f"Error extracting email ID from SNS message: {e}")
    return email_id