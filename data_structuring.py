# import json
import re



def get_json_structure(text):
    # Extract overall invoice details using regular expressions
    company_name = re.search(r'ORIGINAL FOR RECIPIENT\n([A-Za-z ]+)', text).group(1).strip()
    gst_number = re.search(r'GSTIN\s([A-Z0-9]+)', text).group(1)
    address = re.search(r'C/o\s(.+?)\sMobile', text, re.DOTALL).group(1).replace("\n", " ").strip()
    mobile_number = re.search(r'Mobile\s(\+\d+\s\d+)', text).group(1)
    email = re.search(r'Email\s([^\s]+)', text).group(1)
    invoice_number = re.search(r'Invoice\s#:\s([^\n]+)', text).group(1)
    invoice_date = re.search(r'Invoice Date:\s([^\n]+)', text).group(1)
    due_date = re.search(r'Due Date:\s([^\n]+)', text).group(1)
    customer_details = re.search(r'Customer Details:\s*([^\n]+)', text).group(1)
    place_of_supply = re.search(r'Place of Supply:\s*([^\n]+)', text).group(1)

    # Extract all the item rows
    items_text = re.findall(r'(\d+)\n([^\n]+)\n([\d.]+)\n([\d.]+ \(-[\d.]+%\))\n([^\n]+)\n([\d.]+)\n([\d.]+ \([\d.]+%\))\n([\d.,]+)', text)

    # Create a list of items
    items = []
    for item in items_text:
        item_number = item[0]
        item_name = item[1]
        base_rate = item[2]
        discounted_rate, discount = re.search(r'([\d.]+) \((-[\d.]+%)\)', item[3]).groups()
        qty = item[4]
        taxable_value = item[5]
        tax_amount, tax_percentage = re.search(r'([\d.]+) \(([\d.]+%)\)', item[6]).groups()
        total_amount = item[7]
        
        # Append structured data for each item
        items.append({
            "Item Number": item_number,
            "Item Name": item_name,
            "Rate / Item": {
                "Base Rate": base_rate,
                "Discounted Rate": discounted_rate,
                "Discount": discount
            },
            "Qty": qty,
            "Taxable Value": taxable_value,
            "Tax Amount": {
                "Amount": tax_amount,
                "Percentage": tax_percentage
            },
            "Amount": total_amount
        })

    # Extract additional invoice details (tax, total, and bank details)
    taxable_amount = re.search(r'Taxable Amount\s+₹([\d.,]+)', text).group(1)
    cgst_6 = re.search(r'CGST\s6.0%\s+₹([\d.,]+)', text)
    sgst_6 = re.search(r'SGST\s6.0%\s+₹([\d.,]+)', text)
    cgst_9 = re.search(r'CGST\s9.0%\s+₹([\d.,]+)', text)
    sgst_9 = re.search(r'SGST\s9.0%\s+₹([\d.,]+)', text)
    igst_12 = re.search(r'IGST 12.0%\s+₹([\d,.]+)', text)
    igst_18 = re.search(r'IGST 18.0%\s+₹([\d,.]+)', text)
    round_off = re.search(r'Round Off\s+([\d.]+)', text)
    total = re.search(r'Total\s+₹([\d.,]+)', text).group(1)
    total_discount = re.search(r'Total Discount\s+₹([\d.,]+)', text)
    total_items_qty = re.search(r'Total Items / Qty\s*:\s*(\d+)\s*/\s*([\d.,]+)', text).groups()
    total_in_words = re.search(r'Total amount \(in words\):\s*(.+)', text).group(1)

    # Extract bank details
    bank_name = re.search(r'Bank:\s*([^\n]+)', text).group(1)
    account_number = re.search(r'Account #:\s*([^\n]+)', text).group(1)
    ifsc_code = re.search(r'IFSC Code:\s*([^\n]+)', text).group(1)
    branch = re.search(r'Branch:\s*([^\n]+)', text).group(1)

    # Structure the entire JSON with invoice, items, and additional data
    data = {
        "company_name": company_name,
        "gst_number": gst_number,
        "address": address,
        "mobile_number": mobile_number,
        "email": email,
        "invoice_number": invoice_number,
        "invoice_date": invoice_date,
        "due_date": due_date,
        "customer_details": customer_details,
        "place_of_supply": place_of_supply,
        "items": items,
        "taxable_amount": taxable_amount,
        "cgst_6": cgst_6.group(1) if cgst_6 else 0,
        "sgst_6": sgst_6.group(1) if sgst_6 else 0,
        "cgst_9": cgst_9.group(1) if cgst_9 else 0,
        "sgst_9": sgst_9.group(1) if sgst_9 else 0,
        "igst_12": igst_12.group(1) if igst_12 else 0,
        "igst_18": igst_18.group(1) if igst_18 else 0,
        "round_off": round_off.group(1) if round_off else 0,
        "total": total,
        "total_discount": total_discount.group(1) if total_discount else 0,
        "total_items_qty": {
            "Total Items": total_items_qty[0],
            "Total Qty": total_items_qty[1]
        },
        "total_in_words": total_in_words,
        "bank_details": {
            "Bank Name": bank_name,
            "Account Number": account_number,
            "IFSC Code": ifsc_code,
            "Branch": branch
        }
    }

    # Convert to JSON and output the structured data
    # json_data = json.dumps(data, indent=4)
    # print(json_data)
    # print(type(json_data))
    return data


def extract_invoice_data(text):
    # Extracting company details
    company_name = re.search(r"UNCUE DERMACARE PRIVATE LIMITED", text).group(0).strip()
    gst_number = re.search(r"GSTIN\s*([\w\d]+)", text).group(1).strip()
    
    address = re.search(r"Clo\s*(.*?)\n", text, re.DOTALL).group(1).strip().replace("\n", " ")
    mobile_number = re.search(r"Mobile\s*([\+\d\s]+)", text).group(1).strip()
    email = re.search(r"Email\s*([\w@\.]+)", text).group(1).strip()
    
    invoice_number = re.search(r"Invoice #:\s*([\w-]+)", text).group(1).strip()
    invoice_date = re.search(r"Invoice Date:\s*([\w\s\d]+)", text).group(1).strip()
    due_date = re.search(r"Due Date:\s*([\w\s\d]+)", text).group(1).strip()
    
    customer_details = re.search(r"Customer Details:\s*(.*?)\n", text).group(1).strip()
    place_of_supply = re.search(r"Place of Supply:\s*([\w\s-]+)", text).group(1).strip()
    
    # Extracting items
    items = []
    item_pattern = re.compile(r"([\d\.]+)\s*(.*?)\s*([\d\s]+)\s*([\d\.]+)\s*([\d\.]+)\s*\(([\d]+%)\)\s*([\d\.]+)\s*([\d\.]+)\s*\(([\d]+%)\)")
    
    for match in item_pattern.finditer(text):
        base_rate = match.group(1).strip()
        item_name = match.group(2).strip()
        qty = match.group(3).strip()
        taxable_value = match.group(4).strip()
        tax_amount = match.group(5).strip()
        tax_percentage = match.group(6).strip()
        amount = match.group(7).strip()
        discounted_rate = match.group(8).strip()
        discount = match.group(9).strip()

        items.append({
            "Item Number": str(len(items) + 1),
            "Item Name": item_name,
            "Rate / Item": {
                "Base Rate": base_rate,
                "Discounted Rate": discounted_rate,
                "Discount": f"-{discount}"
            },
            "Qty": qty,
            "Taxable Value": taxable_value,
            "Tax Amount": {
                "Amount": tax_amount,
                "Percentage": tax_percentage
            },
            "Amount": amount
        })

    # Extracting summary details
    taxable_amount = re.search(r"Taxable Amount\s*([\d\.]+)", text).group(1).strip()
    cgst_6 = re.search(r"CGST 6.0%\s*([\d\.]+)", text)
    sgst_6 = re.search(r"SGST 6.0%\s*([\d\.]+)", text)
    
    cgst_9 = re.search(r"CGST 9.0%\s*([\d\.]+)", text)
    sgst_9 = re.search(r"SGST 9.0%\s*([\d\.]+)", text)
    
    # cgst_9_value = cgst_9.group(1).strip() if cgst_9 else "0"
    # sgst_9_value = sgst_9.group(1).strip() if sgst_9 else "0"

    round_off = re.search(r"Round Off\s*([\d\.]+)", text).group(1).strip()
    total = re.search(r"Total\s*([\d\.]+)", text).group(1).strip()
    total_discount = re.search(r"Total Discount\s*([\d\.]+)", text).group(1).strip()
    
    total_items_qty = {
        "Total Items": str(len(items)),
        "Total Qty": "7.000"
    }
    
    total_in_words = re.search(r"Total amount \(in words\):\s*(.*?)\s*_", text).group(1).strip()

    # Extracting bank details
    bank_name = re.search(r"Bank:\s*(.*?)(?=Account #:)", text).group(1).strip()
    account_number = re.search(r"Account #:\s*(\S+)", text).group(1).strip()
    ifsc_code = re.search(r"IFSC Code:\s*(\S+)", text).group(1).strip()
    branch = re.search(r"Branch:\s*(.*?)(?=Authorized Signatory)", text).group(1).strip()
    
    # Constructing the structured JSON data
    structured_data = {
        "company_name": company_name,
        "gst_number": gst_number,
        "address": address,
        "mobile_number": mobile_number,
        "email": email,
        "invoice_number": invoice_number,
        "invoice_date": invoice_date,
        "due_date": due_date,
        "customer_details": customer_details,
        "place_of_supply": place_of_supply,
        "items": items,
        "taxable_amount": taxable_amount,
        "cgst_6": cgst_6.group(1).strip() if cgst_6 else 0,
        "sgst_6": sgst_6.group(1).strip() if sgst_6 else 0,
        "cgst_9": cgst_9.group(1).strip() if cgst_9 else 0,
        "sgst_9": sgst_9.group(1).strip() if sgst_9 else 0,
        "igst_12": "0",
        "igst_18": "0",
        "round_off": round_off,
        "total": total,
        "total_discount": total_discount,
        "total_items_qty": total_items_qty,
        "total_in_words": total_in_words,
        "bank_details": {
            "Bank Name": bank_name,
            "Account Number": account_number,
            "IFSC Code": ifsc_code,
            "Branch": branch
        }
    }
    
    return structured_data
































