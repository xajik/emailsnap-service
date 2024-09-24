from sqlite3 import IntegrityError
from app.model import AttachmentSummary, EmailLog, EmailSummary
from sqlalchemy.orm import Session
from app.app_logger import appLogger
from sqlalchemy import text

def insert_email_summary(db: Session, email_id: str, message_id: str, email_summary_data: dict):
    try:
        summary = EmailSummary(**email_summary_data)
        summary.email_id = email_id
        summary.message_id = message_id
        
        db.add(summary)
        db.commit()
        
    except IntegrityError as e:
        db.rollback()
        appLogger.debug(f"[EmailSnap]Error: {e}")
        return None

def insert_email_log(db: Session, message_id: str):
    try:
        new_log = EmailLog(message_id=message_id)
        db.add(new_log)
        db.commit()
        appLogger.debug(f"[EmailSnap]Log inserted for email_id: {message_id}")
    except Exception as e:
        db.rollback()
        appLogger.debug(f"[EmailSnap]Error inserting log: {e}")
        
        
def update_email_log_as_done(db: Session, message_id: str):
    try:
        log = (
            db.query(EmailLog)
            .filter_by(message_id=message_id)
            .order_by(EmailLog.updated_at.desc())
            .first()
        )
        if log:
            log.done = True
            db.commit()
            appLogger.debug(f"[EmailSnap]Log updated as done for message_id: {message_id}")
        else:
            appLogger.debug(f"[EmailSnap]No log found for message_id: {message_id}")
    except Exception as e:
        db.rollback()
        appLogger.debug(f"[EmailSnap]Error updating log: {e}")
        
def insert_attachment_summary(db: Session, email_id: str, file_key: str, summary: str):
    try:
        new_summary = AttachmentSummary(email_id=email_id, file_key=file_key, summary=summary)
        db.add(new_summary)
        db.commit()

        appLogger.debug(f"Summary inserted with ID: {new_summary.id}")
        return new_summary.id

    except Exception as e:
        # Rollback in case of an error
        db.rollback()
        appLogger.debug(f"Error inserting summary: {e}")