import email
from email import policy
import os
from app.app_logger import appLogger
import boto3
from app.env import AWS_ACCESS_KEY_ID, AWS_REGION, AWS_SECRET_ACCESS_KEY, EMAIL_BUCKET_NAME


if AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY:
    s3_client = boto3.client(
        "s3",
        region_name=AWS_REGION,
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY
    )
else:
    s3_client = boto3.client("s3", region_name=AWS_REGION)

def save_file_to_s3(s3_client, sender_email, file_name, file_data, content_type):
    try:
        path = f"processed/{sender_email}/{file_name}"
        response = s3_client.put_object(
            Bucket=EMAIL_BUCKET_NAME,
            Key=path,
            Body=file_data,
            ContentType=content_type
        )
        return response
    except Exception as e:
        print(f"Error uploading file to S3: {str(e)}")
        return None

def fetch_email_from_s3(email_id: str) -> str:
    appLogger.debug(f"[EmailSnap]Fetching email from S3 with email_id: {email_id}")
    response = s3_client.get_object(Bucket=EMAIL_BUCKET_NAME, Key=f"emails/{email_id}")    
    body = response['Body'].read()
    return email.message_from_bytes(body,  policy=policy.default)


def upload_file_to_s3(email_id, file_name, file_data, content_type):
    s3_key = f"processed/{email_id}/{file_name}"
    s3_client.put_object(
        Bucket=EMAIL_BUCKET_NAME,
        Key=s3_key,
        Body=file_data,
        ContentType=content_type
    )
    return s3_key

def load_file_from_s3(file_key: str) -> bytes:
    response = s3_client.get_object(Bucket=EMAIL_BUCKET_NAME, Key=file_key)
    return response['Body'].read()

def rename_file_in_s3(email_id, old_file_key, new_file_key):
    _, file_extension = os.path.splitext(old_file_key)
    s3_key = f"processed/{email_id}/{new_file_key}{file_extension}"
    s3_client.copy_object(
        Bucket=EMAIL_BUCKET_NAME,
        CopySource={'Bucket': EMAIL_BUCKET_NAME, 'Key': old_file_key},
        Key=s3_key
    )

    s3_client.delete_object(Bucket=EMAIL_BUCKET_NAME, Key=old_file_key)
    
    appLogger.debug(f"[EmailSnap]File renamed from {old_file_key} to {s3_key}")
    return s3_key

def upload_ocr_file_in_s3(file_key, ocr):
    folder_path, file_name_with_ext = os.path.split(file_key)
    file_name, _ = os.path.splitext(file_name_with_ext)
    s3_key = f"{folder_path}/{file_name}_llm_ocr.txt"
    s3_client.put_object(
        Bucket=EMAIL_BUCKET_NAME,
        Key=s3_key,
        Body=ocr,
        ContentType='text/plain'
    )
    appLogger.debug(f"[EmailSnap]OCR file uploaded to S3 with key: {s3_key}")
    return s3_key

def upload_pdf_image_to_s3(id, file_key, image):
    folder_path, file_name_with_ext = os.path.split(file_key)
    file_name, _ = os.path.splitext(file_name_with_ext)
    s3_key = f"{folder_path}/{file_name}_{id}.jpeg"
    s3_client.put_object(
        Bucket=EMAIL_BUCKET_NAME,
        Key=s3_key,
        Body=image,
        ContentType='imaeg/jpeg'
    )
    appLogger.debug(f"[EmailSnap]Uploaded PDF image to S3 with key: {s3_key}")
    return s3_key