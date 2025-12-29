"""WhatsApp ChatStorage.sqlite parser."""

from __future__ import annotations
from typing import List, Dict, Any

from .base import BaseParser
from ..utils import cocoa_to_datetime, format_ts


class WhatsAppParser(BaseParser):
    """
    Parser for WhatsApp message database.
    
    Path: /private/var/mobile/Containers/Data/Application/[UUID]/Documents/ChatStorage.sqlite
    """
    
    MSG_TYPES = {
        0: 'text',
        1: 'image',
        2: 'video',
        3: 'audio',
        4: 'contact',
        5: 'location',
        6: 'system',
        8: 'document',
        15: 'sticker'
    }
    
    def parse(self, limit: int | None = None) -> List[Dict[str, Any]]:
        """Extract messages from database."""
        query = """
            SELECT 
                m.Z_PK,
                m.ZTEXT,
                m.ZMESSAGEDATE,
                m.ZISFROMME,
                m.ZMESSAGETYPE,
                m.ZSTARRED,
                c.ZPARTNERNAME,
                c.ZCONTACTJID
            FROM ZWAMESSAGE m
            LEFT JOIN ZWACHATSESSION c ON m.ZCHATSESSION = c.Z_PK
            ORDER BY m.ZMESSAGEDATE DESC
        """
        
        if limit:
            query += f" LIMIT {limit}"
        
        self.cursor.execute(query)
        self._data = []
        
        for row in self.cursor.fetchall():
            msg_type = self.MSG_TYPES.get(row['ZMESSAGETYPE'], 'unknown')
            
            self._data.append({
                'id': row['Z_PK'],
                'text': row['ZTEXT'],
                'date': format_ts(cocoa_to_datetime(row['ZMESSAGEDATE'])),
                'is_from_me': bool(row['ZISFROMME']),
                'type': msg_type,
                'starred': bool(row['ZSTARRED']),
                'contact_name': row['ZPARTNERNAME'],
                'contact_jid': row['ZCONTACTJID']
            })
        
        return self._data
    
    def chats(self) -> List[Dict[str, Any]]:
        """Get all chat sessions."""
        query = """
            SELECT 
                Z_PK,
                ZPARTNERNAME,
                ZCONTACTJID,
                ZLASTMESSAGEDATE,
                ZMESSAGECOUNTER
            FROM ZWACHATSESSION
            ORDER BY ZLASTMESSAGEDATE DESC
        """
        
        self.cursor.execute(query)
        results = []
        
        for row in self.cursor.fetchall():
            jid = row['ZCONTACTJID'] or ''
            is_group = jid.endswith('@g.us')
            
            results.append({
                'id': row['Z_PK'],
                'name': row['ZPARTNERNAME'],
                'jid': jid,
                'is_group': is_group,
                'message_count': row['ZMESSAGECOUNTER'],
                'last_message': format_ts(cocoa_to_datetime(row['ZLASTMESSAGEDATE']))
            })
        
        return results
    
    def media(self, limit: int | None = 100) -> List[Dict[str, Any]]:
        """Get media items."""
        query = """
            SELECT 
                Z_PK,
                ZMEDIALOCALPATH,
                ZVCARDSTRING,
                ZFILESIZE,
                ZLATITUDE,
                ZLONGITUDE
            FROM ZWAMEDIAITEM
            WHERE ZMEDIALOCALPATH IS NOT NULL
            ORDER BY Z_PK DESC
        """
        
        if limit:
            query += f" LIMIT {limit}"
        
        self.cursor.execute(query)
        results = []
        
        for row in self.cursor.fetchall():
            results.append({
                'id': row['Z_PK'],
                'path': row['ZMEDIALOCALPATH'],
                'size': row['ZFILESIZE'],
                'lat': row['ZLATITUDE'],
                'lon': row['ZLONGITUDE']
            })
        
        return results
