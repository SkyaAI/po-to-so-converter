#!/usr/bin/env python3
"""
Sales Order Generator Module for Purchase Order to Sales Order Conversion System

This module generates sales orders from extracted purchase order data:
- Generates sequential sales order numbers
- Creates client information record (Output 1)
- Creates line items record (Output 2)
- Links Output 1 and Output 2 via SO number
"""

import os
import json
import datetime
import re

class SalesOrderGenerator:
    """Generate sales orders from extracted PO data"""
    
    def __init__(self, config_path=None):
        self.config_path = config_path or os.path.join(os.path.dirname(os.path.abspath(__file__)), 'so_config.json')
        self.config = self._load_config()
        self.so_number = None
    
    def _load_config(self):
        """Load configuration from file or create default"""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        
        # Default configuration
        default_config = {
            'last_so_number': 0,
            'so_prefix': 'SO-',
            'so_number_format': '{prefix}{number:06d}'
        }
        
        # Save default configuration
        self._save_config(default_config)
        
        return default_config
    
    def _save_config(self, config):
        """Save configuration to file"""
        try:
            with open(self.config_path, 'w') as f:
                json.dump(config, f, indent=2)
        except IOError:
            print(f"Warning: Could not save configuration to {self.config_path}")
    
    def _generate_so_number(self):
        """Generate sequential sales order number"""
        # Increment last SO number
        self.config['last_so_number'] += 1
        
        # Format SO number
        so_number = self.config['so_number_format'].format(
            prefix=self.config['so_prefix'],
            number=self.config['last_so_number']
        )
        
        # Save updated configuration
        self._save_config(self.config)
        
        return so_number
    
    def generate(self, extracted_data):
        """Generate sales order from extracted data"""
        # Generate SO number
        self.so_number = self._generate_so_number()
        
        # Generate client information record (Output 1)
        client_info = self._generate_client_info(extracted_data)
        
        # Generate line items record (Output 2)
        line_items = self._generate_line_items(extracted_data)
        
        return {
            'so_number': self.so_number,
            'so_date': datetime.datetime.now().strftime('%Y-%m-%d'),
            'client_info': client_info,
            'po_details': extracted_data.get('po_details', {}),
            'ship_to': extracted_data.get('ship_to', {}),
            'line_items': line_items
        }
    
    def _generate_client_info(self, extracted_data):
        """Generate client information record (Output 1)"""
        client_info = {}
        
        # Add client information
        if 'client_info' in extracted_data:
            for key, value in extracted_data['client_info'].items():
                client_info[key] = value
        
        return client_info
    
    def _generate_line_items(self, extracted_data):
        """Generate line items record (Output 2)"""
        line_items = []
        
        if 'line_items' in extracted_data and extracted_data['line_items']:
            for item in extracted_data['line_items']:
                line_item = item.copy()  # Copy original line item
                line_items.append(line_item)
        
        return line_items

def generate_sales_order(extracted_data, config_path=None):
    """Unified interface for sales order generation"""
    generator = SalesOrderGenerator(config_path)
    return generator.generate(extracted_data)
