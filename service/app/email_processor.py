
from app.llm_chain import execute_llm_chain
from app.model import FullyLoadedEmailData
from app.s3_repo import fetch_email_from_s3
from app.app_logger import appLogger
import email
from email import policy
from email.utils import parsedate_to_datetime
from app.model import EmailData
from app.s3_repo import upload_file_to_s3
from app.app_logger import appLogger


def process_email(email_id) -> FullyLoadedEmailData:
    appLogger.debug(f"[EmailSnap]Processing email with email_id: {email_id}")
    email_content = fetch_email_from_s3(email_id)
    processed_email = _extract_email_info(email_id, email_content)
    appLogger.debug(f"[EmailSnap] Email from: {processed_email.sender}")
    result = execute_llm_chain(email_id=email_id, email_data=processed_email)
    return result

def _extract_email_info(email_id, msg) -> EmailData:
    sender = msg.get('From', 'Unknown Sender')
    recipient = msg.get('To', 'Unknown Recipient')
    subject = msg.get('Subject', 'No Subject')
    message_id = msg.get('Message-ID', 'Unknown Message-ID')
    reply_to = msg.get('Reply-To', 'Unknown Reply-To')
    forwarded = msg.get('X-Forwarded-For', 'Not Forwarded')
    
    date_str = msg.get('Date', None)
    try:
        date = parsedate_to_datetime(date_str).isoformat() if date_str else 'No Date'
    except Exception:
        date = 'Invalid Date'
    
    body_plain = None
    body_html = None
    attachments = []

    def _process_email_part(part):
        nonlocal body_plain, body_html, attachments

        content_type = part.get_content_type()
        disposition = str(part.get("Content-Disposition", ""))

        if content_type == "message/rfc822":
            forwarded_msg = email.message_from_bytes(part.get_payload(decode=True), policy=policy.default)
            # Recursively process forwarded message parts
            _extract_email_info(forwarded_msg)
        
        # Extract plain text body
        elif content_type == "text/plain" and "attachment" not in disposition:
            if body_plain is None:
                body_plain = part.get_payload(decode=True).decode(part.get_content_charset() or 'utf-8')
        
        elif content_type == "text/html" and "attachment" not in disposition:
            if body_html is None:
                body_html = part.get_payload(decode=True).decode(part.get_content_charset() or 'utf-8')
        
        elif part.get_filename() or "attachment" in disposition or content_type.startswith('application/'):
            file_name = part.get_filename() or "unnamed_attachment"
            attachment_data = part.get_payload(decode=True)
            
            attachment_key = upload_file_to_s3(email_id, file_name, attachment_data, content_type)
            
            attachments.append({
                'file_name': file_name,
                'content_type': content_type,
                'file_key': attachment_key,
                'content_id': part.get('Content-ID'),
            })

    if msg.is_multipart():
        for part in msg.walk():
            _process_email_part(part)
    else:
        _process_email_part(msg)

    if not body_plain:
        body_plain = "No plain text content found"

    email_data = {
        'sender': sender,
        'recipient': recipient,
        'subject': subject,
        'date': date,
        'body_plain': body_plain,
        'attachments': attachments,
        'message_id': message_id,
        'reply_to': reply_to,
        'forwarded_from': forwarded
    }
    
    appLogger.debug(f"Email data: {email_data}")

    return EmailData(**email_data)