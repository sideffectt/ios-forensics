"""Apple Property List (plist) parser."""

from __future__ import annotations
import json
import plistlib
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List


class PlistParser:
    """Parser for binary and XML plist files."""
    
    def __init__(self, path: str):
        self.path = Path(path)
        self._data: Dict[str, Any] = {}
        
        if not self.path.exists():
            raise FileNotFoundError(f"Plist not found: {path}")
    
    def parse(self) -> Dict[str, Any]:
        """Parse plist file."""
        with open(self.path, 'rb') as f:
            self._data = plistlib.load(f)
        return self._data
    
    @property
    def data(self) -> Dict[str, Any]:
        """Get parsed data."""
        return self._data
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """
        Get nested value using dot notation.
        
        Example: get('root.child.value')
        """
        keys = key_path.split('.')
        current = self._data
        
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            elif isinstance(current, list):
                try:
                    current = current[int(key)]
                except (ValueError, IndexError):
                    return default
            else:
                return default
        
        return current
    
    def keys(self) -> List[str]:
        """Get top-level keys."""
        if isinstance(self._data, dict):
            return list(self._data.keys())
        return []
    
    def flatten(self, sep: str = '.') -> Dict[str, Any]:
        """Flatten nested plist to single-level dict."""
        result = {}
        
        def _flatten(obj, prefix=''):
            if isinstance(obj, dict):
                for k, v in obj.items():
                    new_key = f"{prefix}{sep}{k}" if prefix else k
                    _flatten(v, new_key)
            elif isinstance(obj, list):
                for i, v in enumerate(obj):
                    _flatten(v, f"{prefix}{sep}{i}")
            else:
                result[prefix] = obj
        
        _flatten(self._data)
        return result
    
    def to_serializable(self) -> Dict[str, Any]:
        """Convert to JSON-serializable dict."""
        def _convert(obj):
            if isinstance(obj, dict):
                return {k: _convert(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [_convert(v) for v in obj]
            elif isinstance(obj, datetime):
                return obj.isoformat()
            elif isinstance(obj, bytes):
                return obj.hex()
            return obj
        
        return _convert(self._data)
    
    def export_json(self, path: str) -> None:
        """Export plist as JSON."""
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(self.to_serializable(), f, ensure_ascii=False, indent=2)
    
    def print_structure(self, max_depth: int = 3) -> None:
        """Print plist structure."""
        def _print(obj, depth=0, prefix=''):
            indent = '  ' * depth
            
            if depth > max_depth:
                print(f"{indent}...")
                return
            
            if isinstance(obj, dict):
                for k, v in obj.items():
                    if isinstance(v, (dict, list)):
                        print(f"{indent}{k}: ({type(v).__name__})")
                        _print(v, depth + 1)
                    else:
                        val = str(v)[:40]
                        if len(str(v)) > 40:
                            val += '...'
                        print(f"{indent}{k}: {val}")
            elif isinstance(obj, list):
                print(f"{indent}[{len(obj)} items]")
                if obj:
                    _print(obj[0], depth + 1)
        
        _print(self._data)
