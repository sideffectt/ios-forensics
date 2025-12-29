"""SMS/iMessage database parser (sms.db)."""

from __future__ import annotations
from typing import List, Dict, Any

from .base import BaseParser
from ..utils import cocoa_to_datetime, format_ts


class SMSParser(BaseParser):
    """
    Parser for iOS SMS database.
    
    Path: /private/var/mobile/Library/SMS/sms.db
    """
    
    def parse(self, limit: int | None = None) -> List[Dict[str, Any]]:
        """Extract messages from database."""
        query = """
            SELECT 
                m.ROWID,
                m.text,
                m.date,
                m.date_read,
                m.date_delivered,
                m.is_from_me,
                m.is_read,
                m.is_sent,
                h.id AS handle,
                m.service,
                m.cache_has_attachments
            FROM message m
            LEFT JOIN handle h ON m.handle_id = h.ROWID
            ORDER BY m.date DESC
        """
        
        if limit:
            query += f" LIMIT {limit}"
        
        self.cursor.execute(query)
        self._data = []
        
        for row in self.cursor.fetchall():
            ts = row['date'] / 1e9 if row['date'] else None
            ts_read = row['date_read'] / 1e9 if row['date_read'] else None
            
            self._data.append({
                'id': row['ROWID'],
                'text': row['text'],
                'date': format_ts(cocoa_to_datetime(ts)),
                'date_read': format_ts(cocoa_to_datetime(ts_read)),
                'is_from_me': bool(row['is_from_me']),
                'is_read': bool(row['is_read']),
                'handle': row['handle'],
                'service': row['service'],
                'has_attachment': bool(row['cache_has_attachments'])
            })
        
        return self._data
    
    def conversations(self) -> List[Dict[str, Any]]:
        """Get conversation summary per contact."""
        query = """
            SELECT 
                h.id AS contact,
                COUNT(*) AS total,
                SUM(CASE WHEN m.is_from_me = 1 THEN 1 ELSE 0 END) AS sent,
                SUM(CASE WHEN m.is_from_me = 0 THEN 1 ELSE 0 END) AS received,
                MAX(m.date) AS last_date
            FROM message m
            JOIN handle h ON m.handle_id = h.ROWID
            GROUP BY h.id
            ORDER BY last_date DESC
        """
        
        self.cursor.execute(query)
        results = []
        
        for row in self.cursor.fetchall():
            ts = row['last_date'] / 1e9 if row['last_date'] else None
            results.append({
                'contact': row['contact'],
                'total': row['total'],
                'sent': row['sent'],
                'received': row['received'],
                'last_message': format_ts(cocoa_to_datetime(ts))
            })
        
        return results
    
    def attachments(self, limit: int | None = 100) -> List[Dict[str, Any]]:
        """Get message attachments."""
        query = """
            SELECT 
                a.ROWID,
                a.filename,
                a.mime_type,
                a.total_bytes,
                a.created_date
            FROM attachment a
            ORDER BY a.created_date DESC
        """
        
        if limit:
            query += f" LIMIT {limit}"
        
        self.cursor.execute(query)
        results = []
        
        for row in self.cursor.fetchall():
            ts = row['created_date'] / 1e9 if row['created_date'] else None
            results.append({
                'id': row['ROWID'],
                'filename': row['filename'],
                'mime_type': row['mime_type'],
                'size_bytes': row['total_bytes'],
                'created': format_ts(cocoa_to_datetime(ts))
            })
        
        return results
