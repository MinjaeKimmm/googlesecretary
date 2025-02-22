import os
import json
from datetime import datetime
from typing import Any, Dict, List, Optional
from ...utils.files import setup_directories, create_safe_folder_name

class DriveStorage:
    def __init__(self, email: str):
        """Initialize DriveStorage with user email."""
        print(f"Initializing DriveStorage for user: {email}")
        self.email = email
        self.base_path = setup_directories(email)
        self.drive_path = os.path.join(self.base_path, 'drive')
        os.makedirs(self.drive_path, exist_ok=True)
        print(f"DriveStorage initialized at: {self.drive_path}")
    
    def _get_folder_path(self, topic: str) -> str:
        """Get the path for a specific folder."""
        folder_name = create_safe_folder_name(topic)
        return os.path.join(self.drive_path, folder_name)
    
    def _save_folder_metadata(self, folder_path: str, metadata: Dict) -> None:
        """Save folder metadata to a JSON file."""
        metadata_path = os.path.join(folder_path, 'metadata.json')
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
    
    def _save_folder_content(self, folder_path: str, content: str) -> None:
        """Save folder content to a text file."""
        content_path = os.path.join(folder_path, 'content.txt')
        with open(content_path, 'w') as f:
            f.write(content)
    
    def backup_folder(self, folder_id: str, topic: str, metadata: Dict, content: str) -> str:
        """Backup a Drive folder with its metadata and content."""
        try:
            print(f"Starting backup of folder {folder_id} with topic: {topic}")
            folder_path = self._get_folder_path(topic)
            os.makedirs(folder_path, exist_ok=True)
            
            # Save metadata and content
            print(f"Saving metadata for folder: {folder_id}")
            self._save_folder_metadata(folder_path, metadata)
            
            print(f"Saving content for folder: {folder_id}")
            self._save_folder_content(folder_path, content)
            
            print(f"Successfully backed up folder {folder_id} to {folder_path}")
            return folder_path
        except OSError as e:
            print(f"OS error backing up folder {folder_id}: {str(e)}")
            raise
        except Exception as e:
            print(f"Unexpected error backing up folder {folder_id}: {str(e)}")
            raise
    
    def get_folder_content(self, topic: str) -> Optional[str]:
        """Get the content of a backed up folder."""
        try:
            folder_path = self._get_folder_path(topic)
            content_path = os.path.join(folder_path, 'content.txt')
            
            if not os.path.exists(content_path):
                return None
            
            with open(content_path, 'r') as f:
                return f.read()
        except Exception as e:
            print(f"Error reading folder content for {topic}: {str(e)}")
            return None
    
    def get_folder_metadata(self, topic: str) -> Optional[Dict]:
        """Get the metadata of a backed up folder."""
        try:
            folder_path = self._get_folder_path(topic)
            metadata_path = os.path.join(folder_path, 'metadata.json')
            
            if not os.path.exists(metadata_path):
                return None
            
            with open(metadata_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error reading folder metadata for {topic}: {str(e)}")
            return None
    
    async def should_update(self, folder_id: str) -> bool:
        """Check if a folder exists and needs update."""
        try:
            folder_path = self._get_folder_path(folder_id)
            metadata_path = os.path.join(folder_path, 'metadata.json')
            return os.path.exists(metadata_path)
        except Exception as e:
            print(f"Error checking folder update status: {str(e)}")
            return False
    
    async def update_folder(self, service: Any, folder_id: str, topic: str, metadata: Dict, content: str) -> str:
        """Update an existing folder backup."""
        try:
            print(f"Skipping folder update for {folder_id} (temporarily disabled)")
            folder_path = self._get_folder_path(topic)
            return folder_path
        except Exception as e:
            print(f"Error in update_folder: {str(e)}")
            raise
    
    def list_backed_up_folders(self) -> List[Dict]:
        """List all backed up folders with their metadata."""
        try:
            folders = []
            for folder_name in os.listdir(self.drive_path):
                folder_path = os.path.join(self.drive_path, folder_name)
                if os.path.isdir(folder_path):
                    metadata = self.get_folder_metadata(folder_name)
                    if metadata:
                        folders.append({
                            'name': folder_name,
                            'metadata': metadata
                        })
            return folders
        except Exception as e:
            print(f"Error listing backed up folders: {str(e)}")
            return []
