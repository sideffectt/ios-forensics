# iOS Forensics Toolkit

Modular Python toolkit for parsing iOS device artifacts. Extracts data from SQLite databases and Property List files commonly found in iOS backups and file system extractions.

## Supported Artifacts

| Parser | Database | Description |
|--------|----------|-------------|
| `SMSParser` | sms.db | SMS and iMessage data |
| `WhatsAppParser` | ChatStorage.sqlite | WhatsApp messages and media |
| `SafariParser` | History.db | Browser history |
| `CallHistoryParser` | CallHistory.storedata | Call records |
| `KnowledgeCParser` | knowledgeC.db | System activity and app usage |
| `ContactsParser` | AddressBook.sqlitedb | Contact information |
| `PlistParser` | *.plist | Configuration files |

## Installation

```bash
git clone https://github.com/sideffectt/ios-forensics.git
cd ios-forensics
pip install -e .
```

## Usage

### Command Line

```bash
# Parse SMS database
python cli.py sms.db -o messages.json

# Parse with limit
python cli.py ChatStorage.sqlite -t whatsapp -l 100 -o output.csv -f csv

# List database tables
python cli.py sms.db --tables

# Show table schema
python cli.py sms.db --schema message

# Get call statistics
python cli.py CallHistory.storedata -t calls --stats
```

### Python API

```python
from src import SMSParser, WhatsAppParser, PlistParser

# Parse SMS
with SMSParser('sms.db') as parser:
    messages = parser.parse(limit=100)
    conversations = parser.conversations()
    parser.export_json('sms.json')

# Parse WhatsApp
with WhatsAppParser('ChatStorage.sqlite') as parser:
    messages = parser.parse()
    chats = parser.chats()

# Parse plist
plist = PlistParser('Info.plist')
data = plist.parse()
bundle_id = plist.get('CFBundleIdentifier')
plist.print_structure()
```

### Timestamp Conversion

```python
from src import cocoa_to_datetime, auto_convert

# Cocoa timestamp (since 2001-01-01)
dt = cocoa_to_datetime(700000000)

# Auto-detect format
dt = auto_convert(some_timestamp)
```

## Project Structure

```
ios-forensics/
├── src/
│   ├── parsers/
│   │   ├── base.py         # Base parser class
│   │   ├── sms.py          # SMS/iMessage parser
│   │   ├── whatsapp.py     # WhatsApp parser
│   │   ├── safari.py       # Safari history parser
│   │   ├── calls.py        # Call history parser
│   │   ├── knowledgec.py   # System activity parser
│   │   ├── contacts.py     # Contacts parser
│   │   └── plist.py        # Property list parser
│   └── utils/
│       ├── timestamp.py    # Timestamp converters
│       └── export.py       # Export functions
├── cli.py                  # Command-line interface
├── setup.py
└── README.md
```

## iOS Artifact Locations

| Artifact | Path |
|----------|------|
| SMS | `/private/var/mobile/Library/SMS/sms.db` |
| WhatsApp | `/private/var/mobile/Containers/Data/Application/[UUID]/Documents/ChatStorage.sqlite` |
| Safari | `/private/var/mobile/Library/Safari/History.db` |
| Calls | `/private/var/mobile/Library/CallHistoryDB/CallHistory.storedata` |
| KnowledgeC | `/private/var/mobile/Library/CoreDuet/Knowledge/knowledgeC.db` |
| Contacts | `/private/var/mobile/Library/AddressBook/AddressBook.sqlitedb` |

## Apple Timestamp Formats

| Format | Epoch | Used In |
|--------|-------|---------|
| Cocoa/CoreData | 2001-01-01 | Most iOS databases |
| Unix | 1970-01-01 | General purpose |
| WebKit | 1601-01-01 | Safari (microseconds) |
| Nanoseconds | 2001-01-01 | SMS database |

## Export Formats

- JSON (default)
- CSV
- HTML

## Requirements

- Python 3.7+
- No external dependencies (standard library only)

## License

MIT
