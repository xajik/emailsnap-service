import base64
from io import BytesIO
import json
import time
from typing import List, Optional
from app.db import get_db_session
from app.db_repo import insert_attachment_summary
from app.env import LANGCHAIN_ENDPOINT, LANGCHAIN_PROJECT, LANGCHAIN_TRACING_V2, OPENAI_API_KEY
from app.image_utils import check_file_format_and_convert, downsize_and_convert_to_base64
from app.app_logger import appLogger
from app.model import AttachedInfo, EmailAttachment, EmailData, EmailSummary, FullyLoadedEmailData
from app.s3_repo import load_file_from_s3, rename_file_in_s3, upload_ocr_file_in_s3, upload_pdf_image_to_s3
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts.chat import ChatPromptTemplate
from openai import RateLimitError

system_prompt_format_email = '''
    You are an AI assistant in a company, tasked with converting poorly formatted email content from an EML file into a human-readable format. 
    Your goal is to make the email easy to read while maintaining its original structure, including forwarded content and email threads.

    Guidelines for formatting the email:
    1. Clearly separate and label different sections of the email (e.g., From, To, Subject, Date, Body).
    2. Use appropriate spacing and line breaks to improve readability.
    3. Indent forwarded content and replies in email threads.
    4. Preserve the chronological order of email threads.
    5. Remove any unnecessary or repetitive information.
    6. Format any attachments or embedded images appropriately. 
        a. Replace Base64-encoded attachments with a placeholder text like "[Attachment: file_name.jpg]"

    Your formatted email should be easy to read and understand, with a clear structure that reflects the original email's content and flow. 
    Make sure to preserve all important information while eliminating any unnecessary clutter or formatting issues.

    Do not include any explanations or comments. Start your response with an email summary.
'''

system_prompt_ocr_attachments = '''
    You are an AI assistant in a company, tasked with reading a document and returning a well-formatted text. 
    Your goal is to process the given document and present it in a clear, organized, and easily readable format. Follow these instructions carefully:

    1. Read through the entire document carefully, paying attention to its structure, content, and any formatting elements present.

    2. When formatting the output, follow these general guidelines:
    - Use consistent spacing throughout the document
    - Ensure proper indentation for nested elements
    - Maintain a clear hierarchy of headings and subheadings
    - Preserve the original meaning and intent of the content

    3. Handle specific elements as follows:
    - Headings: Use appropriate heading levels and ensure they are properly nested
    - Lists: Maintain bullet points or numbering, and use consistent indentation for nested lists
    - Tables: Preserve table structure and alignment, using ASCII characters if necessary
    - Quotes: Indent and clearly demarcate quoted text
    - Links: Preserve hyperlinks and their descriptive text

    4. Ensure that the formatting is consistent and enhances readability without altering the original content's meaning.

    Remember to maintain the document's original structure and hierarchy while improving its overall formatting and presentation.
    
    Do not include any explanations or comments. Start your response document content.
'''

system_prompt_summary_attachments = '''
   You are an AI assistant in a company, tasked with reviewing a document and generating a summary. Follow these instructions carefully to complete the task:

    1. First, carefully read the following document.

    2. After reading the document, analyze its content. Consider the following:
    - The main topic or theme of the document
    - Key points or arguments presented
    - Important facts, figures, or statistics
    - Any conclusions or recommendations made

    3. Generate a summary of the document, keeping in mind these guidelines:
    - The summary should be concise, typically no more than 10-15% of the original document's length
    - Focus on the most important information and main ideas
    - Maintain the original document's tone and style
    - Use your own words; avoid copying sentences directly from the original text
    - Ensure the summary is coherent and flows logically

    4. Present your summary in the following JSON format:

    {
        "suggested_file_name": "[Suggested name of the file here. Type: String]",
        "addressed_to_email" : "[Email address of the person the document is addressed to. Type: String]",
        "addressed_to_name" : "[Name of the person the document is addressed to. Type: String]", 
        "summary": "[File summary. Type: String]",
        "urgent": ["[List urgent points from the document. Type: List<String>]"]
    }

    5. For the suggested_file_name:
    - It must be less than 256 characters
    - It should contain the name of the main person from the document and the type of the document
    - Examples: "John Doe - MRI Report", "Anna Doe - Appointment Details", "John Doe - Payment Receipt"

    6. For the addressed_to_email & addressed_to_name:
    - If Document mentiones specific doctor or person to whom it may be concerned, use the email and name of that person
    - If the document is not addressed to a specific person, use "" for both fields    

    6. Important: Your response must start with the '{' character of the JSON object.

    Remember to be objective and accurate in your summary, capturing the essence of the original document without adding any personal opinions or interpretations.'''

system_prompt_review_email = '''
    You are a helpful assistant in a company, assigned to review emails send to the staff.
    Your task is to review the content of emails, find correct recepiet, review content and attachments and forward a well formater email. 

    Please follow these steps to complete your task:

    1. Carefully read through the entire email content, including any forwarded messages.

    2. Extract from the email:
        a. real sender's email and name, root sender of all inmportant information 
        b. Real recepient of the email, whom is all of the content and attachemnet must be send to
        Note: Real sender and receiver might be mentioned in the attached documents.

    3. Create a short highlight of the forwarded email content. Include important point and action items.
    
    4. Write a more detailed summary (3-5 sentences). Look through the whole histore of the email and attached documents

    5. Determine the email priority on a scale of 1 to 5, where:
    1 = Not important
    2 = Low priority
    3 = Normal priority
    4 = High priority
    5 = Urgent
    
    Consider factors such as:
    - Real Sender's position or importance
    - Content urgency
    - Potential impact on client well being
    - Deadlines mentioned in the email
    
    6. Create a new Subject of the based on the content following format: [Priority: Normal] Subject 

    7. If you were not able to extract to exract any informatoin, provide corresponding summary and subject.

    8. Compile all the information into the following JSON format:

    {
    "sender_email": "",
    "sender_name": "",
    "receiver_email": "",
    "receiver_name": "",
    "email_subject": "",
    "email_highlights": "",
    "email_summary": "",
    "email_priority": 0
    }
    
    9. Response MUST start from the '{' character and end with the '}' character. The JSON object should not contain any other characters, including spaces, tabs, or newlines. 

    10. All text fields max length is 512 characters, except "forwarded_email_short_summary" and "forwarded_email_summary" which are not constrained.

    Please provide your final output in this JSON format, ensuring all fields are filled with the appropriate information or empty if the information is not available.
'''

# Format email from plan body to humar readable format 

def format_email(email_id: str, email_content: EmailData) -> str:
    appLogger.debug(f"[EmailSnap]Formatting email with email_id: {email_id}")
    messages = [
        SystemMessage(content=system_prompt_format_email),
    ]
    email_for_review = {
        'sender': email_content.sender,
        'recipient': email_content.recipient,
        'subject': email_content.subject,
        'date': email_content.date,
        'body_plain': email_content.body_plain,
    }
    json_email = json.dumps(email_for_review)
    appLogger.debug(f"[EmailSnap]Sending email for review: {email_id}")
    messages.append(HumanMessage(content=json_email))  
    summary = invoke_with_retry(messages)
    appLogger.debug(f"[EmailSnap]Formatted email: {email_id}. \n {summary.content}") 
    return summary.content

#  Process file attachments

def send_to_llm_for_review(file_name: str, base64_data: str) -> Optional[str]:
    appLogger.debug(f"[EmailSnap]Sending file '{file_name}' to LLM for review")
    
    template = ChatPromptTemplate.from_messages(
        [
            SystemMessage(content=system_prompt_ocr_attachments),
            (
                "human",
                [
                    {
                        "type": "image_url",
                        "image_url": "data:image/jpeg;base64,{image_base64}",
                    },
                ],
            ),
        ]   
    )

    prompt_value = template.format_messages(image_base64=base64_data)

    try:
        llm_summary = invoke_with_retry(prompt_value)
        appLogger.debug(f"[EmailSnap]LLM review completed for file '{file_name}'")
        appLogger.debug(llm_summary.content)
        return llm_summary.content
    except Exception as e:
        appLogger.debug(f"[EmailSnap]Failed to send file '{file_name}' to LLM for review: {e}")
        return None

def process_and_send_email_attachment(email_id: str, file_key: str) -> Optional[str]:
    file_extension = file_key.split('.')[-1]
    appLogger.debug(f"[EmailSnap]Processing file '{file_key}' with extension '{file_extension}'")
    
    file_data = load_file_from_s3(file_key)
    if not file_data:
        appLogger.debug(f"[EmailSnap]No data for file '{file_key}'")
        return None
    
    images = check_file_format_and_convert(file_data, file_extension)
    if not images:
        appLogger.debug(f"[EmailSnap]Failed to process file '{file_key}'")
        return None
    
    try:
        i = 0
        for image in images:
            i += 1
            buffer = BytesIO()
            image.save(buffer, format='JPEG')
            upload_pdf_image_to_s3(i,file_key=file_key, image=buffer.getvalue())
    except Exception as e:
        appLogger.debug(f"[EmailSnap]Failed to upload image to S3 for file '{file_key}': {e}")

    result_summary = ""
    
    for image in images:
        base64_data = downsize_and_convert_to_base64(image)
        if not base64_data:
            appLogger.debug(f"[EmailSnap]Failed to process image for file '{file_key}'")
            continue
        
        llm_content = send_to_llm_for_review(file_key, base64_data)
        if not llm_content:
            appLogger.debug(f"[EmailSnap]Failed to get LLM content for file '{file_key}'")
            continue
    
        result_summary += f"{llm_content}\n"
    
    appLogger.debug(f"[EmailSnap]Processing complete for file '{file_key}'")
    return result_summary if result_summary else None

def handle_email_processing(email_id: str, file_key: str) -> Optional[str]:
    appLogger.debug(f"[EmailSnap]Handling email processing for '{file_key}'")
    result = process_and_send_email_attachment(email_id, file_key)
    with get_db_session() as db:
            insert_attachment_summary(db, email_id, file_key, result)
    if result:
        appLogger.debug(f"[EmailSnap]Email processing complete for '{file_key}'")
        print(result)  # Output the appended results
    else:
        appLogger.debug(f"[EmailSnap]Email processing failed or incomplete for '{file_key}'")
    return result

# Summarize email attachments 

def summarize_email_attachments(email_id: str, file_key: str, attached_file: str) -> AttachedInfo:
    messages = [
        SystemMessage(content=system_prompt_summary_attachments),
    ]
    messages.append(HumanMessage(content=attached_file))    
    summary = invoke_with_retry(messages)
    
    summary = AttachedInfo.model_validate_json(summary.content)
    summary.original_file_name = file_key
    summary.email_id = email_id

    return summary

# Process email with LLM

def process_attachments(email_id: str, attachments: List[EmailAttachment]) -> List[AttachedInfo]:
    summarised_attachments = []
    for attachment in attachments:
        response = handle_email_processing(email_id, attachment.file_key)
        if response is not None:
            attachment_data = summarize_email_attachments(email_id, attachment.file_key, response)
            new_key = rename_file_in_s3(email_id, attachment.file_key, attachment_data.suggested_file_name)
            upload_ocr_file_in_s3(new_key, response)
            summarised_attachments.append(attachment_data)
            attachment.new_file_key = new_key
    return summarised_attachments

#  Execute chain

def execute_llm_chain(email_id: str, email_data: EmailData) -> FullyLoadedEmailData:
    formatted_email = format_email(email_id, email_data)
    appLogger.debug(f"[EmailSnap]Done formatting email: {email_id}.")
    summarised_attachments = process_attachments(email_id, email_data.attachments)
    appLogger.debug(f"[EmailSnap]Done processign attachment: {email_id}.")
    appLogger.debug(f"[EmailSnap]Summarised attachments: {email_id}. {summarised_attachments}")
    for summarised_attachment in summarised_attachments:
        if summarised_attachment.original_file_name:
            appLogger.debug(f"[EmailSnap]Replacing {summarised_attachment.original_file_name} with {summarised_attachment.suggested_file_name} in email: {email_id}.")
            formatted_email = formatted_email.replace(summarised_attachment.original_file_name, summarised_attachment.suggested_file_name)
    
    if summarised_attachments:
        short_att_summary = '\n'.join([x.to_review_string() for x in summarised_attachments])
        appLogger.debug(f"[EmailSnap]Content: {short_att_summary}")
        human_message = HumanMessage(content=f"{formatted_email} \n Attachments: {short_att_summary}")
    else:
        human_message = HumanMessage(content=formatted_email)
        
    appLogger.debug(f"[EmailSnap]Done replacing attachments: {email_id}.")
    
    messages = [
        SystemMessage(content=system_prompt_review_email),
        human_message,
    ]
    
    appLogger.debug(f"[EmailSnap]Final Review: {email_id}.")
    
    summary = invoke_with_retry(messages)
    
    appLogger.debug(f"[EmailSnap]Final Review Done: {email_id}. Summary: {summary.content}")
    
    return FullyLoadedEmailData(summary=summary.content, data=email_data, attachments=summarised_attachments)
    
    
def invoke_with_retry(*args, **kwargs):
    max_retries = 3
    retries = 0
    
    while retries < max_retries:
        try:
            result = _get_llm().invoke(*args, **kwargs)
            return result
        except RateLimitError:
            appLogger.error("[EmailSnap]Rate limit reached. Waiting 10 seconds before retrying...")
            retries += 1
            time.sleep(10 * retries)

    raise RateLimitError("Max retries reached. Please try again later.")
    
_llm_instance = None

def _get_llm():
    global _llm_instance
    if _llm_instance is None:
        appLogger.debug("[EmailSnap]Creating new LLM instance.")
        appLogger.debug(f"[EmailSnap]LangSmith enabled: {LANGCHAIN_TRACING_V2}. Project name: {LANGCHAIN_PROJECT}, URL: {LANGCHAIN_ENDPOINT}")
        _llm_instance = ChatOpenAI(
                model="gpt-4o",
                api_key=OPENAI_API_KEY
            )
    return _llm_instance