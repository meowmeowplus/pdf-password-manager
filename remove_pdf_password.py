from pypdf2 import PdfReader, PdfWriter
import argparse
import getpass
import os

def remove_password(input_pdf, output_pdf, password):
    try:
        # Read the encrypted PDF
        reader = PdfReader(input_pdf)
        if reader.is_encrypted:
            if not reader.decrypt(password):        
                print("Error: Incorrect password. Please try again.")
                return
        
        # Create a new PDF writer
        writer = PdfWriter()
        for page in reader.pages:
            writer.add_page(page)
        
        # Save the unlocked PDF
        with open(output_pdf, "wb") as f:
            writer.write(f)
        print(f"Success! Unlocked PDF saved as: {output_pdf}")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    # Set up command-line arguments
    parser = argparse.ArgumentParser(description="Remove password from a PDF file.")
    parser.add_argument("input", help="Path to the input PDF file.")
    parser.add_argument("-o", "--output", help="Path to the output unlocked PDF file. Defaults to 'unlocked_<input_filename>'.")
    args = parser.parse_args()

    # Determine output file name if not provided
    if not args.output:
        base_name = os.path.basename(args.input)
        args.output = f"unlocked_{base_name}"

    # Securely prompt for password
    password = getpass.getpass("Enter the PDF password: ")

    # Run the function
    remove_password(args.input, args.output, password)