import json
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
    json_data = json.dumps(data, indent=4)
    print(json_data)
    return json_data































