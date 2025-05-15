import os
import logging
from typing import List, Dict, Any, Tuple
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def is_pdf_file(filename: str) -> bool:
    """
    Check if a file is a PDF based on its extension.
    
    Args:
        filename: Name of the file to check
        
    Returns:
        Boolean indicating if the file has a PDF extension
    """
    return filename.lower().endswith('.pdf')

def validate_file_exists(file_path: str) -> Tuple[bool, str]:
    """
    Validate that a file exists and is accessible.
    
    Args:
        file_path: Path to the file to validate
        
    Returns:
        Tuple (valid, message) where:
          - valid: Boolean indicating if the file is valid
          - message: Error message if not valid, empty string otherwise
    """
    if not os.path.exists(file_path):
        return False, f"File not found: {file_path}"
    
    if not os.path.isfile(file_path):
        return False, f"Not a file: {file_path}"
    
    if not os.access(file_path, os.R_OK):
        return False, f"File is not readable: {file_path}"
    
    if not is_pdf_file(file_path):
        return False, f"Not a PDF file: {file_path}"
    
    return True, ""

def format_datetime(dt: datetime) -> str:
    """
    Format a datetime object as a readable string.
    
    Args:
        dt: Datetime object to format
        
    Returns:
        Formatted datetime string
    """
    if dt:
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    return "Unknown"

def format_metadata_for_display(metadata: Dict[str, Any]) -> Dict[str, str]:
    """
    Format metadata values for display.
    
    Args:
        metadata: Dictionary containing metadata
        
    Returns:
        Dictionary with formatted metadata values
    """
    formatted = {}
    
    for key, value in metadata.items():
        if isinstance(value, datetime):
            formatted[key] = format_datetime(value)
        elif value is None:
            formatted[key] = "Not available"
        else:
            formatted[key] = str(value)
    
    return formatted

def get_temp_upload_path() -> str:
    """
    Get a temporary directory path for uploaded files.
    
    Returns:
        Path to temporary upload directory
    """
    # Create a temporary directory if it doesn't exist
    temp_dir = os.path.join(os.getcwd(), 'temp_uploads')
    os.makedirs(temp_dir, exist_ok=True)
    return temp_dir

def clean_temp_files(max_age_minutes: int = 30) -> None:
    """
    Clean temporary files older than a certain age.
    
    Args:
        max_age_minutes: Maximum age in minutes before files are deleted
    """
    temp_dir = get_temp_upload_path()
    now = datetime.now()
    
    try:
        for filename in os.listdir(temp_dir):
            file_path = os.path.join(temp_dir, filename)
            if os.path.isfile(file_path):
                # Check file age
                file_modified = datetime.fromtimestamp(os.path.getmtime(file_path))
                age_minutes = (now - file_modified).total_seconds() / 60
                
                if age_minutes > max_age_minutes:
                    try:
                        os.remove(file_path)
                        logger.debug(f"Removed old temporary file: {filename}")
                    except Exception as e:
                        logger.warning(f"Failed to remove temporary file {filename}: {e}")
    except Exception as e:
        logger.error(f"Error cleaning temporary files: {e}")

def get_severity_class(is_suspicious: bool) -> str:
    """
    Get Bootstrap severity class based on suspicious status.
    
    Args:
        is_suspicious: Boolean indicating if the document is suspicious
        
    Returns:
        Bootstrap CSS class name
    """
    return "danger" if is_suspicious else "success"

def filter_issues_by_category(issues: List[str]) -> Dict[str, List[str]]:
    """
    Filter issues into categories for better visualization.
    
    Args:
        issues: List of issue strings
        
    Returns:
        Dictionary of categorized issues
    """
    categories = {
        'date_issues': [],
        'software_issues': [],
        'metadata_issues': [],
        'integrity_issues': []
    }
    
    for issue in issues:
        issue_lower = issue.lower()
        
        if any(keyword in issue_lower for keyword in ['date', 'modified', 'creation']):
            categories['date_issues'].append(issue)
        elif any(keyword in issue_lower for keyword in ['software', 'producer', 'creator']):
            categories['software_issues'].append(issue)
        elif any(keyword in issue_lower for keyword in ['metadata', 'field', 'missing']):
            categories['metadata_issues'].append(issue)
        else:
            categories['integrity_issues'].append(issue)
    
    return categories
