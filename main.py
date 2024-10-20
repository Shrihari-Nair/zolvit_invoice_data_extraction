from extract import extract_invoice_data
import os
import glob

def main():
    dir_path = "./data/Jan to Mar"
    pdf_pattern = os.path.join(dir_path, '*.pdf')
    # Get a list of all PDF files in the directory
    pdf_files = glob.glob(pdf_pattern)
    # Loop through each PDF file and process it
    for pdf_file in pdf_files:
        print(pdf_file.split("/")[-1])
        extract_invoice_data(pdf_file)

if __name__ == "__main__":
    main()