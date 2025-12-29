"""Call history parser (CallHistory.storedata)."""

from __future__ import annotations
from typing import List, Dict, Any

from .base import BaseParser
from ..utils import cocoa_to_datetime, format_ts


class CallHistoryParser(BaseParser):
    """
    Parser for iOS call history.
    
    Path: /private/var/mobile/Library/CallHistoryDB/CallHistory.storedata
    """
    
    CALL_TYPES = {
        1: 'incoming',
        2: 'outgoing',
        3: 'missed',
        4: 'blocked',
        5: 'incoming_facetime',
        6: 'outgoing_facetime',
        7: 'missed_facetime'
    }
    
    def parse(self, limit: int | None = None) -> List[Dict[str, Any]]:
        """Extract call records."""
        query = """
            SELECT 
                Z_PK,
                ZADDRESS,
                ZDATE,
                ZDURATION,
                ZCALLTYPE,
                ZANSWERED,
                ZORIGINATED,
                ZFACE_TIME_DATA
            FROM ZCALLRECORD
            ORDER BY ZDATE DESC
        """
        
        if limit:
            query += f" LIMIT {limit}"
        
        self.cursor.execute(query)
        self._data = []
        
        for row in self.cursor.fetchall():
            call_type = self.CALL_TYPES.get(row['ZCALLTYPE'], 'unknown')
            duration = row['ZDURATION'] or 0
            
            self._data.append({
                'id': row['Z_PK'],
                'number': row['ZADDRESS'],
                'date': format_ts(cocoa_to_datetime(row['ZDATE'])),
                'duration': int(duration),
                'duration_fmt': f"{int(duration//60)}:{int(duration%60):02d}",
                'type': call_type,
                'answered': bool(row['ZANSWERED']),
                'outgoing': bool(row['ZORIGINATED']),
                'facetime': row['ZFACE_TIME_DATA'] is not None
            })
        
        return self._data
    
    def stats(self) -> Dict[str, Any]:
        """Get call statistics."""
        query = """
            SELECT 
                ZCALLTYPE,
                COUNT(*) AS cnt,
                SUM(ZDURATION) AS total_dur,
                AVG(ZDURATION) AS avg_dur
            FROM ZCALLRECORD
            GROUP BY ZCALLTYPE
        """
        
        self.cursor.execute(query)
        results = {}
        
        for row in self.cursor.fetchall():
            call_type = self.CALL_TYPES.get(row['ZCALLTYPE'], 'unknown')
            results[call_type] = {
                'count': row['cnt'],
                'total_minutes': round((row['total_dur'] or 0) / 60, 1),
                'avg_seconds': round(row['avg_dur'] or 0, 1)
            }
        
        return results
    
    def by_contact(self) -> List[Dict[str, Any]]:
        """Get call summary grouped by contact."""
        query = """
            SELECT 
                ZADDRESS,
                COUNT(*) AS total,
                SUM(ZDURATION) AS total_dur,
                MAX(ZDATE) AS last_call
            FROM ZCALLRECORD
            WHERE ZADDRESS IS NOT NULL
            GROUP BY ZADDRESS
            ORDER BY total DESC
        """
        
        self.cursor.execute(query)
        results = []
        
        for row in self.cursor.fetchall():
            results.append({
                'number': row['ZADDRESS'],
                'total_calls': row['total'],
                'total_minutes': round((row['total_dur'] or 0) / 60, 1),
                'last_call': format_ts(cocoa_to_datetime(row['last_call']))
            })
        
        return results
