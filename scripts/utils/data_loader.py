"""Standardized data loading utilities for Fleet22 scripts."""
import json
from pathlib import Path
from typing import List, Dict, Any
from .logger import setup_logger

logger = setup_logger(__name__)

def load_json(filepath: Path) -> List[Dict[str, Any]]:
    """
    Load JSON data from a file.
    
    Args:
        filepath: Path to JSON file
    
    Returns:
        Parsed JSON data as list of dictionaries
    
    Raises:
        FileNotFoundError: If file doesn't exist
        json.JSONDecodeError: If file isn't valid JSON
    """
    if not filepath.exists():
        raise FileNotFoundError(f"File not found: {filepath}")
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        logger.info(f"Loaded {len(data) if isinstance(data, list) else 'data'} from {filepath.name}")
        return data
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in {filepath}: {e}")
        raise

def save_json(data: Any, filepath: Path, indent: int = 4, 
              create_backup: bool = True) -> None:
    """
    Save data as JSON to a file.
    
    Args:
        data: Data to save
        filepath: Path to save to
        indent: JSON indentation (default: 4)
        create_backup: Whether to create backup of existing file
    """
    # Create backup if file exists
    if create_backup and filepath.exists():
        from .path_utils import get_backup_path
        backup_path = get_backup_path(filepath)
        import shutil
        shutil.copy2(filepath, backup_path)
        logger.info(f"Created backup: {backup_path.name}")
    
    # Save new data
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=indent, ensure_ascii=False)
    
    logger.info(f"Saved {len(data) if isinstance(data, list) else 'data'} to {filepath.name}")
