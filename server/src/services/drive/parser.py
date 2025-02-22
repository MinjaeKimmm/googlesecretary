import os
from typing import Dict, List, Optional, Any, Union
from datetime import datetime

def parse_folder_metadata(folder: Dict) -> Dict:
    """Parse folder metadata from Drive API response."""
    return {
        'id': folder.get('id'),
        'name': folder.get('name'),
        'mimeType': folder.get('mimeType'),
        'createdTime': folder.get('createdTime'),
        'modifiedTime': folder.get('modifiedTime'),
        'owners': [owner.get('emailAddress') for owner in folder.get('owners', [])],
        'permissions': folder.get('permissions', []),
        'shared': folder.get('shared', False),
        'size': folder.get('size', '0'),
        'parents': folder.get('parents', [])
    }

def parse_file_metadata(file: Dict) -> Dict:
    """Parse file metadata from Drive API response."""
    return {
        'id': file.get('id'),
        'name': file.get('name'),
        'mimeType': file.get('mimeType'),
        'createdTime': file.get('createdTime'),
        'modifiedTime': file.get('modifiedTime'),
        'size': file.get('size', '0'),
        'parents': file.get('parents', []),
        'webViewLink': file.get('webViewLink'),
        'iconLink': file.get('iconLink'),
        'thumbnailLink': file.get('thumbnailLink'),
        'shared': file.get('shared', False)
    }

def parse_folder_contents(service: Any, folder_id: str, depth: int = 1, include_team_drives: bool = False) -> List[Dict]:
    """Recursively parse folder contents up to specified depth.
    
    Args:
        service: Google Drive service instance
        folder_id: ID of the folder to parse
        depth: How deep to recurse into subfolders (default: 1)
        include_team_drives: Whether to include shared drives (default: False)
    
    Returns:
        List of dictionaries containing file/folder metadata
    """
    try:
        contents = []
        query = f"'{folder_id}' in parents and trashed=false"
        
        # Build request parameters
        params = {
            'q': query,
            'spaces': 'drive',
            'fields': ('files(id, name, mimeType, createdTime, modifiedTime, size, parents, '
                      'webViewLink, iconLink, thumbnailLink, shared, owners, permissions)'),
            'supportsAllDrives': include_team_drives,
            'includeItemsFromAllDrives': include_team_drives
        }
        
        # Handle pagination
        page_token = None
        while True:
            if page_token:
                params['pageToken'] = page_token
            
            try:
                response = service.files().list(**params).execute()
                items = response.get('files', [])
                
                for item in items:
                    try:
                        is_folder = item['mimeType'] == 'application/vnd.google-apps.folder'
                        item_metadata = parse_folder_metadata(item) if is_folder else parse_file_metadata(item)
                        
                        if is_folder and depth > 0:
                            item_metadata['contents'] = parse_folder_contents(
                                service, item['id'], depth - 1, include_team_drives)
                        
                        contents.append(item_metadata)
                    except Exception as item_error:
                        print(f"Error processing item {item.get('name', 'unknown')}: {str(item_error)}")
                        continue
                
                page_token = response.get('nextPageToken')
                if not page_token:
                    break
                    
            except Exception as page_error:
                print(f"Error fetching page: {str(page_error)}")
                break
        
        return contents
        
    except Exception as e:
        print(f"Error parsing folder contents: {str(e)}")
        return []

def format_folder_structure(contents: List[Dict], level: int = 0, include_metadata: bool = False) -> str:
    """Format folder structure as a readable string with optional metadata.
    
    Args:
        contents: List of file/folder metadata dictionaries
        level: Current indentation level (default: 0)
        include_metadata: Whether to include additional metadata like dates and sharing info (default: False)
    
    Returns:
        Formatted string representation of the folder structure
    """
    result = []
    indent = "  " * level
    
    for item in contents:
        try:
            is_folder = item['mimeType'] == 'application/vnd.google-apps.folder'
            name = item['name']
            size = int(item.get('size', 0))
            
            # Format size
            if size < 1024:
                size_str = f"{size} B"
            elif size < 1024 * 1024:
                size_str = f"{size/1024:.1f} KB"
            else:
                size_str = f"{size/(1024*1024):.1f} MB"
            
            # Format metadata if requested
            metadata = ""
            if include_metadata:
                modified = datetime.fromisoformat(item['modifiedTime'].replace('Z', '+00:00'))
                shared = "🔗" if item.get('shared', False) else ""
                metadata = f" | {modified.strftime('%Y-%m-%d %H:%M')} {shared}"
            
            # Add item to result
            if is_folder:
                result.append(f"{indent}📁 {name}/{metadata}")
                if 'contents' in item:
                    result.append(format_folder_structure(item['contents'], level + 1, include_metadata))
            else:
                result.append(f"{indent}📄 {name} ({size_str}){metadata}")
                
        except Exception as e:
            print(f"Error formatting item: {str(e)}")
            continue
    
    return "\n".join(result)

def get_file_path(service: Any, file_id: str) -> str:
    """Get the full path of a file in Google Drive.
    
    Args:
        service: Google Drive service instance
        file_id: ID of the file
    
    Returns:
        Full path of the file from root
    """
    try:
        path_parts = []
        current_id = file_id
        
        while current_id:
            try:
                file = service.files().get(
                    fileId=current_id,
                    fields='name,parents'
                ).execute()
                
                path_parts.insert(0, file.get('name', ''))
                parents = file.get('parents', [])
                current_id = parents[0] if parents else None
                
            except Exception as e:
                print(f"Error getting file info: {str(e)}")
                break
        
        return os.path.join(*path_parts) if path_parts else ''
        
    except Exception as e:
        print(f"Error getting file path: {str(e)}")
        return ''
