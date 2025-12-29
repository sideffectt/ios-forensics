"""Export utilities for parsed data."""

from __future__ import annotations
import json
import csv
from pathlib import Path
from typing import List, Dict, Any


def to_json(data: List[Dict], path: str, indent: int = 2) -> None:
    """Export data to JSON file."""
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=indent, default=str)


def to_csv(data: List[Dict], path: str) -> None:
    """Export data to CSV file."""
    if not data:
        return
    
    with open(path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)


def to_html(data: List[Dict], path: str, title: str = "Report") -> None:
    """Export data to HTML table."""
    if not data:
        return
    
    html = f"<!DOCTYPE html><html><head><title>{title}</title>"
    html += "<style>table{border-collapse:collapse;width:100%}"
    html += "th,td{border:1px solid #ddd;padding:8px;text-align:left}"
    html += "th{background:#4a4a4a;color:white}</style></head><body>"
    html += f"<h1>{title}</h1><table><tr>"
    
    for key in data[0].keys():
        html += f"<th>{key}</th>"
    html += "</tr>"
    
    for row in data:
        html += "<tr>"
        for val in row.values():
            html += f"<td>{val}</td>"
        html += "</tr>"
    
    html += "</table></body></html>"
    
    with open(path, 'w', encoding='utf-8') as f:
        f.write(html)
