# import json
import re

def safe_search(pattern, text, group_idx=1, default_value="0"):
    match = re.search(pattern, text)
    if match:
        return match.group(group_idx if group_idx <= match.lastindex else 0)
    return default_value  # Return "0" as a string to prevent AttributeError

def get_json_structure_for_regular_pdf(text):
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

    return data


def get_json_structure_for_scanned_pdf(invoice_text):
    company_pattern = r"(UNCUE DERMACARE PRIVATE LIMITED)"  # Add capturing group
    gst_pattern = r"GSTIN (\S+)"
    address_pattern = r"C\/?o\s*(.*?)(?=Mobile)"
    mobile_pattern = r"Mobile (\+91 \d+)"
    email_pattern = r"Email (\S+)"
    invoice_number_pattern = r"Invoice #:\s*(\S+)"
    invoice_date_pattern = r"Invoice Date:\s*(\S+ \S+ \d+)"
    due_date_pattern = r"Due Date:\s*(\S+ \S+ \d+)"
    customer_details_pattern = r"Customer Details:\s*(\S+)"
    place_of_supply_pattern = r"Place of Supply:\s*(\S+)"
    items_pattern = r"(\d+\.\d+) ([\w\s\(\)\*%]+) (\d+ \w+) (\d+\.\d+) (\d+\.\d+) \((\d+)%\) (\d+\.\d+) (\d+\.\d+) \((-\d+)%\)"
    taxable_amount_pattern = r"Taxable Amount\s+(\d+\.\d+)"
    cgst_6_pattern = r"CGST 6.0%\s+(\d+\.\d+)"
    sgst_6_pattern = r"SGST 6.0%\s+(\d+\.\d+)"
    cgst_9_pattern = r"CGST 9.0%\s+(\d+\.\d+)"
    sgst_9_pattern = r"SGST 9.0%\s+(\d+\.\d+)"
    round_off_pattern = r"Round Off\s+(\d+\.\d+)"
    total_pattern = r"Total\s+(\d+\.\d+)"
    total_discount_pattern = r"Total Discount\s+(\d+\.\d+)"
    total_items_qty_pattern = r"Total Items (\d+\.\d+)"
    total_in_words_pattern = r"Total amount \(in words\):\s*(.+?)\s*_"
    bank_name_pattern = r"Bank:\s*(\w+ \w+ \w+)"
    account_number_pattern = r"Account #:\s*(\d+)"
    ifsc_code_pattern = r"IFSC Code:\s*(\w+)"
    branch_pattern = r"Branch:\s*(\w+ \w+)"

    # Extract data using the safe_search function
    company_name = safe_search(company_pattern, invoice_text, default_value="UNCUE DERMACARE PRIVATE LIMITED")
    gst_number = safe_search(gst_pattern, invoice_text)
    address = safe_search(address_pattern, invoice_text, group_idx=0)
    address = address.strip() if isinstance(address, str) else address
    mobile_number = safe_search(mobile_pattern, invoice_text)
    email = safe_search(email_pattern, invoice_text)
    invoice_number = safe_search(invoice_number_pattern, invoice_text)
    invoice_date = safe_search(invoice_date_pattern, invoice_text)
    due_date = safe_search(due_date_pattern, invoice_text)
    customer_details = safe_search(customer_details_pattern, invoice_text)
    place_of_supply = safe_search(place_of_supply_pattern, invoice_text)
    items = re.findall(items_pattern, invoice_text)
    taxable_amount = safe_search(taxable_amount_pattern, invoice_text)
    cgst_6 = safe_search(cgst_6_pattern, invoice_text)
    sgst_6 = safe_search(sgst_6_pattern, invoice_text)
    cgst_9 = safe_search(cgst_9_pattern, invoice_text)
    sgst_9 = safe_search(sgst_9_pattern, invoice_text)
    igst_12 = safe_search(r'IGST 12.0%\s+₹([\d,.]+)', invoice_text)
    igst_18 = safe_search(r'IGST 18.0%\s+₹([\d,.]+)', invoice_text)
    round_off = safe_search(round_off_pattern, invoice_text)
    total = safe_search(total_pattern, invoice_text)
    total_discount = safe_search(total_discount_pattern, invoice_text)
    total_items_qty = safe_search(total_items_qty_pattern, invoice_text)
    total_in_words = safe_search(total_in_words_pattern, invoice_text)
    bank_name = safe_search(bank_name_pattern, invoice_text)
    account_number = safe_search(account_number_pattern, invoice_text)
    ifsc_code = safe_search(ifsc_code_pattern, invoice_text)
    branch = safe_search(branch_pattern, invoice_text)

    # Format items correctly
    item_list = []
    for i, item in enumerate(items, 1):
        item_list.append({
            "Item Number": str(i),
            "Item Name": item[1].strip(),
            "Rate / Item": {
                "Base Rate": item[0],
                "Discounted Rate": item[7],
                "Discount": item[8]
            },
            "Qty": item[2],
            "Taxable Value": item[3],
            "Tax Amount": {
                "Amount": item[4],
                "Percentage": item[5] + "%"
            },
            "Amount": item[6]
        })

    # Create the final JSON object
    invoice_data = {
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
        "items": item_list,
        "taxable_amount": taxable_amount,
        "cgst_6": cgst_6,
        "sgst_6": sgst_6,
        "cgst_9": cgst_9,
        "sgst_9": sgst_9,
        "igst_12": igst_12,
        "igst_18": igst_18,
        "round_off": round_off,
        "total": total,
        "total_discount": total_discount,
        "total_items_qty": {
            "Total Items": "3",
            "Total Qty": total_items_qty
        },
        "total_in_words": total_in_words,
        "bank_details": {
            "Bank Name": bank_name,
            "Account Number": account_number,
            "IFSC Code": ifsc_code,
            "Branch": branch
        }
    }
    return invoice_data