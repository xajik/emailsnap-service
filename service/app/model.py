from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, func
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from pydantic import BaseModel
from typing import List, Optional

Base = declarative_base()

class EmailLog(Base):
    __tablename__ = 'email_log'

    id = Column(Integer, primary_key=True, autoincrement=True)
    message_id = Column(String(512), nullable=False, index=True)
    done = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(DateTime, default=datetime.now, onupdate=func.now(), nullable=False)

class EmailSummary(Base):
    __tablename__ = 'email_summary'

    id = Column(Integer, primary_key=True, autoincrement=True)
    email_id = Column(String(512), nullable=False, unique=True, index=True)
    message_id = Column(String(512), nullable=False)
    sender_email = Column(String(512), nullable=False)
    sender_name = Column(String(512), nullable=True)
    receiver_email = Column(String(512), nullable=False)
    receiver_name = Column(String(512), nullable=True)
    email_subject = Column(String(512), nullable=True)
    email_highlights = Column(Text, nullable=False)
    email_summary = Column(Text, nullable=False)
    email_priority = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(DateTime, default=datetime.now, onupdate=func.now(), nullable=False)
    
class AttachmentSummary(Base):
    __tablename__ = 'attachment_summary'

    id = Column(Integer, primary_key=True, autoincrement=True)
    email_id = Column(String(512), nullable=False, index=True)
    file_key = Column(String(512), nullable=False, index=True, unique=True)
    summary = Column(Text, nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class EmailAttachment(BaseModel):
    file_name: str
    content_type: str
    file_key: str
    content_id: str
    # Added manually
    new_file_key: Optional[str] = None

class EmailData(BaseModel):
    subject: str
    sender: str
    recipient: str
    date: str
    body_plain: str
    message_id: str
    reply_to: str
    forwarded_from: str
    attachments: Optional[List[EmailAttachment]] = []
    
class AttachedInfo(BaseModel):
    suggested_file_name: str
    addressed_to_email: str
    addressed_to_name: str
    summary: str
    urgent: List[str]
    # Added manually
    original_file_name: Optional[str] = None 
    email_id: Optional[str] = None 
    
    def to_review_string(self) -> str:
        urgent_bullet_list = '\n \t'.join([f"• {item}" for item in self.urgent])
        review = f'''
            File name: {self.suggested_file_name}
            
            Addressed To: {self.addressed_to_name} <{self.addressed_to_email}>
            
            Highlights:
            
        {urgent_bullet_list}
            
            Summary:
            
            {self.summary}
            
        '''
        
        return review

class FullyLoadedEmailData(BaseModel):
    summary: str
    data: EmailData
    attachments: List[AttachedInfo]