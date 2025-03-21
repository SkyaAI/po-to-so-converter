#!/usr/bin/env python3
"""
Improved Data Extraction Module for Purchase Order to Sales Order Conversion System

This module extracts relevant information from parsed documents with enhanced pattern matching:
- Client information (name, phone, address, email)
- PO details (number, creation date, due date)
- Order total and comments
- Line items (item code, description, quantity, unit price, total price)
"""

import re
import pandas as pd
from datetime import datetime
import json

class DataExtractor:
    """Extract data from parsed documents"""
    
    def __init__(self):
        self.parsed_data = None
        self.extracted_data = {
            'client_info': {},
            'po_details': {},
            'ship_to': {},
            'line_items': []
        }
    
    def extract(self, parsed_data):
        """Extract data from parsed document"""
        self.parsed_data = parsed_data
        self.extracted_data = {
            'client_info': {},
            'po_details': {},
            'ship_to': {},
            'line_items': []
        }
        
        # Extract data from text
        self._extract_from_text(parsed_data['text'])
        
        # Extract data from tables
        self._extract_from_tables(parsed_data['tables'])
        
        # Validate and clean extracted data
        self._validate_and_clean()
        
        return self.extracted_data
    
    def _extract_from_text(self, text):
        """Extract data from text content"""
        # Extract client information
        self._extract_client_info(text)
        
        # Extract PO details
        self._extract_po_details(text)
        
        # Extract ship to information
        self._extract_ship_to(text)
        
        # Extract order total
        self._extract_order_total(text)
        
        # Extract comments
        self._extract_comments(text)
    
    def _extract_client_info(self, text):
        """Extract client information from text"""
        # Extract client name
        client_name_patterns = [
            r'(?:Client|Customer|Bill To|Sold To|Company)(?:\s*Name)?(?:\s*:)?\s*([A-Za-z0-9\s&.,]+)(?:\n|$)',
            r'(?:TO|BILL TO|SOLD TO):\s*([A-Za-z0-9\s&.,]+)(?:\n|$)',
            r'^([A-Za-z0-9\s&.,]+)(?:\n)(?:\d{1,3}[^@]*?)(?:\n|$)'  # First line followed by address
        ]
        
        for pattern in client_name_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                self.extracted_data['client_info']['name'] = match.group(1).strip()
                break
        
        # Look for company name in first few lines if not found
        if 'name' not in self.extracted_data['client_info'] or not self.extracted_data['client_info']['name']:
            lines = text.split('\n')
            for i in range(min(5, len(lines))):
                line = lines[i].strip()
                if line and len(line) > 3 and not re.search(r'(invoice|purchase order|p\.?o\.?|quotation|estimate)', line, re.IGNORECASE):
                    self.extracted_data['client_info']['name'] = line
                    break
        
        # Extract phone number
        phone_patterns = [
            r'(?:Phone|Tel|Telephone)(?:\s*:)?\s*((?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4})',
            r'(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
        ]
        
        for pattern in phone_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                # Fix: Handle the case where group(1) doesn't exist
                if match.lastindex and match.lastindex >= 1:
                    self.extracted_data['client_info']['phone'] = match.group(1).strip()
                else:
                    self.extracted_data['client_info']['phone'] = match.group(0).strip()
                break
        
        # Extract email
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        match = re.search(email_pattern, text)
        if match:
            self.extracted_data['client_info']['email'] = match.group(0)
        
        # Extract address
        address_patterns = [
            r'(?:Address|Location)(?:\s*:)?\s*([A-Za-z0-9\s,.#-]+(?:\n[A-Za-z0-9\s,.#-]+){1,3})',
            r'(?:BILL TO|SOLD TO):\s*(?:[A-Za-z0-9\s&.,]+)\n([A-Za-z0-9\s,.#-]+(?:\n[A-Za-z0-9\s,.#-]+){1,3})',
            r'^\S+[^\n]+\n(\d+[^@\n]+(?:\n[A-Za-z0-9\s,.#-]+){0,2})'  # Address after company name
        ]
        
        for pattern in address_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                address = match.group(1).strip()
                # Clean up address by removing excessive whitespace
                address = re.sub(r'\s+', ' ', address)
                self.extracted_data['client_info']['address'] = address
                break
    
    def _extract_ship_to(self, text):
        """Extract ship to information from text"""
        # Extract ship to name and address
        ship_to_patterns = [
            r'(?:SHIP TO|Deliver To|Shipping Address)(?:\s*:)?\s*([A-Za-z0-9\s&.,]+)(?:\n)([A-Za-z0-9\s,.#-]+(?:\n[A-Za-z0-9\s,.#-]+){0,3})',
            r'(?:SHIP TO|Deliver To|Shipping Address)(?:\s*:)?\s*([A-Za-z0-9\s&.,\n#-]+)'
        ]
        
        for pattern in ship_to_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                if match.lastindex >= 2:
                    self.extracted_data['ship_to']['name'] = match.group(1).strip()
                    address = match.group(2).strip()
                    # Clean up address by removing excessive whitespace
                    address = re.sub(r'\s+', ' ', address)
                    self.extracted_data['ship_to']['address'] = address
                else:
                    ship_to_info = match.group(1).strip()
                    lines = ship_to_info.split('\n')
                    if len(lines) > 0:
                        self.extracted_data['ship_to']['name'] = lines[0].strip()
                        if len(lines) > 1:
                            address = ' '.join(lines[1:])
                            self.extracted_data['ship_to']['address'] = address
                break
        
        # Extract ship to phone
        if 'name' in self.extracted_data['ship_to']:
            ship_to_section = text[text.find(self.extracted_data['ship_to']['name']):]
            phone_patterns = [
                r'(?:Phone|Tel|Telephone)(?:\s*:)?\s*((?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4})',
                r'(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
            ]
            
            for pattern in phone_patterns:
                match = re.search(pattern, ship_to_section, re.IGNORECASE)
                if match:
                    if match.lastindex and match.lastindex >= 1:
                        self.extracted_data['ship_to']['phone'] = match.group(1).strip()
                    else:
                        self.extracted_data['ship_to']['phone'] = match.group(0).strip()
                    break
    
    def _extract_po_details(self, text):
        """Extract PO details from text"""
        # Extract PO number - prioritize PO-16994 format
        po_pattern_direct = r'PO-\d+'
        match = re.search(po_pattern_direct, text)
        if match:
            self.extracted_data['po_details']['po_number'] = match.group(0)
        else:
            # Try alternative patterns
            po_number_patterns = [
                r'(?:P\.?O\.?|Purchase Order)(?:\s*Number|\s*#|\s*No\.?)?\s*:?\s*([A-Za-z0-9-]+)',
                r'(?:Order|Reference)(?:\s*Number|\s*#|\s*No\.?)?\s*:?\s*([A-Za-z0-9-]+)'
            ]
            
            for pattern in po_number_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    self.extracted_data['po_details']['po_number'] = match.group(1).strip()
                    break
        
        # Extract creation date
        creation_date_patterns = [
            r'(?:Date|Order Date|PO Date|Created|Creation Date)(?:\s*:)?\s*(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})',
            r'(?:Date|Order Date|PO Date|Created|Creation Date)(?:\s*:)?\s*(\d{1,2}\s+[A-Za-z]{3,}\s+\d{2,4})'
        ]
        
        for pattern in creation_date_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                date_str = match.group(1).strip()
                self.extracted_data['po_details']['creation_date'] = date_str
                break
        
        # Extract due date
        due_date_patterns = [
            r'(?:Due Date|Delivery Date|Required Date|Need By)(?:\s*:)?\s*(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})',
            r'(?:Due Date|Delivery Date|Required Date|Need By)(?:\s*:)?\s*(\d{1,2}\s+[A-Za-z]{3,}\s+\d{2,4})'
        ]
        
        for pattern in due_date_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                date_str = match.group(1).strip()
                self.extracted_data['po_details']['due_date'] = date_str
                break
        
        # Extract payment terms - ensure "Net 30" format without "VENDOR"
        payment_terms_patterns = [
            r'(?:Payment Terms|Terms)(?:\s*:)?\s*(Net\s+\d+)',
            r'(?:Payment Terms|Terms)(?:\s*:)?\s*([A-Za-z0-9\s]+)',
            r'(?:Net|Due)\s+(\d+)'
        ]
        
        for pattern in payment_terms_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                terms = match.group(1).strip()
                self.extracted_data['po_details']['payment_terms'] = terms
                break
        
        # Extract subtotal
        subtotal_patterns = [
            r'(?:Subtotal)(?:\s*:)?\s*\$?\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
            r'(?:Subtotal)(?:\s*:)?\s*(\$\s*\d{1,3}(?:,\d{3})*(?:\.\d{2})?)'
        ]
        
        for pattern in subtotal_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                subtotal_str = match.group(1).strip()
                # Remove currency symbol and commas
                subtotal_str = subtotal_str.replace('$', '').replace(',', '')
                try:
                    subtotal = float(subtotal_str)
                    self.extracted_data['po_details']['subtotal'] = subtotal
                except ValueError:
                    pass
                break
        
        # Extract tax
        tax_patterns = [
            r'(?:Tax|Sales Tax)(?:\s*\(\d+(?:\.\d+)?%\))?(?:\s*:)?\s*\$?\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
            r'(?:Tax|Sales Tax)(?:\s*\(\d+(?:\.\d+)?%\))?(?:\s*:)?\s*(\$\s*\d{1,3}(?:,\d{3})*(?:\.\d{2})?)'
        ]
        
        for pattern in tax_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                tax_str = match.group(1).strip()
                # Remove currency symbol and commas
                tax_str = tax_str.replace('$', '').replace(',', '')
                try:
                    tax = float(tax_str)
                    self.extracted_data['po_details']['tax'] = tax
                except ValueError:
                    pass
                break
        
        # Extract shipping
        shipping_patterns = [
            r'(?:Shipping|Freight|Delivery)(?:\s*:)?\s*\$?\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
            r'(?:Shipping|Freight|Delivery)(?:\s*:)?\s*(\$\s*\d{1,3}(?:,\d{3})*(?:\.\d{2})?)'
        ]
        
        for pattern in shipping_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                shipping_str = match.group(1).strip()
                # Remove currency symbol and commas
                shipping_str = shipping_str.replace('$', '').replace(',', '')
                try:
                    shipping = float(shipping_str)
                    self.extracted_data['po_details']['shipping'] = shipping
                except ValueError:
                    pass
                break
    
    def _extract_order_total(self, text):
        """Extract order total from text"""
        total_patterns = [
            r'(?:Total|Grand Total|Order Total|TOTAL)(?:\s*:)?\s*\$?\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
            r'(?:Total|Grand Total|Order Total|TOTAL)(?:\s*:)?\s*(\$\s*\d{1,3}(?:,\d{3})*(?:\.\d{2})?)'
        ]
        
        for pattern in total_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                total_str = match.group(1).strip()
                # Remove currency symbol and commas
                total_str = total_str.replace('$', '').replace(',', '')
                try:
                    total = float(total_str)
                    self.extracted_data['po_details']['total_amount'] = total
                except ValueError:
                    pass
                break
    
    def _extract_comments(self, text):
        """Extract comments from text"""
        comment_patterns = [
            r'(?:Comments|Notes|Special Instructions|COMMENTS)(?:\s*:)?\s*([A-Za-z0-9\s,.#-]+(?:\n[A-Za-z0-9\s,.#-]+){0,3})',
            r'(?:Comments|Notes|Special Instructions|COMMENTS)(?:\s*:)?\s*(.+)'
        ]
        
        for pattern in comment_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                comment = match.group(1).strip()
                self.extracted_data['po_details']['comments'] = comment
                break
    
    def _extract_from_tables(self, tables):
        """Extract data from tables"""
        if not tables:
            return
        
        # Find the table that likely contains line items
        line_items_table = self._find_line_items_table(tables)
        
        if line_items_table:
            self._extract_line_items(line_items_table)
    
    def _find_line_items_table(self, tables):
        """Find the table that likely contains line items"""
        # Look for tables with certain column headers
        line_item_headers = ['item', 'code', 'description', 'qty', 'quantity', 'price', 'amount', 'total']
        
        for table in tables:
            if not table:
                continue
            
            # Check if first row contains line item headers
            if isinstance(table[0], list):
                header_row = [str(cell).lower() for cell in table[0] if cell]
                
                # Count how many line item headers are present
                header_match_count = sum(1 for header in line_item_headers if any(header in cell for cell in header_row))
                
                if header_match_count >= 3:  # If at least 3 headers match
                    return table
        
        # If no table with matching headers found, return the largest table
        largest_table = None
        max_rows = 0
        
        for table in tables:
            if table and len(table) > max_rows:
                max_rows = len(table)
                largest_table = table
        
        return largest_table
    
    def _extract_line_items(self, table):
        """Extract line items from table"""
        if not table or len(table) < 2:  # Need at least header and one data row
            return
        
        # Convert table to DataFrame for easier processing
        df = pd.DataFrame(table)
        
        # Use first row as header
        df.columns = df.iloc[0]
        df = df[1:]  # Remove header row
        
        # Identify columns
        item_code_col = self._find_column(df, ['item', 'code', 'item code', 'sku', 'part', 'part number'])
        description_col = self._find_column(df, ['description', 'desc', 'item description', 'product', 'service'])
        quantity_col = self._find_column(df, ['qty', 'quantity', 'amount', 'units'])
        u<response clipped><NOTE>To save on context only part of this file has been shown to you. You should retry this tool after you have searched inside the file with `grep -n` in order to find the line numbers of what you are looking for.</NOTE>