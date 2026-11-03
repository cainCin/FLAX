import os
import sys
from PyPDF2 import PdfReader, PdfWriter

def extract_first_pages(pdf_path, output_dir="pdf_examples", num_pages=3):
    os.makedirs(output_dir, exist_ok=True)
    basename = os.path.basename(pdf_path)
    output_pdf_path = os.path.join(output_dir, f"example_{basename}")
    
    reader = PdfReader(pdf_path)
    writer = PdfWriter()
    
    for i in range(min(num_pages, len(reader.pages))):
        writer.add_page(reader.pages[i])
        
    with open(output_pdf_path, "wb") as f:
        writer.write(f)
    print(f"Extracted first {num_pages} pages of '{pdf_path}' to '{output_pdf_path}'.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python handle_pdf.py <pdf_file_path> [num_pages]")
        sys.exit(1)
    pdf_file = sys.argv[1]
    num_pages = int(sys.argv[2]) if len(sys.argv) > 2 else 3
    extract_first_pages(pdf_file, num_pages=num_pages)