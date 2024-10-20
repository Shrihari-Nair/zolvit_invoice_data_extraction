import json
import re
import os

def is_close(a, b, tolerance=1e-2):  # Set tolerance to 0.01 (1 cent)
    return abs(a - b) < tolerance

def validate_invoice_data(data):
    report = []
    
    # Check if 'items' exists in data
    if 'items' not in data or data['items'] is None:
        report.append("No items found in the invoice data.")
        return report  # Early exit if no items

    # Initialize variables to compute sums for verification
    total_taxable_value = 0
    total_amount = 0

    for item in data['items']:
        # Check if 'Rate / Item' key exists
        if 'Rate / Item' not in item:
            report.append(f"Item {item.get('Item Number', 'Unknown')}: Rate / Item key is missing.")
            continue
        
        # Extract relevant values, ensuring proper conversion
        base_rate = float(str(item['Rate / Item']['Base Rate']).replace(",", "")) if 'Base Rate' in item['Rate / Item'] else None
        discounted_rate = float(str(item['Rate / Item']['Discounted Rate']).replace(",", "")) if 'Discounted Rate' in item['Rate / Item'] else None
        discount_percentage = float(re.sub(r'%', '', item['Rate / Item'].get('Discount', '0%'))) / 100 if 'Discount' in item['Rate / Item'] else None
        qty_value = float(re.sub(r' BTL| STRP', '', item['Qty'])) if 'Qty' in item else None  # Clean and convert Qty to float
        taxable_value = float(str(item['Taxable Value']).replace(",", "")) if 'Taxable Value' in item else None
        tax_amount = float(str(item['Tax Amount']['Amount']).replace(",", "")) if 'Tax Amount' in item and 'Amount' in item['Tax Amount'] else None
        percentage = float(re.sub(r'%', '', item['Tax Amount'].get('Percentage', '0%'))) / 100 if 'Tax Amount' in item and 'Percentage' in item['Tax Amount'] else None

        # Perform checks only if all necessary values are present
        if None not in (base_rate, discounted_rate, discount_percentage, qty_value, taxable_value, tax_amount, percentage):
            # Check the base_rate condition
            if is_close(base_rate, (discounted_rate - (discount_percentage * discounted_rate))):
                report.append(f"Item {item['Item Number']}: Base Rate condition fulfilled.")
            else:
                report.append(f"Item {item['Item Number']}: Base Rate condition failed.")

            # Check the taxable_value condition
            calculated_taxable_value = qty_value * base_rate
            if is_close(taxable_value, calculated_taxable_value):
                report.append(f"Item {item['Item Number']}: Taxable Value condition fulfilled.")
            else:
                report.append(f"Item {item['Item Number']}: Taxable Value condition failed.")

            # Check the tax_amount condition
            calculated_tax_amount = taxable_value * percentage
            if is_close(tax_amount, calculated_tax_amount):
                report.append(f"Item {item['Item Number']}: Tax Amount condition fulfilled.")
            else:
                report.append(f"Item {item['Item Number']}: Tax Amount condition failed.")

            # Check the Amount condition
            amount = float(str(item['Amount']).replace(",", "")) if 'Amount' in item else None
            if amount is not None:
                calculated_total_amount = tax_amount + taxable_value
                if is_close(amount, calculated_total_amount):
                    report.append(f"Item {item['Item Number']}: Amount condition fulfilled.")
                else:
                    report.append(f"Item {item['Item Number']}: Amount condition failed.")

                # Accumulate totals
                total_taxable_value += taxable_value
                total_amount += amount
        else:
            report.append(f"Item {item.get('Item Number', 'Unknown')}: Missing values, skipping validation.")

    # Check if taxable_amount is the sum of all Amount present inside items
    if is_close(total_taxable_value, float(str(data.get('taxable_amount', '0')).replace(",", ""))):
        report.append("Taxable Amount condition fulfilled.")
    else:
        report.append("Taxable Amount condition failed.")

    # Check if total is the sum of taxable_amount + other taxes + round_off
    total_sum = (total_taxable_value + 
                 float(str(data.get('cgst_6', '0')).replace(",", "")) + 
                 float(str(data.get('sgst_6', '0')).replace(",", "")) + 
                 float(str(data.get('cgst_9', '0')).replace(",", "")) + 
                 float(str(data.get('sgst_9', '0')).replace(",", "")) + 
                 float(str(data.get('igst_12', '0')).replace(",", "")) + 
                 float(str(data.get('igst_18', '0')).replace(",", "")) + 
                 float(str(data.get('round_off', '0')).replace(",", "")))

    if is_close(total_sum, float(str(data.get('total', '0')).replace(",", ""))):
        report.append("Total condition fulfilled.")
    else:
        report.append("Total condition failed.")

    print(report)


def load_json_from_file(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

# Example usage
directory_path = './artifacts/json_dumps/regular_pdf_jsons'  # Change this to your directory
json_filename = 'INV-121_Jitesh Soni.json'  # Change this to your specific JSON file name
file_path = os.path.join(directory_path, json_filename)

try:
    invoice_data = load_json_from_file(file_path)
    report = validate_invoice_data(invoice_data)

    # Print the report
    for line in report:
        print(line)
except FileNotFoundError:
    print(f"File not found: {file_path}")
except json.JSONDecodeError:
    print(f"Error decoding JSON from the file: {file_path}")
except Exception as e:
    print(f"An error occurred: {str(e)}")