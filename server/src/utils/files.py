import re
from pathlib import Path
from datetime import datetime

def create_safe_name(name: str) -> str:
    """Create a safe filename/foldername by replacing invalid characters with underscores.
    Preserves Korean characters and other Unicode text while only replacing characters
    that are unsafe for filesystems.
    """
    # Only replace characters that are unsafe for filesystems
    unsafe_chars = '<>:"\/|?*\n\r\t'
    safe_name = name
    
    # Replace unsafe characters with underscore
    for c in unsafe_chars:
        safe_name = safe_name.replace(c, '_')
    
    # Remove leading/trailing spaces and dots
    safe_name = safe_name.strip('. ')
    
    # Collapse multiple underscores into one
    safe_name = re.sub(r'_+', '_', safe_name)
    
    # Ensure the name is not empty
    if not safe_name:
        safe_name = 'unnamed'
        
    return safe_name

def create_safe_folder_name(topic: str, timestamp: str = None, max_topic_length: int = 100) -> str:
    """Create a safe folder name using topic and timestamp."""
    if timestamp is None:
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
    clean_topic = create_safe_name(topic)
    clean_topic = clean_topic[:max_topic_length]
    return f"{clean_topic}_{timestamp}"

def setup_directories(email: str) -> Path:
    """Setup directories for a specific user's email.
    Returns base_dir which contains emails and drive subdirectories.
    """
    base_dir = Path('data') / email
    emails_dir = base_dir / 'emails'
    drive_dir = base_dir / 'drive'
    
    base_dir.mkdir(parents=True, exist_ok=True)
    emails_dir.mkdir(parents=True, exist_ok=True)
    drive_dir.mkdir(parents=True, exist_ok=True)
    
    return base_dir
