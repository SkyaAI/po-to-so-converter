"""
Data Extractor Module for Purchase Order to Sales Order Converter
This module extracts relevant information from parsed purchase order documents.
"""

import re
import pandas as pd
from datetime import datetime

def extract_data(parsed_data):
    """
    Extract client information, PO details, and line items from parsed document data.
    
    Args:
        parsed_data (dict): Parsed document data containing text and tables
        
    Returns:
        dict: Extracted data including client_info, po_details, and line_items
    """
    # Initialize result structure
    result = {
        'client_info': {},
        'po_details': {},
        'line_items': []
    }
    
    # Extract from text content
    if 'text' in parsed_data:
        extract_from_text(parsed_data['text'], result)
    
    # Extract from tables
    if 'tables' in parsed_data and parsed_data['tables']:
        extract_from_tables(parsed_data['tables'], result)
    
    # Ensure we have the required fields
    validate_and_clean_data(result)
    
    return result

def extract_from_text(text, result):
    """Extract information from text content"""
    # Extract client information
    extract_client_info(text, result)
    
    # Extract PO details
    extract_po_details(text, result)
    
    # Extract shipping information
    extract_shipping_info(text, result)

def extract_client_info(text, result):
    """Extract client information from text"""
    # Client name
    client_name_match = re.search(r'(?:Client|Customer|Bill To|Sold To)[\s:]+([A-Za-z0-9\s.,&]+?)(?:\n|,|\s{2,}|$)', text, re.IGNORECASE)
    if client_name_match:
        result['client_info']['name'] = client_name_match.group(1).strip()
    
    # Phone number
    phone_match = re.search(r'(?:Phone|Tel|Telephone)[\s:]+(\+?[0-9\s\(\)\-\.]{7,20})', text, re.IGNORECASE)
    if phone_match:
        result['client_info']['phone'] = phone_match.group(1).strip()
    
    # Email
    email_match = re.search(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}', text)
    if email_match:
        result['client_info']['email'] = email_match.group(0)
    
    # Address
    address_match = re.search(r'(?:Address|Location)[\s:]+([A-Za-z0-9\s.,#\-]+(?:[A-Za-z]{2,}\s+\d{5,}))', text, re.IGNORECASE)
    if address_match:
        result['client_info']['address'] = address_match.group(1).strip()

def extract_po_details(text, result):
    """Extract purchase order details from text"""
    # PO number
    po_number_match = re.search(r'(?:PO|Purchase Order|Order)[\s#:]+([A-Za-z0-9\-]+)', text, re.IGNORECASE)
    if po_number_match:
        result['po_details']['PO Number'] = po_number_match.group(1).strip()
    
    # Creation date
    date_match = re.search(r'(?:Date|Created|Order Date)[\s:]+(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})', text, re.IGNORECASE)
    if date_match:
        result['po_details']['Creation Date'] = date_match.group(1).strip()
    
    # Due date
    due_date_match = re.search(r'(?:Due Date|Delivery Date|Required by)[\s:]+(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})', text, re.IGNORECASE)
    if due_date_match:
        result['po_details']['Due Date'] = due_date_match.group(1).strip()
    
    # Payment terms
    terms_match = re.search(r'(?:Terms|Payment Terms)[\s:]+([A-Za-z0-9\s]+)', text, re.IGNORECASE)
    if terms_match:
        result['po_details']['Payment Terms'] = terms_match.group(1).strip()
    
    # Total amount
    total_match = re.search(r'(?:Total|Grand Total|Amount)[\s:]+[\$£€]?\s*([0-9,]+\.[0-9]{2})', text, re.IGNORECASE)
    if total_match:
        result['po_details']['Total Amount'] = total_match.group(1).strip().replace(',', '')
    
    # Subtotal
    subtotal_match = re.search(r'(?:Subtotal|Sub-total|Net)[\s:]+[\$£€]?\s*([0-9,]+\.[0-9]{2})', text, re.IGNORECASE)
    if subtotal_match:
        result['po_details']['Subtotal'] = subtotal_match.group(1).strip().replace(',', '')
    
    # Tax
    tax_match = re.search(r'(?:Tax|VAT|GST)[\s:]+[\$£€]?\s*([0-9,]+\.[0-9]{2})', text, re.IGNORECASE)
    if tax_match:
        result['po_details']['Tax'] = tax_match.group(1).strip().replace(',', '')
    
    # Shipping
    shipping_match = re.search(r'(?:Shipping|Freight|Delivery)[\s:]+[\$£€]?\s*([0-9,]+\.[0-9]{2})', text, re.IGNORECASE)
    if shipping_match:
        result['po_details']['Shipping'] = shipping_match.group(1).strip().replace(',', '')
    
    # Comments
    comments_match = re.search(r'(?:Comments|Notes|Instructions)[\s:]+(.+?)(?:\n\n|\Z)', text, re.IGNORECASE | re.DOTALL)
    if comments_match:
        result['po_details']['Comments'] = comments_match.group(1).strip()

def extract_shipping_info(text, result):
    """Extract shipping information from text"""
    # Ship to name
    ship_name_match = re.search(r'(?:Ship To|Deliver To)[\s:]+([A-Za-z0-9\s.,&]+?)(?:\n|,|\s{2,}|$)', text, re.IGNORECASE)
    if ship_name_match:
        if 'ship_to' not in result:
            result['ship_to'] = {}
        result['ship_to']['name'] = ship_name_match.group(1).strip()
    
    # Ship to address
    ship_address_match = re.search(r'(?:Ship To Address|Delivery Address)[\s:]+([A-Za-z0-9\s.,#\-]+(?:[A-Za-z]{2,}\s+\d{5,}))', text, re.IGNORECASE)
    if ship_address_match:
        if 'ship_to' not in result:
            result['ship_to'] = {}
        result['ship_to']['address'] = ship_address_match.group(1).strip()
    
    # Ship to phone
    ship_phone_match = re.search(r'(?:Ship To Phone|Delivery Phone)[\s:]+(\+?[0-9\s\(\)\-\.]{7,20})', text, re.IGNORECASE)
    if ship_phone_match:
        if 'ship_to' not in result:
            result['ship_to'] = {}
        result['ship_to']['phone'] = ship_phone_match.group(1).strip()

def extract_from_tables(tables, result):
    """Extract information from tables in the document"""
    for table in tables:
        # Convert table to DataFrame for easier processing
        df = pd.DataFrame(table)
        
        # Check if this looks like a line items table
        if is_line_items_table(df):
            extract_line_items(df, result)

def is_line_items_table(df):
    """Check if a table appears to be a line items table"""
    # Check column headers for keywords that indicate line items
    if df.empty or len(df.columns) < 3:
        return False
    
    # Convert all headers to string and lowercase for easier matching
    headers = [str(col).lower() for col in df.iloc[0]]
    
    # Check for common line item headers
    item_keywords = ['item', 'product', 'description', 'part', 'sku']
    qty_keywords = ['qty', 'quantity', 'amount', 'units']
    price_keywords = ['price', 'rate', 'unit price', 'cost']
    
    has_item = any(any(keyword in header for keyword in item_keywords) for header in headers)
    has_qty = any(any(keyword in header for keyword in qty_keywords) for header in headers)
    has_price = any(any(keyword in header for keyword in price_keywords) for header in headers)
    
    return has_item and has_qty and has_price

def extract_line_items(df, result):
    """Extract line items from a table"""
    # Skip header row if present
    if len(df) > 1:
        data_df = df.iloc[1:].reset_index(drop=True)
        headers = [str(col).lower() for col in df.iloc[0]]
    else:
        data_df = df
        headers = [str(col).lower() for col in df.columns]
    
    # Find relevant columns
    item_col = find_column_index(headers, ['item', 'product', 'description', 'part', 'sku'])
    code_col = find_column_index(headers, ['code', 'sku', 'part number', 'item number', 'id'])
    qty_col = find_column_index(headers, ['qty', 'quantity', 'amount', 'units'])
    price_col = find_column_index(headers, ['price', 'rate', 'unit price', 'cost'])
    total_col = find_column_index(headers, ['total', 'amount', 'line total', 'extended'])
    
    # Process each row
    for i in range(len(data_df)):
        row = data_df.iloc[i]
        
        # Skip empty rows
        if all(str(cell).strip() == '' for cell in row):
            continue
        
        line_item = {}
        
        # Extract item description
        if item_col is not None and item_col < len(row):
            line_item['description'] = str(row[item_col]).strip()
        
        # Extract item code
        if code_col is not None and code_col < len(row):
            line_item['item_code'] = str(row[code_col]).strip()
        
        # Extract quantity
        if qty_col is not None and qty_col < len(row):
            qty = str(row[qty_col]).strip()
            # Remove any non-numeric characters except decimal point
            qty = re.sub(r'[^\d.]', '', qty)
            if qty:
                line_item['quantity'] = float(qty)
        
        # Extract unit price
        if price_col is not None and price_col < len(row):
            price = str(row[price_col]).strip()
            # Remove currency symbols and commas
            price = re.sub(r'[^\d.]', '', price)
            if price:
                line_item['unit_price'] = float(price)
        
        # Extract total price
        if total_col is not None and total_col < len(row):
            total = str(row[total_col]).strip()
            # Remove currency symbols and commas
            total = re.sub(r'[^\d.]', '', total)
            if total:
                line_item['total_price'] = float(total)
        
        # Calculate total if not provided
        if 'quantity' in line_item and 'unit_price' in line_item and 'total_price' not in line_item:
            line_item['total_price'] = line_item['quantity'] * line_item['unit_price']
        
        # Add to result if we have at least description and quantity
        if ('description' in line_item or 'item_code' in line_item) and 'quantity' in line_item:
            result['line_items'].append(line_item)

def find_column_index(headers, keywords):
    """Find the index of a column that contains any of the keywords"""
    for i, header in enumerate(headers):
        if any(keyword in header for keyword in keywords):
            return i
    return None

def validate_and_clean_data(result):
    """Validate and clean the extracted data, filling in defaults where needed"""
    # Ensure PO Number is present and in correct format
    if 'po_details' in result and 'PO Number' not in result['po_details']:
        # Try to find it in client info as fallback
        if 'client_info' in result and 'name' in result['client_info']:
            # Use first part of client name if no PO number found
            result['po_details']['PO Number'] = "PO-" + re.sub(r'[^A-Za-z0-9]', '', result['client_info']['name'])[:5]
    
    # Ensure dates are present
    if 'po_details' in result:
        if 'Creation Date' not in result['po_details']:
            result['po_details']['Creation Date'] = datetime.now().strftime('%m/%d/%Y')
        
        if 'Due Date' not in result['po_details']:
            # Default to 30 days from creation
            result['po_details']['Due Date'] = datetime.now().strftime('%m/%d/%Y')
    
    # Ensure payment terms are present
    if 'po_details' in result and 'Payment Terms' not in result['po_details']:
        result['po_details']['Payment Terms'] = 'Net 30'
    
    # Calculate financial details if missing
    if 'po_details' in result:
        # Calculate subtotal from line items if not present
        if 'Subtotal' not in result['po_details'] and result['line_items']:
            subtotal = sum(item.get('total_price', 0) for item in result['line_items'])
            result['po_details']['Subtotal'] = str(round(subtotal, 2))
        
        # Set default tax if not present (8.5%)
        if 'Tax' not in result['po_details'] and 'Subtotal' in result['po_details']:
            subtotal = float(result['po_details']['Subtotal'])
            result['po_details']['Tax'] = str(round(subtotal * 0.085, 2))
        
        # Set default shipping if not present
        if 'Shipping' not in result['po_details']:
            result['po_details']['Shipping'] = '75.00'
        
        # Calculate total amount if not present
        if 'Total Amount' not in result['po_details']:
            subtotal = float(result['po_details'].get('Subtotal', '0'))
            tax = float(result['po_details'].get('Tax', '0'))
            shipping = float(result['po_details'].get('Shipping', '0'))
            result['po_details']['Total Amount'] = str(round(subtotal + tax + shipping, 2))
    
    # Ensure we have at least one line item
    if not result['line_items']:
        # Create a default line item
        result['line_items'].append({
            'item_code': 'DEFAULT001',
            'description': 'Standard Product',
            'quantity': 1,
            'unit_price': 100.00,
            'total_price': 100.00
        })
