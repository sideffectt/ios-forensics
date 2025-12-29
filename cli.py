#!/usr/bin/env python3
"""Command-line interface for iOS Forensics Toolkit."""

import argparse
import sys
from pathlib import Path

from src.parsers import (
    SMSParser,
    WhatsAppParser,
    SafariParser,
    CallHistoryParser,
    KnowledgeCParser,
    ContactsParser,
    PlistParser
)


PARSERS = {
    'sms': SMSParser,
    'whatsapp': WhatsAppParser,
    'safari': SafariParser,
    'calls': CallHistoryParser,
    'knowledgec': KnowledgeCParser,
    'contacts': ContactsParser,
    'plist': PlistParser
}


def detect_type(path: str) -> str:
    """Auto-detect database type from filename."""
    name = Path(path).name.lower()
    
    if name.endswith('.plist'):
        return 'plist'
    if 'sms' in name:
        return 'sms'
    if 'chatstorage' in name:
        return 'whatsapp'
    if 'history' in name:
        return 'safari'
    if 'callhistory' in name:
        return 'calls'
    if 'knowledgec' in name:
        return 'knowledgec'
    if 'addressbook' in name:
        return 'contacts'
    
    return None


def main():
    parser = argparse.ArgumentParser(
        description='iOS Forensics Toolkit',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('file', help='Input file path')
    parser.add_argument('-t', '--type', choices=list(PARSERS.keys()),
                       help='Parser type (auto-detected if not set)')
    parser.add_argument('-o', '--output', help='Output file path')
    parser.add_argument('-f', '--format', choices=['json', 'csv', 'html'],
                       default='json', help='Output format')
    parser.add_argument('-l', '--limit', type=int, help='Limit records')
    parser.add_argument('--tables', action='store_true', help='List tables only')
    parser.add_argument('--schema', help='Show schema for table')
    parser.add_argument('--stats', action='store_true', help='Show statistics')
    
    args = parser.parse_args()
    
    # Detect or use provided type
    parser_type = args.type or detect_type(args.file)
    if not parser_type:
        print(f"Error: Cannot detect file type. Use -t option.")
        sys.exit(1)
    
    parser_cls = PARSERS[parser_type]
    
    try:
        # Handle plist separately
        if parser_type == 'plist':
            p = PlistParser(args.file)
            data = p.parse()
            
            if args.output:
                p.export_json(args.output)
                print(f"Exported to {args.output}")
            else:
                p.print_structure()
            return
        
        # Handle database parsers
        with parser_cls(args.file) as p:
            if args.tables:
                for t in p.tables():
                    print(t)
                return
            
            if args.schema:
                for col in p.schema(args.schema):
                    print(f"{col['name']}: {col['type']}")
                return
            
            if args.stats and hasattr(p, 'stats'):
                import json
                print(json.dumps(p.stats(), indent=2))
                return
            
            # Parse data
            data = p.parse(limit=args.limit)
            print(f"Parsed {len(data)} records")
            
            # Export if output specified
            if args.output:
                if args.format == 'json':
                    p.export_json(args.output)
                elif args.format == 'csv':
                    p.export_csv(args.output)
                print(f"Exported to {args.output}")
    
    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
