def compare_fields(gt_value, pred_value):
    """
    Compare two values and return 1 if they match, 0 otherwise.
    Handles cases where values may be strings or numbers.
    """
    return 1 if gt_value == pred_value else 0

def compare_json(ground_truth, predicted):
    """
    Compare two JSON objects field-by-field and return accuracy.
    This handles both simple and nested fields.
    """
    correct = 0
    total = 0
    field_accuracy = {}

    # Compare top-level fields (simple fields)
    simple_fields = ["company_name", "gst_number", "address", "mobile_number", "email", "invoice_number",
                     "invoice_date", "due_date", "customer_details", "place_of_supply", "taxable_amount",
                     "cgst_6", "sgst_6", "cgst_9", "sgst_9", "igst_12", "igst_18", "round_off", "total",
                     "total_discount", "total_in_words"]

    for field in simple_fields:
        total += 1
        field_accuracy[field] = compare_fields(ground_truth.get(field), predicted.get(field))
        correct += field_accuracy[field]

    # Compare total_items_qty
    total += 2  # Total Items and Total Qty
    field_accuracy["total_items_qty"] = {}
    field_accuracy["total_items_qty"]["Total Items"] = compare_fields(
        ground_truth["total_items_qty"]["Total Items"], predicted["total_items_qty"]["Total Items"])
    field_accuracy["total_items_qty"]["Total Qty"] = compare_fields(
        ground_truth["total_items_qty"]["Total Qty"], predicted["total_items_qty"]["Total Qty"])
    correct += field_accuracy["total_items_qty"]["Total Items"] + field_accuracy["total_items_qty"]["Total Qty"]

    # Compare bank_details
    total += 3  # Bank Name, Account Number, IFSC Code
    field_accuracy["bank_details"] = {}
    bank_fields = ["Bank Name", "Account Number", "IFSC Code"]
    for field in bank_fields:
        field_accuracy["bank_details"][field] = compare_fields(
            ground_truth["bank_details"][field], predicted["bank_details"][field])
        correct += field_accuracy["bank_details"][field]

    # Compare items
    total += len(ground_truth["items"]) * 7  # Each item has 7 fields to compare
    field_accuracy["items"] = []
    for i, gt_item in enumerate(ground_truth["items"]):
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

    # Calculate overall accuracy
    overall_accuracy = correct / total if total > 0 else 0
    return field_accuracy, overall_accuracy