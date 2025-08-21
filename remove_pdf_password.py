from PyPDF2 import PdfReader, PdfWriter
import argparse
import getpass
import os
import sys
import logging
import shutil
from datetime import datetime

# Try to import PyCryptodome for AES support
try:
    from Crypto.Cipher import AES
    AES_AVAILABLE = True
except ImportError:
    AES_AVAILABLE = False
    logging.warning("PyCryptodome not available. AES-encrypted PDFs may not be supported.")

def setup_logging(verbose=False):
    """Setup logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('pdf_password_remover.log'),
            logging.StreamHandler()
        ]
    )

def validate_pdf_file(file_path):
    """Validate if the file is a PDF and accessible."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    if not file_path.lower().endswith('.pdf'):
        raise ValueError("File must be a PDF")
    
    if not os.access(file_path, os.R_OK):
        raise PermissionError(f"Cannot read file: {file_path}")
    
    # Basic PDF header check
    try:
        with open(file_path, 'rb') as f:
            header = f.read(4)
            if header != b'%PDF':
                raise ValueError("File does not appear to be a valid PDF")
    except Exception as e:
        raise ValueError(f"Cannot validate PDF file: {e}")

def create_backup(file_path, backup_dir=None):
    """Create a backup of the original file."""
    if backup_dir is None:
        backup_dir = os.path.dirname(file_path)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_name = os.path.splitext(os.path.basename(file_path))[0]
    backup_name = f"{base_name}_backup_{timestamp}.pdf"
    backup_path = os.path.join(backup_dir, backup_name)
    
    shutil.copy2(file_path, backup_path)
    logging.info(f"Backup created: {backup_path}")
    return backup_path

def add_password(input_pdf, output_pdf, user_password, owner_password=None, create_backup_flag=True, overwrite=False, permissions=None):
    """Add password protection to PDF file."""
    try:
        logging.info(f"Adding password protection to: {input_pdf}")
        
        # Validate input file
        validate_pdf_file(input_pdf)
        
        # Create backup if requested
        backup_path = None
        if create_backup_flag:
            try:
                backup_path = create_backup(input_pdf)
            except Exception as e:
                logging.warning(f"Could not create backup: {e}")
                if not input("Continue without backup? (y/N): ").lower().startswith('y'):
                    return False
        
        # Read the PDF
        reader = PdfReader(input_pdf)
        
        # Check if PDF is already encrypted
        if reader.is_encrypted:
            logging.warning("PDF is already password protected")
            print("Warning: This PDF is already password protected.")
            if not input("Continue anyway? This will re-encrypt the PDF. (y/N): ").lower().startswith('y'):
                return False
        
        # Check if output file exists and handle overwrite
        if os.path.exists(output_pdf) and not overwrite:
            if not input(f"Output file {output_pdf} exists. Overwrite? (y/N): ").lower().startswith('y'):
                return False
        
        # Create a new PDF writer
        writer = PdfWriter()
        total_pages = len(reader.pages)
        
        logging.info(f"Processing {total_pages} pages...")
        for i, page in enumerate(reader.pages):
            writer.add_page(page)
            if total_pages > 10 and i % 10 == 0:  # Progress for large files
                print(f"Processed {i+1}/{total_pages} pages...")
        
        # Set up encryption parameters
        if owner_password is None:
            owner_password = user_password
        
        # Default permissions if not specified
        if permissions is None:
            permissions = {
                'print': True,
                'modify': False,
                'copy': True,
                'annotate': True
            }
        
        # Apply encryption
        writer.encrypt(
            user_password=user_password,
            owner_password=owner_password,
            use_128bit=True,
            permissions_flag=_convert_permissions_to_flag(permissions)
        )
        
        # Save the encrypted PDF
        with open(output_pdf, "wb") as f:
            writer.write(f)
        
        logging.info(f"Successfully added password protection to PDF: {output_pdf}")
        print(f"Success! Password-protected PDF saved as: {output_pdf}")
        
        if backup_path:
            print(f"Backup saved as: {backup_path}")
        
        return True
        
    except Exception as e:
        logging.error(f"Error adding password to PDF: {str(e)}")
        print(f"An error occurred: {str(e)}")
        return False

def _convert_permissions_to_flag(permissions):
    """Convert permissions dict to PyPDF2 permissions flag."""
    # PyPDF2 permissions flag (simplified version)
    flag = 0
    if permissions.get('print', False):
        flag |= 4  # Print
    if permissions.get('modify', False):
        flag |= 8  # Modify contents
    if permissions.get('copy', False):
        flag |= 16  # Copy/extract text and graphics
    if permissions.get('annotate', False):
        flag |= 32  # Add or modify text annotations
    return flag

def remove_password(input_pdf, output_pdf, password, create_backup_flag=True, overwrite=False):
    """Remove password from PDF file with enhanced error handling and logging."""
    try:
        logging.info(f"Processing file: {input_pdf}")
        
        # Validate input file
        validate_pdf_file(input_pdf)
        
        # Create backup if requested
        backup_path = None
        if create_backup_flag:
            try:
                backup_path = create_backup(input_pdf)
            except Exception as e:
                logging.warning(f"Could not create backup: {e}")
                if not input("Continue without backup? (y/N): ").lower().startswith('y'):
                    return False
        
        # Read the encrypted PDF
        reader = PdfReader(input_pdf)
        
        # Check if PDF is encrypted
        if not reader.is_encrypted:
            logging.warning("PDF is not password protected")
            print("Warning: This PDF is not password protected.")
            return True
        
        # Attempt to decrypt
        if not reader.decrypt(password):        
            logging.error("Incorrect password provided")
            print("Error: Incorrect password. Please try again.")
            return False
        
        # Check if output file exists and handle overwrite
        if os.path.exists(output_pdf) and not overwrite:
            if not input(f"Output file {output_pdf} exists. Overwrite? (y/N): ").lower().startswith('y'):
                return False
        
        # Create a new PDF writer
        writer = PdfWriter()
        total_pages = len(reader.pages)
        
        logging.info(f"Processing {total_pages} pages...")
        for i, page in enumerate(reader.pages):
            writer.add_page(page)
            if total_pages > 10 and i % 10 == 0:  # Progress for large files
                print(f"Processed {i+1}/{total_pages} pages...")
        
        # Save the unlocked PDF
        with open(output_pdf, "wb") as f:
            writer.write(f)
        
        logging.info(f"Successfully removed password from PDF: {output_pdf}")
        print(f"Success! Unlocked PDF saved as: {output_pdf}")
        
        if backup_path:
            print(f"Backup saved as: {backup_path}")
        
        return True
        
    except Exception as e:
        logging.error(f"Error processing PDF: {str(e)}")
        print(f"An error occurred: {str(e)}")
        return False

def process_batch(file_list, password, output_dir=None, backup=True, overwrite=False, operation='remove', owner_password=None, permissions=None):
    """Process multiple PDF files for add/remove operations."""
    successful = []
    failed = []
    
    for input_file in file_list:
        print(f"\nProcessing: {input_file}")
        
        if output_dir:
            if operation == 'remove':
                output_file = os.path.join(output_dir, f"unlocked_{os.path.basename(input_file)}")
            else:  # add
                output_file = os.path.join(output_dir, f"protected_{os.path.basename(input_file)}")
        else:
            if operation == 'remove':
                output_file = f"unlocked_{input_file}"
            else:  # add
                output_file = f"protected_{input_file}"
        
        if operation == 'remove':
            success = remove_password(input_file, output_file, password, backup, overwrite)
        else:  # add
            success = add_password(input_file, output_file, password, owner_password, backup, overwrite, permissions)
            
        if success:
            successful.append(input_file)
        else:
            failed.append(input_file)
    
    print(f"\n=== Batch Processing Complete ===")
    print(f"Operation: {operation.title()} Password")
    print(f"Successful: {len(successful)}")
    print(f"Failed: {len(failed)}")
    
    if failed:
        print("Failed files:")
        for f in failed:
            print(f"  - {f}")

if __name__ == "__main__":
    # Set up command-line arguments
    parser = argparse.ArgumentParser(
        description="Add or remove passwords from PDF file(s).",
        epilog="Examples:\n"
               "  # Remove password\n"
               "  %(prog)s document.pdf --remove\n"
               "  %(prog)s *.pdf --remove --batch --output-dir ./unlocked\n"
               "\n"
               "  # Add password\n"
               "  %(prog)s document.pdf --add --password secret123\n"
               "  %(prog)s *.pdf --add --batch --password secret123 --output-dir ./protected\n"
               "\n"
               "  # Advanced options\n"
               "  %(prog)s file.pdf --add --password user123 --owner-password admin456 --no-print --no-modify",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # Positional arguments
    parser.add_argument("input", nargs="+", help="Path to input PDF file(s).")
    
    # Operation mode (mutually exclusive)
    mode_group = parser.add_mutually_exclusive_group(required=True)
    mode_group.add_argument("--add", action="store_true", help="Add password protection to PDF(s).")
    mode_group.add_argument("--remove", action="store_true", help="Remove password protection from PDF(s).")
    
    # Output options
    parser.add_argument("-o", "--output", help="Path to output file (single file mode) or directory (batch mode).")
    parser.add_argument("--output-dir", help="Output directory for batch processing.")
    
    # Password options
    parser.add_argument("-p", "--password", help="PDF password (will prompt if not provided).")
    parser.add_argument("--owner-password", help="Owner password (for add mode, defaults to user password).")
    
    # Permission options (for add mode)
    parser.add_argument("--no-print", action="store_true", help="Disable printing (add mode only).")
    parser.add_argument("--no-modify", action="store_true", help="Disable content modification (add mode only).")
    parser.add_argument("--no-copy", action="store_true", help="Disable copying/extracting (add mode only).")
    parser.add_argument("--no-annotate", action="store_true", help="Disable annotations (add mode only).")
    
    # Processing options
    parser.add_argument("--batch", action="store_true", help="Process multiple files.")
    parser.add_argument("--no-backup", action="store_true", help="Skip creating backup files.")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing output files without asking.")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose logging.")
    parser.add_argument("--version", action="version", version="PDF Password Manager v2.0")
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.verbose)
    
    # Determine operation
    operation = 'add' if args.add else 'remove'
    
    # Get password if not provided
    password = args.password
    if not password:
        if operation == 'add':
            password = getpass.getpass("Enter the password to protect the PDF: ")
        else:
            password = getpass.getpass("Enter the current PDF password: ")
    
    # Get owner password for add mode
    owner_password = args.owner_password
    if operation == 'add' and not owner_password:
        owner_response = input("Enter owner password (press Enter to use same as user password): ").strip()
        owner_password = owner_response if owner_response else password
    
    # Set up permissions for add mode
    permissions = None
    if operation == 'add':
        permissions = {
            'print': not args.no_print,
            'modify': not args.no_modify,
            'copy': not args.no_copy,
            'annotate': not args.no_annotate
        }
    
    # Process files
    if args.batch or len(args.input) > 1:
        # Batch processing
        output_dir = args.output_dir or args.output
        process_batch(args.input, password, output_dir, not args.no_backup, args.overwrite, 
                     operation, owner_password, permissions)
    else:
        # Single file processing
        input_file = args.input[0]
        
        # Determine output file name if not provided
        if args.output:
            output_file = args.output
        else:
            base_name = os.path.basename(input_file)
            if operation == 'add':
                output_file = f"protected_{base_name}"
            else:
                output_file = f"unlocked_{base_name}"
        
        # Process the file
        if operation == 'add':
            success = add_password(input_file, output_file, password, owner_password, 
                                 not args.no_backup, args.overwrite, permissions)
        else:
            success = remove_password(input_file, output_file, password, not args.no_backup, args.overwrite)
            
        sys.exit(0 if success else 1)