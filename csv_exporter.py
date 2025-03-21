#!/usr/bin/env python3
"""
CSV Export Module for Purchase Order to Sales Order Conversion System

This module exports sales order data to CSV files:
- Client information CSV (Output 1)
- Line items CSV (Output 2)
"""

import os
import csv
import pandas as pd

class CSVExporter:
    """Export sales order data to CSV files"""
    
    def __init__(self, output_dir=None):
        self.output_dir = output_dir or os.path.join(os.path.dirname(os.path.abspath(__file__)), 'output')
        os.makedirs(self.output_dir, exist_ok=True)
    
    def export(self, sales_order_data):
        """Export sales order data to CSV files"""
        # Export client information (Output 1)
        client_info_path = self._export_client_info(sales_order_data)
        
        # Export line items (Output 2)
        line_items_path = self._export_line_items(sales_order_data)
        
        return {
            'client_info_path': client_info_path,
            'line_items_path': line_items_path
        }
    
    def _export_client_info(self, sales_order_data):
        """Export client information to CSV (Output 1)"""
        if 'client_info' not in sales_order_data or not sales_order_data['client_info']:
            return None
        
        # Define output path
        so_number = sales_order_data.get('so_number', 'unknown')
        output_path = os.path.join(self.output_dir, f'client_info_{so_number}.csv')
        
        # Define field order for client information
        field_order = [
            'so_number',           # Sales Order number
            'so_date',             # Sales Order date
            'client_name',         # Client name
            'client_phone',        # Client phone
            'client_email',        # Client email
            'client_address',      # Client address
            'po_number',           # PO number
            'creation_date',       # PO creation date
            'due_date',            # PO due date
            'payment_terms',       # Payment terms
            'subtotal',            # Subtotal amount
            'tax',                 # Tax amount
            'shipping',            # Shipping amount
            'total_amount',        # Total amount
            'ship_to_name',        # Ship to name
            'ship_to_address',     # Ship to address
            'ship_to_phone',       # Ship to phone
            'comments'             # General comments
        ]
        
        # Prepare data for CSV
        client_info = sales_order_data['client_info']
        po_details = sales_order_data.get('po_details', {})
        ship_to = sales_order_data.get('ship_to', {})
        
        # Combine all data into a single row
        row_data = {}
        
        # Add client info fields
        for field in ['name', 'phone', 'email', 'address']:
            if field in client_info:
                row_data[f'client_{field}'] = client_info[field]
            else:
                row_data[f'client_{field}'] = ''
        
        # Add PO details fields
        for field in ['po_number', 'creation_date', 'due_date', 'payment_terms', 'subtotal', 'tax', 'shipping', 'total_amount', 'comments']:
            if field in po_details:
                row_data[field] = po_details[field]
            else:
                row_data[field] = ''
        
        # Add ship to fields
        for field in ['name', 'address', 'phone']:
            if field in ship_to:
                row_data[f'ship_to_{field}'] = ship_to[field]
            else:
                row_data[f'ship_to_{field}'] = ''
        
        # Add SO fields
        row_data['so_number'] = so_number
        row_data['so_date'] = sales_order_data.get('so_date', '')
        
        # Ensure all fields exist (with empty values if not present)
        for field in field_order:
            if field not in row_data:
                row_data[field] = ''
        
        # Write to CSV
        with open(output_path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=field_order)
            writer.writeheader()
            writer.writerow(row_data)
        
        return output_path
    
    def _export_line_items(self, sales_order_data):
        """Export line items to CSV (Output 2)"""
        if 'line_items' not in sales_order_data or not sales_order_data['line_items']:
            return None
        
        # Define output path
        so_number = sales_order_data.get('so_number', 'unknown')
        output_path = os.path.join(self.output_dir, f'line_items_{so_number}.csv')
        
        # Define field order for line items
        field_order = [
            'so_number',           # Sales Order number (link to Output 1)
            'item_code',           # Item code
            'description',         # Item description
            'quantity',            # Quantity
            'unit_price',          # Unit price
            'total_price',         # Total price for item
            'po_number',           # PO number
            'creation_date',       # PO creation date
            'due_date'             # PO due date (if any)
        ]
        
        # Prepare data for CSV
        line_items = sales_order_data['line_items']
        
        # Ensure all fields exist for each line item
        rows_data = []
        for item in line_items:
            row_data = {field: item.get(field, '') for field in field_order}
            # Add SO number to link with Output 1
            row_data['so_number'] = so_number
            rows_data.append(row_data)
        
        # Write to CSV
        with open(output_path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=field_order)
            writer.writeheader()
            writer.writerows(rows_data)
        
        return output_path

def export_to_csv(sales_order_data, output_dir=None):
    """Unified interface for CSV export"""
    exporter = CSVExporter(output_dir)
    return exporter.export(sales_order_data)
