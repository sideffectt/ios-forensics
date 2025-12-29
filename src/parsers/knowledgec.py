"""KnowledgeC system activity parser (knowledgeC.db)."""

from __future__ import annotations
from typing import List, Dict, Any

from .base import BaseParser
from ..utils import cocoa_to_datetime, format_ts


class KnowledgeCParser(BaseParser):
    """
    Parser for iOS system activity database.
    
    Path: /private/var/mobile/Library/CoreDuet/Knowledge/knowledgeC.db
    
    Contains app usage, device states, locations, and user activities.
    """
    
    def parse(self, limit: int | None = None) -> List[Dict[str, Any]]:
        """Extract activity events."""
        query = """
            SELECT 
                o.Z_PK,
                o.ZSTREAMNAME,
                o.ZCREATIONDATE,
                o.ZSTARTDATE,
                o.ZENDDATE,
                o.ZVALUESTRING,
                s.ZBUNDLEID
            FROM ZOBJECT o
            LEFT JOIN ZSOURCE s ON o.ZSOURCE = s.Z_PK
            ORDER BY o.ZCREATIONDATE DESC
        """
        
        if limit:
            query += f" LIMIT {limit}"
        
        self.cursor.execute(query)
        self._data = []
        
        for row in self.cursor.fetchall():
            start = cocoa_to_datetime(row['ZSTARTDATE'])
            end = cocoa_to_datetime(row['ZENDDATE'])
            duration = None
            
            if start and end:
                duration = int((end - start).total_seconds())
            
            self._data.append({
                'id': row['Z_PK'],
                'stream': row['ZSTREAMNAME'],
                'created': format_ts(cocoa_to_datetime(row['ZCREATIONDATE'])),
                'start': format_ts(start),
                'end': format_ts(end),
                'duration_sec': duration,
                'bundle_id': row['ZBUNDLEID'],
                'value': row['ZVALUESTRING']
            })
        
        return self._data
    
    def app_usage(self) -> List[Dict[str, Any]]:
        """Get app usage statistics."""
        query = """
            SELECT 
                s.ZBUNDLEID,
                COUNT(*) AS events,
                SUM(o.ZENDDATE - o.ZSTARTDATE) AS total_sec
            FROM ZOBJECT o
            JOIN ZSOURCE s ON o.ZSOURCE = s.Z_PK
            WHERE o.ZSTREAMNAME LIKE '%InFocus%'
                AND o.ZENDDATE IS NOT NULL 
                AND o.ZSTARTDATE IS NOT NULL
                AND s.ZBUNDLEID IS NOT NULL
            GROUP BY s.ZBUNDLEID
            ORDER BY total_sec DESC
        """
        
        self.cursor.execute(query)
        results = []
        
        for row in self.cursor.fetchall():
            total = row['total_sec'] or 0
            results.append({
                'bundle_id': row['ZBUNDLEID'],
                'events': row['events'],
                'total_hours': round(total / 3600, 2)
            })
        
        return results
    
    def streams(self) -> List[Dict[str, Any]]:
        """Get available data streams."""
        query = """
            SELECT 
                ZSTREAMNAME,
                COUNT(*) AS cnt
            FROM ZOBJECT
            WHERE ZSTREAMNAME IS NOT NULL
            GROUP BY ZSTREAMNAME
            ORDER BY cnt DESC
        """
        
        self.cursor.execute(query)
        return [
            {'stream': row['ZSTREAMNAME'], 'count': row['cnt']}
            for row in self.cursor.fetchall()
        ]
    
    def device_states(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get device lock/unlock events."""
        query = """
            SELECT 
                o.Z_PK,
                o.ZSTREAMNAME,
                o.ZCREATIONDATE,
                o.ZVALUESTRING
            FROM ZOBJECT o
            WHERE o.ZSTREAMNAME LIKE '%DeviceLock%'
                OR o.ZSTREAMNAME LIKE '%Display%'
            ORDER BY o.ZCREATIONDATE DESC
            LIMIT ?
        """
        
        self.cursor.execute(query, (limit,))
        results = []
        
        for row in self.cursor.fetchall():
            results.append({
                'id': row['Z_PK'],
                'stream': row['ZSTREAMNAME'],
                'date': format_ts(cocoa_to_datetime(row['ZCREATIONDATE'])),
                'value': row['ZVALUESTRING']
            })
        
        return results
