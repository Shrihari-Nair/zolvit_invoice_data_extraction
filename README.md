# Zolvit Invoice Data Extraction 
## Setup 
1. Install conda and create a virtual environment
2. Run the following command : `pip install requirements.txt`. Ensure that the environment variables for `pytesseract` and `pdf2image` are added to the system's PATH.

## Repository Outline
```
|-- ./
    |-- .git/
    |-- .env
    |-- .gitignore
    |-- main.py
    |-- extract.py
    |-- accuracy_check.py
    |-- gemini.py
    |-- json_structure.py
    |-- README.md
    |-- requirements.txt
    |-- trust_determination.py
    |-- utils.py
    |-- artifacts/
        |-- ground_truth_jsons/
        |-- accuracy_values/
            |-- regular/
            |-- scanned/
        |-- ground_truth_jsons/
        |-- images/
        |-- invoice_snaps/
        |-- json_dumps/
            |-- regular_pdf_jsons/
            |-- scanned_pdf_jsons/
        |-- text_data/
    |-- data/
        |-- Jan to Mar/
    |-- notebooks/
```
- **`main.py`**: Acts as the entry point for the data extraction process, handling both regular and scanned PDFs.
- **`data` folder**: Contains the PDF files that are used for extraction purposes.
- **`extract.py`**: Contains the logic to determine whether a PDF is regular or scanned and applies the appropriate extraction algorithm accordingly.
- **`accuracy_check.py`**: Responsible for computing the accuracy of the extraction after the data is stored in JSON format, which is saved in the `artifacts/json_dumps` folder.
- **`json_structure.py`**: Converts the raw text extracted by `extract.py` into a structured JSON format. It compares this output with the manually created ground truth JSON files located in `artifacts/ground_truth_jsons`.
- **`trust_determination.py`**: Evaluates the quality of the extraction by cross-verifying the extracted data based on invoice logic and calculating various metrics present in the PDF.
- **`gemini.py`**: Demonstrates how large language models (LLMs) can consistently capture and structure data in an alternate manner.
- **`artifacts` folder**: Stores intermediate outputs such as extracted texts, images and `json` files containing accuracy values for each PDF.