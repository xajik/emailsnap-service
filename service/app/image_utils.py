import base64
from io import BytesIO
from PIL import Image
from typing import List, Optional
from app.app_logger import appLogger
from pdf2image import convert_from_bytes


def downsize_and_convert_to_base64(image: Image.Image, target_size=(640, 640)) -> Optional[str]:
    try:
        appLogger.debug(f"[EmailSnap]Resizing image to {target_size}")
        image.thumbnail(target_size)  # Resize while preserving aspect ratio
        buffer = BytesIO()
        image.save(buffer, format='JPEG')  # Convert to JPEG format
        base64_data = base64.b64encode(buffer.getvalue()).decode('utf-8')
        appLogger.debug("Image successfully converted to Base64")
        return base64_data
    except Exception as e:
        appLogger.debug(f"[EmailSnap]Failed to resize or convert image to Base64: {e}")
        return None
    
    
def check_file_format_and_convert(file_data: bytes, file_extension: str) -> Optional[List[Image.Image]]:
    appLogger.debug(f"[EmailSnap]Checking file format: '{file_extension}'")
    if file_extension.lower() == 'pdf':
        try:
            images = convert_from_bytes(file_data)
            appLogger.debug(f"[EmailSnap]Converted PDF to {len(images)} images")
            return images
        except Exception as e:
            appLogger.debug(f"[EmailSnap]Failed to convert PDF: {e}")
            return None
    elif file_extension.lower() in ['png', 'jpeg', 'jpg']:
        try:
            image = Image.open(BytesIO(file_data))
            appLogger.debug(f"[EmailSnap]Loaded image: '{file_extension}'")
            return [image]
        except Exception as e:
            appLogger.debug(f"[EmailSnap]Failed to load image '{file_extension}': {e}")
            return None
    else:
        appLogger.debug(f"[EmailSnap]Unsupported file format: '{file_extension}'")
        return None