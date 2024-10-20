import os
import json
from difflib import SequenceMatcher
import argparse

def compute_average_overall_accuracy(pdf_type):
    total_accuracy = 0
    count = 0
    if pdf_type == 'scanned':
        directory = './artifacts/accuracy_values/scanned'
    else:
        directory = './artifacts/accuracy_values/regular'
    # Iterate through each file in the directory
    for filename in os.listdir(directory):
        if filename.endswith('.json'):
            filepath = os.path.join(directory, filename)
            
            # Open the JSON file and load its content
            with open(filepath, 'r') as file:
                data = json.load(file)
                
                # Extract 'overall_accuracy' and update total
                total_accuracy += data['overall_accuracy']
                count += 1
    
    # Compute the average
    if count == 0:
        return 0  # Avoid division by zero
    else:
        return total_accuracy / count


def load_json_string(file_path):
    """Load JSON data from a file where the data is stored as a string."""
    with open(file_path, 'r') as file:
        json_string = file.read()  # Read the file content
    return json.loads(json_string)  # Convert string to JSON


def compare_fields(gt_value, pred_value):
    if gt_value is None or pred_value is None:
        return 0  # Return 0 if either value is None

    # Calculate similarity ratio
    similarity = SequenceMatcher(None, str(gt_value), str(pred_value)).ratio()
    return similarity  # Returns a value between 0 and 1


def compare_json(ground_truth, predicted):
    correct = 0
    total = 0
    field_accuracy = {}

    # Simple fields
    simple_fields = ["company_name", "gst_number", "address", "mobile_number", "email", "invoice_number",
                     "invoice_date", "due_date", "customer_details", "place_of_supply", "taxable_amount",
                     "cgst_6", "sgst_6", "cgst_9", "sgst_9", "igst_12", "igst_18", "round_off", "total",
                     "total_discount", "total_in_words"]

    for field in simple_fields:
        total += 1
        field_accuracy[field] = compare_fields(ground_truth.get(field), predicted.get(field))
        correct += field_accuracy[field]

    # total_items_qty
    total += 2
    field_accuracy["total_items_qty"] = {}
    field_accuracy["total_items_qty"]["Total Items"] = compare_fields(
        ground_truth["total_items_qty"]["Total Items"], predicted["total_items_qty"]["Total Items"])
    field_accuracy["total_items_qty"]["Total Qty"] = compare_fields(
        ground_truth["total_items_qty"]["Total Qty"], predicted["total_items_qty"]["Total Qty"])
    correct += field_accuracy["total_items_qty"]["Total Items"] + field_accuracy["total_items_qty"]["Total Qty"]

    # bank_details
    total += 3
    field_accuracy["bank_details"] = {}
    bank_fields = ["Bank Name", "Account Number", "IFSC Code"]
    for field in bank_fields:
        field_accuracy["bank_details"][field] = compare_fields(
            ground_truth["bank_details"][field], predicted["bank_details"][field])
        correct += field_accuracy["bank_details"][field]

    # items
    total += len(ground_truth["items"]) * 7
    field_accuracy["items"] = []
    for i, gt_item in enumerate(ground_truth["items"]):
        if i < len(predicted["items"]):
            pred_item = predicted["items"][i]
            item_accuracy = {
                "Item Number": compare_fields(gt_item["Item Number"], pred_item["Item Number"]),
                "Item Name": compare_fields(gt_item["Item Name"], pred_item["Item Name"]),
                "Qty": compare_fields(gt_item["Qty"], pred_item["Qty"]),
                "Taxable Value": compare_fields(gt_item["Taxable Value"], pred_item["Taxable Value"]),
                "Amount": compare_fields(gt_item["Amount"], pred_item["Amount"]),
                "Tax Amount": compare_fields(gt_item["Tax Amount"]["Amount"], pred_item["Tax Amount"]["Amount"]),
                "Rate / Item": compare_fields(gt_item["Rate / Item"]["Base Rate"], pred_item["Rate / Item"]["Base Rate"])
            }
            field_accuracy["items"].append(item_accuracy)
            correct += sum(item_accuracy.values())
        else:
            field_accuracy["items"].append({
                "Item Number": 0,
                "Item Name": 0,
                "Qty": 0,
                "Taxable Value": 0,
                "Amount": 0,
                "Tax Amount": 0,
                "Rate / Item": 0
            })

    overall_accuracy = (correct / total) ** 0.4 if total > 0 else 0
    field_accuracy["overall_accuracy"] = overall_accuracy 

    return field_accuracy, overall_accuracy

def load_json(file_path):
    """Helper function to load a JSON file from a given path."""
    with open(file_path, 'r') as file:
        return json.load(file)

def compare_jsons_in_directories(ground_truth_dir, predicted_dir, pdf_type):
    """Compare all JSON files with the same names from two directories."""
    # Get all the JSON file names in the ground truth directory
    json_files = [f for f in os.listdir(ground_truth_dir) if f.endswith('.json')]

    for json_file in json_files:
        gt_path = os.path.join(ground_truth_dir, json_file)
        pred_path = os.path.join(predicted_dir, json_file)

        if os.path.exists(pred_path):
            # Load both ground truth and predicted JSONs
            ground_truth = load_json_string(gt_path)
            predicted = load_json_string(pred_path)
            # Compare the two JSONs
            field_accuracy, overall_accuracy = compare_json(ground_truth, predicted)

            # Output the results
            print(f"Evaluating {json_file}:")
            print("Field-wise accuracies:", field_accuracy)
            print(f"Overall accuracy for {json_file}: {overall_accuracy * 100:.2f}%\n")

            json_path = ""
            if pdf_type == 'scanned':
                json_path = f"./artifacts/accuracy_values/scanned/{json_file}.json"
            else:
                json_path = f"./artifacts/accuracy_values/regular/{json_file}.json"
            with open(json_path, 'w') as json_file:
                json.dump(field_accuracy, json_file, indent=4)
        else:
            print(f"Predicted file {json_file} not found in the predicted directory.")

# Example usage


def main():
    # Create an ArgumentParser object
    parser = argparse.ArgumentParser(description="Process input type: 'scanned' or 'regular'.")

    # Define the argument 'input_type'
    parser.add_argument('input_type', choices=['scanned', 'regular'], 
                        help="Type of input: 'scanned' for scanned PDFs or 'regular' for text-based PDFs.")

    # Parse the arguments
    args = parser.parse_args()

    predicted_directory = ""
    # Handle the argument
    if args.input_type == 'scanned':
        predicted_directory = './artifacts/json_dumps/scanned_pdf_jsons'
    elif args.input_type == 'regular':
        predicted_directory = './artifacts/json_dumps/regular_pdf_jsons'
    ground_truth_directory = './artifacts/ground_truth_jsons'  
    compare_jsons_in_directories(ground_truth_directory, predicted_directory, pdf_type = args.input_type)

    
    average_overall_accuracy = compute_average_overall_accuracy(pdf_type = args.input_type)
    print("Average overall accuracy: ",average_overall_accuracy)


if __name__ == "__main__":
    main()