"""Safari browser history parser (History.db)."""

from __future__ import annotations
from typing import List, Dict, Any

from .base import BaseParser
from ..utils import cocoa_to_datetime, format_ts


class SafariParser(BaseParser):
    """
    Parser for Safari browsing history.
    
    Path: /private/var/mobile/Library/Safari/History.db
    """
    
    def parse(self, limit: int | None = None) -> List[Dict[str, Any]]:
        """Extract browsing history."""
        query = """
            SELECT 
                hi.id,
                hi.url,
                hv.title,
                hv.visit_time,
                hi.visit_count
            FROM history_items hi
            LEFT JOIN history_visits hv ON hi.id = hv.history_item
            ORDER BY hv.visit_time DESC
        """
        
        if limit:
            query += f" LIMIT {limit}"
        
        self.cursor.execute(query)
        self._data = []
        
        for row in self.cursor.fetchall():
            self._data.append({
                'id': row['id'],
                'url': row['url'],
                'title': row['title'],
                'visit_time': format_ts(cocoa_to_datetime(row['visit_time'])),
                'visit_count': row['visit_count']
            })
        
        return self._data
    
    def top_sites(self, n: int = 20) -> List[Dict[str, Any]]:
        """Get most visited sites."""
        query = """
            SELECT 
                url,
                visit_count,
                MAX(visit_time) AS last_visit
            FROM history_items hi
            LEFT JOIN history_visits hv ON hi.id = hv.history_item
            GROUP BY url
            ORDER BY visit_count DESC
            LIMIT ?
        """
        
        self.cursor.execute(query, (n,))
        results = []
        
        for row in self.cursor.fetchall():
            results.append({
                'url': row['url'],
                'visits': row['visit_count'],
                'last_visit': format_ts(cocoa_to_datetime(row['last_visit']))
            })
        
        return results
    
    def search_url(self, keyword: str) -> List[Dict[str, Any]]:
        """Search history by URL keyword."""
        query = """
            SELECT 
                hi.id,
                hi.url,
                hv.title,
                hv.visit_time,
                hi.visit_count
            FROM history_items hi
            LEFT JOIN history_visits hv ON hi.id = hv.history_item
            WHERE hi.url LIKE ?
            ORDER BY hv.visit_time DESC
        """
        
        self.cursor.execute(query, (f'%{keyword}%',))
        results = []
        
        for row in self.cursor.fetchall():
            results.append({
                'id': row['id'],
                'url': row['url'],
                'title': row['title'],
                'visit_time': format_ts(cocoa_to_datetime(row['visit_time'])),
                'visit_count': row['visit_count']
            })
        
        return results
