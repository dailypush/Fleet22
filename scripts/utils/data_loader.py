"""Standardized data loading utilities for Fleet22 scripts."""
import json
import os
import tempfile
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
    
    # Serialize before touching the destination, then atomically replace it.
    filepath.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8',
                                         dir=filepath.parent, prefix=f'.{filepath.name}.',
                                         suffix='.tmp', delete=False) as f:
            temporary = Path(f.name)
            json.dump(data, f, indent=indent, ensure_ascii=False)
            f.write('\n')
            f.flush()
            os.fsync(f.fileno())
        os.chmod(temporary, filepath.stat().st_mode & 0o777 if filepath.exists() else 0o644)
        os.replace(temporary, filepath)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
    
    logger.info(f"Saved {len(data) if isinstance(data, list) else 'data'} to {filepath.name}")
