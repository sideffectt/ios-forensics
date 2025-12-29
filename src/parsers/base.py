"""Base parser class for SQLite databases."""

from __future__ import annotations
import sqlite3
from pathlib import Path
from typing import List, Dict, Any
from abc import ABC, abstractmethod

from ..utils import to_json, to_csv


class BaseParser(ABC):
    """Abstract base for all database parsers."""
    
    def __init__(self, db_path: str):
        self.db_path = Path(db_path)
        self._conn: sqlite3.Connection | None = None
        self._cursor: sqlite3.Cursor | None = None
        self._data: List[Dict[str, Any]] = []
        
        if not self.db_path.exists():
            raise FileNotFoundError(f"Database not found: {db_path}")
    
    @property
    def cursor(self) -> sqlite3.Cursor:
        """Get cursor, raise if not connected."""
        if self._cursor is None:
            raise RuntimeError("Not connected. Use 'with' statement or call connect()")
        return self._cursor
    
    @property
    def conn(self) -> sqlite3.Connection:
        """Get connection, raise if not connected."""
        if self._conn is None:
            raise RuntimeError("Not connected. Use 'with' statement or call connect()")
        return self._conn
    
    def connect(self) -> None:
        """Open database connection."""
        self._conn = sqlite3.connect(str(self.db_path))
        self._conn.row_factory = sqlite3.Row
        self._cursor = self._conn.cursor()
    
    def close(self) -> None:
        """Close database connection."""
        if self._conn:
            self._conn.close()
            self._conn = None
            self._cursor = None
    
    def __enter__(self):
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
    
    @abstractmethod
    def parse(self, limit: int | None = None) -> List[Dict[str, Any]]:
        """Parse database and return records."""
        pass
    
    def tables(self) -> List[str]:
        """List all tables in database."""
        self.cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        )
        return [r[0] for r in self.cursor.fetchall()]
    
    def schema(self, table: str) -> List[Dict[str, Any]]:
        """Get table schema."""
        self.cursor.execute(f"PRAGMA table_info({table})")
        return [
            {'name': r[1], 'type': r[2], 'pk': bool(r[5])}
            for r in self.cursor.fetchall()
        ]
    
    def count(self, table: str) -> int:
        """Count rows in table."""
        self.cursor.execute(f"SELECT COUNT(*) FROM {table}")
        return self.cursor.fetchone()[0]
    
    def export_json(self, path: str) -> None:
        """Export parsed data to JSON."""
        to_json(self._data, path)
    
    def export_csv(self, path: str) -> None:
        """Export parsed data to CSV."""
        to_csv(self._data, path)
    
    @property
    def data(self) -> List[Dict[str, Any]]:
        """Get parsed data."""
        return self._data
