import re
import html
import email
import base64
import logging
from email.header import decode_header
from pathlib import Path
from typing import Tuple, Dict, List, Any, Optional

logger = logging.getLogger(__name__)

def parse_forwarded_email(body: str) -> dict:
    """Parse forwarded email to extract original message metadata and content."""
    result = {
        "is_forwarded": False,
        "original": {
            "from": "",
            "to": "",
            "cc": "",
            "subject": "",
            "date": "",
            "body": ""
        }
    }
    
    if not body:
        return result
    
    # Clean up HTML entities
    body = html.unescape(body)
    
    # Check for forwarded message markers
    markers = [
        "-----Original Message-----",
        "---------- Forwarded message ----------",
        "Begin forwarded message:"
    ]
    
    for marker in markers:
        if marker in body:
            result["is_forwarded"] = True
            parts = body.split(marker, 1)
            if len(parts) == 2:
                original_content = parts[1].strip()
                
                # Split into headers and body
                sections = re.split(r'\n\s*\n', original_content, maxsplit=1)
                headers_section = sections[0] if sections else ""
                body_section = sections[1] if len(sections) > 1 else ""
                
                # Extract headers
                header_patterns = [
                    ('from', r'From:\s*([^T][^o:][^\n]+?)(?=(?:To:|Subject:|Sent:|Date:|$))'),
                    ('to', r'To:\s*([^C][^c:][^\n]+?)(?=(?:Cc:|Subject:|Sent:|Date:|$))'),
                    ('cc', r'Cc:(?:\s*([^S][^e][^n][^t:][^\n]+?))?(?=(?:Subject:|Sent:|Date:|$))'),
                    ('date', r'(?:Sent|Date):\s*([^S][^u][^b][^j][^\n]+?)(?=(?:Subject:|$))')
                ]
                
                header_fields = {}
                for field_name, pattern in header_patterns:
                    match = re.search(pattern, headers_section, re.IGNORECASE | re.DOTALL)
                    if match:
                        value = match.group(1) if field_name != 'cc' else (match.group(1) or "")
                        if value:
                            value = value.strip()
                            value = re.sub(r';\s*$', '', value)
                            header_fields[field_name] = value
                
                # Extract subject
                subject_match = re.search(r'Subject:\s*(.+?)(?=\n\s*\n|$)', headers_section, re.IGNORECASE | re.DOTALL)
                if subject_match:
                    subject = subject_match.group(1).strip().split('\n')[0].strip()
                    header_fields['subject'] = subject
                
                # Update result
                result['original'].update(header_fields)
                
                # Clean up body
                if body_section:
                    body_lines = []
                    started = False
                    for line in body_section.split('\n'):
                        if not started and re.match(r'^(From|To|Cc|Subject|Sent|Date):', line.strip(), re.IGNORECASE):
                            continue
                        started = True
                        body_lines.append(line)
                    
                    body_text = "\n".join(body_lines).strip()
                    body_text = re.sub(r'\r\n', '\n', body_text)
                    body_text = re.sub(r'\n{3,}', '\n\n', body_text)
                    result["original"]["body"] = body_text
                break
    
    # Clean up HTML entities in all fields
    for key in result["original"]:
        if result["original"][key]:
            result["original"][key] = html.unescape(result["original"][key])
    
    return result

def decode_email_part(part) -> Tuple[str, str]:
    """Decode an email message part and return its content and type."""
    content = ""
    content_type = part.get_content_type()
    
    if part.get_content_maintype() == 'text':
        try:
            payload = part.get_payload(decode=True)
            charset = part.get_content_charset() or 'utf-8'
            content = payload.decode(charset, errors='replace')
            
            if content:
                content = html.unescape(content)
                content = re.sub(r'\r\n', '\n', content)
                content = re.sub(r'\n{3,}', '\n\n', content)
        except Exception as e:
            print(f"Error decoding text content: {str(e)}")
    
    return content, content_type

def process_message_part(service: Any, message_id: str, part: Dict, msg_folder: Path, attachment_files: List[str]) -> Tuple[Any, str]:
    """Process a message part and return content and content type."""
    content = ""
    content_type = part.get("mimeType", "")
    body = part.get("body", {})
    
    # Handle text content
    if content_type in ["text/plain", "text/html"]:
        if "data" in body:
            try:
                data = body["data"]
                try:
                    content = base64.urlsafe_b64decode(data.encode('utf-8')).decode('utf-8')
                except:
                    padded_data = data + '=' * (4 - len(data) % 4)
                    content = base64.b64decode(padded_data.encode('utf-8')).decode('utf-8')
            except Exception as e:
                logger.error(f"Error decoding {content_type} content: {str(e)}")
        elif "attachmentId" in body:
            try:
                attachment = service.users().messages().attachments().get(
                    userId="me",
                    messageId=message_id,
                    id=body["attachmentId"]
                ).execute()
                content = base64.urlsafe_b64decode(attachment["data"].encode('utf-8')).decode('utf-8')
            except Exception as e:
                logger.error(f"Error fetching {content_type} attachment: {str(e)}")
    
    # Handle attachments and inline images
    elif "filename" in part or content_type.startswith("image/"):
        filename = part.get("filename", "")
        if not filename and content_type.startswith("image/"):
            # Generate filename for inline image
            content_id = next((h["value"] for h in part.get("headers", []) if h["name"].lower() == "content-id"), None)
            if content_id:
                ext = content_type.split("/")[1]
                filename = f"inline_{content_id.strip('<>')}_{len(attachment_files)}.{ext}"
            else:
                filename = f"inline_image_{len(attachment_files)}.{content_type.split('/')[1]}"
        
        if filename:
            from ...utils.files import create_safe_name
            clean_filename = create_safe_name(filename)
            attachment_path = msg_folder / clean_filename
            
            # Get attachment data
            if "attachmentId" in body:
                try:
                    attachment = service.users().messages().attachments().get(
                        userId="me",
                        messageId=message_id,
                        id=body["attachmentId"]
                    ).execute()
                    
                    file_data = base64.urlsafe_b64decode(attachment["data"])
                    attachment_path.write_bytes(file_data)
                    attachment_files.append(clean_filename)
                    
                    # For inline images, return the saved path
                    if content_type.startswith("image/"):
                        content = attachment_path
                except Exception as e:
                    logger.error(f"Error processing attachment {filename}: {str(e)}")
    
    return content, content_type

def process_raw_message(raw_message: bytes) -> Tuple[Dict[str, str], str, str, List[Tuple[str, Any]]]:
    """Process a raw email message and extract its content."""
    email_msg = email.message_from_bytes(raw_message)
    text_content = ""
    html_content = ""
    attachments = []
    
    def decode_header_str(header: str) -> str:
        """Decode email header string."""
        decoded_parts = decode_header(header)
        return ' '.join(str(part[0], part[1] or 'utf-8') if isinstance(part[0], bytes) else str(part[0]) for part in decoded_parts)
    
    # Extract headers
    headers = {
        'subject': decode_header_str(email_msg.get('subject', '')),
        'from': decode_header_str(email_msg.get('from', '')),
        'to': decode_header_str(email_msg.get('to', '')),
        'cc': decode_header_str(email_msg.get('cc', '')),
        'date': decode_header_str(email_msg.get('date', ''))
    }
    
    # Process message parts
    if email_msg.is_multipart():
        for part in email_msg.walk():
            if part.get_content_maintype() == 'multipart':
                continue
            
            content, content_type = decode_email_part(part)
            
            if content_type == 'text/plain':
                text_content = text_content + '\n\n' + content if text_content else content
            elif content_type == 'text/html':
                html_content = html_content + '<br><br>' + content if html_content else content
            
            filename = part.get_filename()
            if filename:
                attachments.append((filename, part))
    else:
        content, content_type = decode_email_part(email_msg)
        if content_type == 'text/plain':
            text_content = content
        elif content_type == 'text/html':
            html_content = content
    
    return headers, text_content, html_content, attachments
