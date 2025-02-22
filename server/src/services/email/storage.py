import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from ...utils.files import create_safe_folder_name, setup_directories
from .parser import parse_forwarded_email, process_message_part

class EmailStorage:
    def __init__(self, email: str):
        self.email = email
        _, self.emails_dir, _ = setup_directories(email)

    async def should_update(self) -> bool:
        """Check if directory exists and needs update."""
        json_file = self.emails_dir / "email_conversations.json"
        return json_file.exists()

    async def backup_emails(self, service: Any) -> Dict:
        """Initial backup of emails."""
        try:
            email_data = []

            # Get threads
            threads_response = service.users().threads().list(userId='me').execute()
            threads = threads_response.get('threads', [])
            
            for thread in threads:
                thread_id = thread['id']
                thread_data = service.users().threads().get(userId='me', id=thread_id).execute()
                
                # Create conversation folder
                first_message = thread_data['messages'][0]
                headers = {header['name'].lower(): header['value'] 
                          for header in first_message['payload']['headers']}
                
                timestamp = datetime.fromtimestamp(
                    int(first_message['internalDate'])/1000
                ).strftime("%Y-%m-%d_%H-%M-%S")
                
                subject = headers.get('subject', 'No Subject')
                folder_name = create_safe_folder_name(subject, timestamp)
                conv_folder = self.emails_dir / folder_name
                conv_folder.mkdir(parents=True, exist_ok=True)

                conversation_data = {
                    "ConversationID": thread_id,
                    "Topic": subject,
                    "Messages": []
                }

                # Process each message
                for idx, message in enumerate(thread_data['messages']):
                    headers = {header['name'].lower(): header['value'] 
                              for header in message['payload']['headers']}
                    
                    msg_folder = conv_folder / f"message_{idx+1}"
                    msg_folder.mkdir(parents=True, exist_ok=True)

                    text_content = ""
                    html_content = ""
                    attachment_files = []

                    def process_parts(parts):
                        nonlocal text_content, html_content
                        for part in parts:
                            mime_type = part.get('mimeType', '')
                            if mime_type.startswith('multipart/'):
                                if 'parts' in part:
                                    process_parts(part['parts'])
                            else:
                                content, content_type = process_message_part(
                                    service, message['id'], part, msg_folder, attachment_files)
                                if content:
                                    if content_type == 'text/plain':
                                        text_content = content if not text_content else text_content + "\n\n" + content
                                    elif content_type == 'text/html':
                                        html_content = content if not html_content else html_content + "<br><br>" + content

                    if 'parts' in message['payload']:
                        process_parts(message['payload']['parts'])
                    elif 'body' in message['payload']:
                        content, content_type = process_message_part(
                            service, message['id'], message['payload'], msg_folder, attachment_files)
                        if content_type == 'text/plain':
                            text_content = content
                        elif content_type == 'text/html':
                            html_content = content
                    
                    # Save content
                    if text_content:
                        (msg_folder / "EMAIL_BODY.txt").write_text(text_content, encoding="utf-8")
                    if html_content:
                        (msg_folder / "EMAIL_BODY.html").write_text(html_content, encoding="utf-8")

                    # Check forwarded
                    forwarded_info = parse_forwarded_email(text_content)
                    
                    # Prepare message data
                    message_data = {
                        "Subject": subject,
                        "ConversationTopic": subject,
                        "OrderInConversation": idx + 1,
                        "AttachmentFiles": [
                            str((msg_folder / filename).relative_to(self.emails_dir))
                            for filename in attachment_files
                        ],
                        "HasHtml": bool(html_content)
                    }

                    if forwarded_info["is_forwarded"]:
                        message_data.update({
                            "SenderName": forwarded_info["original"]["from"],
                            "To": forwarded_info["original"]["to"],
                            "CC": forwarded_info["original"]["cc"],
                            "ReceivedTime": forwarded_info["original"]["date"],
                            "Body": forwarded_info["original"]["body"],
                            "ForwardedBy": {
                                "From": headers.get('from', 'Unknown Sender'),
                                "Date": headers.get('date', '')
                            }
                        })
                    else:
                        message_data.update({
                            "SenderName": headers.get('from', 'Unknown Sender'),
                            "To": headers.get('to', ''),
                            "CC": headers.get('cc', ''),
                            "ReceivedTime": headers.get('date', ''),
                            "Body": text_content
                        })

                    conversation_data["Messages"].append(message_data)

                email_data.append(conversation_data)

            # Save JSON structure
            json_file = self.emails_dir / "email_conversations.json"
            json_file.write_text(json.dumps(email_data, indent=4, ensure_ascii=False), encoding='utf-8')

            return {
                "message": "Backup complete",
                "data_path": str(self.emails_dir),
                "conversations": email_data
            }

        except Exception as e:
            print(f"Error in backup_emails: {str(e)}")
            raise

    async def update_emails(self, service: Any) -> Dict:
        """Update existing email backup."""
        print(f"Skipping email update for {self.email} (temporarily disabled)")
        return {
            "message": "Update skipped",
            "data_path": str(self.emails_dir),
            "conversations": []
        }
