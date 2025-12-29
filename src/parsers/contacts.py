"""Contacts database parser (AddressBook.sqlitedb)."""

from __future__ import annotations
from typing import List, Dict, Any

from .base import BaseParser
from ..utils import cocoa_to_datetime, format_ts


class ContactsParser(BaseParser):
    """
    Parser for iOS contacts database.
    
    Path: /private/var/mobile/Library/AddressBook/AddressBook.sqlitedb
    """
    
    def parse(self, limit: int | None = None) -> List[Dict[str, Any]]:
        """Extract contacts."""
        query = """
            SELECT 
                p.ROWID,
                p.First,
                p.Last,
                p.Organization,
                p.Note,
                p.CreationDate,
                p.ModificationDate
            FROM ABPerson p
            ORDER BY p.Last, p.First
        """
        
        if limit:
            query += f" LIMIT {limit}"
        
        self.cursor.execute(query)
        self._data = []
        
        for row in self.cursor.fetchall():
            self._data.append({
                'id': row['ROWID'],
                'first_name': row['First'],
                'last_name': row['Last'],
                'organization': row['Organization'],
                'note': row['Note'],
                'created': format_ts(cocoa_to_datetime(row['CreationDate'])),
                'modified': format_ts(cocoa_to_datetime(row['ModificationDate']))
            })
        
        return self._data
    
    def phones(self) -> List[Dict[str, Any]]:
        """Get all phone numbers with contact info."""
        query = """
            SELECT 
                p.ROWID,
                p.First,
                p.Last,
                mv.value AS phone,
                mv.label
            FROM ABPerson p
            JOIN ABMultiValue mv ON p.ROWID = mv.record_id
            WHERE mv.property = 3
            ORDER BY p.Last, p.First
        """
        
        self.cursor.execute(query)
        results = []
        
        for row in self.cursor.fetchall():
            name = ' '.join(filter(None, [row['First'], row['Last']]))
            results.append({
                'id': row['ROWID'],
                'name': name,
                'phone': row['phone'],
                'label': row['label']
            })
        
        return results
    
    def emails(self) -> List[Dict[str, Any]]:
        """Get all email addresses with contact info."""
        query = """
            SELECT 
                p.ROWID,
                p.First,
                p.Last,
                mv.value AS email,
                mv.label
            FROM ABPerson p
            JOIN ABMultiValue mv ON p.ROWID = mv.record_id
            WHERE mv.property = 4
            ORDER BY p.Last, p.First
        """
        
        self.cursor.execute(query)
        results = []
        
        for row in self.cursor.fetchall():
            name = ' '.join(filter(None, [row['First'], row['Last']]))
            results.append({
                'id': row['ROWID'],
                'name': name,
                'email': row['email'],
                'label': row['label']
            })
        
        return results
    
    def search(self, keyword: str) -> List[Dict[str, Any]]:
        """Search contacts by name."""
        query = """
            SELECT 
                p.ROWID,
                p.First,
                p.Last,
                p.Organization
            FROM ABPerson p
            WHERE p.First LIKE ? OR p.Last LIKE ? OR p.Organization LIKE ?
            ORDER BY p.Last, p.First
        """
        
        pattern = f'%{keyword}%'
        self.cursor.execute(query, (pattern, pattern, pattern))
        results = []
        
        for row in self.cursor.fetchall():
            name = ' '.join(filter(None, [row['First'], row['Last']]))
            results.append({
                'id': row['ROWID'],
                'name': name,
                'organization': row['Organization']
            })
        
        return results
