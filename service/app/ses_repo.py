import base64
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import json
from typing import List
from app.model import FullyLoadedEmailData
from app.s3_repo import load_file_from_s3
import boto3
from app.app_logger import appLogger

from app.env import AWS_ACCESS_KEY_ID, AWS_REGION, AWS_SECRET_ACCESS_KEY

if AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY:
    ses_client = boto3.client(
        "ses",
        region_name=AWS_REGION,
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY
    )
else:
    ses_client = boto3.client("ses", region_name=AWS_REGION)

def send_email_with_attachments(summary: FullyLoadedEmailData):
    json_summary = json.loads(summary.summary)
    appLogger.debug(f"[EmailSnap]Sending email ")
    
    msg = MIMEMultipart()
    msg['From'] = "review@emailsnap.app"
    msg['To'] = summary.data.sender
    msg['Subject'] = f" Re: {summary.data.subject}"
    
    original_message_id = summary.data.message_id
    
    msg.add_header('In-Reply-To', original_message_id)
    msg.add_header('References', original_message_id)

    appLogger.debug(f"[EmailSnap]Email message a: {msg.as_string()}")
    
    attachments=[x.to_review_string() for x in summary.attachments]
    
    email_body = f'''

    From: {json_summary['sender_name']} <{json_summary['sender_email']}>
    
    To: {json_summary['receiver_name']} <{json_summary['receiver_email']}>
    
    Subject: {json_summary['email_subject']}
    
    Highlights: 
    
    {json_summary['email_highlights']}
    
    Summary:
    
    {json_summary['email_summary']}
        
    '''

    body_part = MIMEText(email_body, 'plain')
    msg.attach(body_part)
    
    appLogger.debug(f"[EmailSnap]Email message b: {msg.as_string()}")
    
    file_keys=[x.new_file_key for x in summary.data.attachments]

    for file_key in file_keys:
        if file_key is None:
            continue
        appLogger.debug(f"[EmailSnap]Email message c: {msg.as_string()}")
        file_content = load_file_from_s3(file_key)
        encoded_content =  base64.b64encode(file_content).decode('utf-8')

        part = MIMEBase('application', 'octet-stream')
        part.set_payload(base64.b64decode(encoded_content))

        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename="{file_key.split("/")[-1]}"')

        msg.attach(part)
        
    appLogger.debug(f"[EmailSnap]Email message: Sender: {summary.data.sender}; Recipient: {summary.data.recipient}; Body: {email_body}; ")

    response = ses_client.send_raw_email(
        Source=summary.data.recipient,
        Destinations=[summary.data.sender],
        RawMessage={
            'Data': msg.as_string()
        }
    )
    appLogger.debug(f"[EmailSnap]Email sent! Message ID: {response['MessageId']}")