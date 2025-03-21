import streamlit as st
import os
import tempfile
import pandas as pd
from document_parser import parse_document
from data_extractor import extract_data
from sales_order_generator import generate_sales_order
from csv_exporter import export_to_csv
import base64

# Handle missing dependencies gracefully
try:
    import pytesseract
    import pdf2image
    FULL_FUNCTIONALITY = True
except ImportError:
    FULL_FUNCTIONALITY = False
    st.warning("Some dependencies are missing. PDF and image processing may be limited.")

# Set page configuration
st.set_page_config(
    page_title="Purchase Order to Sales Order Converter",
    page_icon="📄",
    layout="wide"
)

# Function to download CSV files
def get_csv_download_link(file_path, link_text):
    with open(file_path, 'r') as f:
        csv_data = f.read()
    b64 = base64.b64encode(csv_data.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{os.path.basename(file_path)}">{link_text}</a>'
    return href

# Main app
def main():
    st.title("Purchase Order to Sales Order Converter")
    
    st.markdown("""
    This application converts purchase orders from clients into sales orders for your business.
    
    **Supported formats:**
    - PDF documents
    - Images (JPG, PNG, TIFF, BMP)
    - Excel spreadsheets (XLSX, XLS)
    - Word documents (DOCX, DOC)
    """)
    
    # File upload
    uploaded_file = st.file_uploader("Upload Purchase Order", type=["pdf", "jpg", "jpeg", "png", "tiff", "bmp", "xlsx", "xls", "docx", "doc"])
    
    if uploaded_file is not None:
        # Create a temporary file to save the uploaded file
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            temp_file_path = tmp_file.name
        
        st.success(f"File uploaded successfully: {uploaded_file.name}")
        
        # Process button
        if st.button("Process Purchase Order"):
            with st.spinner("Processing purchase order..."):
                try:
                    # Step 1: Parse document
                    st.info("Parsing document...")
                    parsed_data = parse_document(temp_file_path)
                    
                    # Step 2: Extract data
                    st.info("Extracting data...")
                    extracted_data = extract_data(parsed_data)
                    
                    # Step 3: Generate sales order
                    st.info("Generating sales order...")
                    sales_order_data = generate_sales_order(extracted_data)
                    
                    # Step 4: Export to CSV
                    st.info("Exporting to CSV...")
                    output_dir = tempfile.mkdtemp()
                    csv_paths = export_to_csv(sales_order_data, output_dir)
                    
                    st.success("Conversion complete!")
                    
                    # Display results
                    st.subheader("Extracted Information")
                    
                    # Client Information
                    st.markdown("### Client Information")
                    client_info = {}
                    client_info.update({f"Client {k}": v for k, v in sales_order_data.get('client_info', {}).items()})
                    client_info.update({k: v for k, v in sales_order_data.get('po_details', {}).items()})
                    client_info['SO Number'] = sales_order_data.get('so_number')
                    client_info['SO Date'] = sales_order_data.get('so_date')
                    
                    # Convert to DataFrame for display
                    client_df = pd.DataFrame([client_info]).T.reset_index()
                    client_df.columns = ['Field', 'Value']
                    st.dataframe(client_df, use_container_width=True)
                    
                    # Line Items
                    st.markdown("### Line Items")
                    if sales_order_data.get('line_items'):
                        line_items_df = pd.DataFrame(sales_order_data.get('line_items'))
                        st.dataframe(line_items_df, use_container_width=True)
                    else:
                        st.warning("No line items found in the purchase order.")
                    
                    # Download links
                    st.subheader("Download CSV Files")
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        if csv_paths.get('client_info_path'):
                            st.markdown(get_csv_download_link(csv_paths['client_info_path'], "Download Client Information CSV"), unsafe_allow_html=True)
                    
                    with col2:
                        if csv_paths.get('line_items_path'):
                            st.markdown(get_csv_download_link(csv_paths['line_items_path'], "Download Line Items CSV"), unsafe_allow_html=True)
                
                except Exception as e:
                    st.error(f"Error processing purchase order: {str(e)}")
                    st.error("Please make sure the file is a valid purchase order document.")
                
                finally:
                    # Clean up temporary files
                    if os.path.exists(temp_file_path):
                        os.unlink(temp_file_path)

if __name__ == "__main__":
    main()
