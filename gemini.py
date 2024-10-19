import google.generativeai as genai
from dotenv import load_dotenv
import os
from pathlib import Path
import json

def image_format(image_path):
    img = Path(image_path)

    if not img.exists():
        raise FileNotFoundError(f"Could not find image: {img}")

    image_parts = [
        {
            "mime_type": "image/png", ## Mime type are PNG - image/png. JPEG - image/jpeg. WEBP - image/webp
            "data": img.read_bytes()
        }
    ]
    return image_parts

def gemini_output(model, image_path, system_prompt, user_prompt):

    image_info = image_format(image_path)
    input_prompt= [system_prompt, image_info[0], user_prompt]
    response = model.generate_content(input_prompt)
    return response.text

def gemini_response(image_path):
    load_dotenv()  # take environment variables from .env.

    os.getenv("GOOGLE_API_KEY")
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

    MODEL_CONFIG = {
    "temperature": 0.1,
    "top_p": 1,
    "top_k": 32,
    "max_output_tokens": 4096,
    }

    ## Safety Settings of Model
    safety_settings = [
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    }
    ]
    model = genai.GenerativeModel(model_name = "gemini-1.5-pro",
                              generation_config = MODEL_CONFIG,
                              safety_settings = safety_settings)

    system_prompt = """
               You are a specialist in comprehending receipts.
               Input images in the form of receipts will be provided to you,
               and your task is to respond to questions based on the content of the input image.
               """
    #system_prompt = "Convert Invoice data into json format with appropriate json tags as required for the data in image "

    user_prompt = """Convert Invoice data into json format with appropriate json tags as required for the data in image. 
                    Make sure the entire image is taken into account. Structure the table properly if available in the image
                    An example of the structure is below. structure is important, values can change.
                    {
    "company_name": "UNCUE DERMACARE PRIVATE LIMITED",
    "gst_number": "23AADCU2395N1ZY",
    "address": "KARUNA GUPTA KURELE, 1st Floor S.P Bungalow Ke Pichhe, Shoagpur Shahdol, Shahdol Shahdol, MADHYA PRADESH, 484001",
    "mobile_number": "+91 8585960963",
    "email": "ruhi@dermaq.in",
    "invoice_number": "INV-117",
    "invoice_date": "01 Feb 2024",
    "due_date": "29 Jan 2024",
    "customer_details": "Naman",
    "place_of_supply": "23-MADHYA PRADESH",
    "items": [
        {
            "Item Number": "1",
            "Item Name": "Kera M 5% Solution ",
            "Rate / Item": {
                "Base Rate": "492.86",
                "Discounted Rate": "616.07",
                "Discount": "-20%"
            },
            "Qty": "1 BTL",
            "Taxable Value": "492.86",
            "Tax Amount": {
                "Amount": "59.14",
                "Percentage": "12%"
            },
            "Amount": "552.00"
        },
        {
            "Item Number": "2",
            "Item Name": "Arachitol Nano (60k) 4*5ml  ",
            "Rate / Item": {
                "Base Rate": "299.58",
                "Discounted Rate": "340.43",
                "Discount": "-12%"
            },
            "Qty": "3 BTL",
            "Taxable Value": "898.73",
            "Tax Amount": {
                "Amount": "107.85",
                "Percentage": "12%"
            },
            "Amount": "1,006.58"
        },
        {
            "Item Number": "3",
            "Item Name": "Neurobion Forte - 30 tablets   ",
            "Rate / Item": {
                "Base Rate": "30.58",
                "Discounted Rate": "34.75",
                "Discount": "-12%"
            },
            "Qty": "3 STRP",
            "Taxable Value": "91.73",
            "Tax Amount": {
                "Amount": "16.51",
                "Percentage": "18%"
            },
            "Amount": "108.24"
        }
    ],
    "taxable_amount": "1,483.32",
    "cgst_6": "83.50",
    "sgst_6": "83.50",
    "cgst_9": "8.26",
    "sgst_9": "8.26",
    "igst_12": 0,
    "igst_18": 0,
    "round_off": "0.18",
    "total": "1,667.00",
    "total_discount": "290.02",
    "total_items_qty": {
        "Total Items": "3",
        "Total Qty": "7.000"
    },
    "total_in_words": "INR One Thousand, Six Hundred And Sixty-Seven Rupees Only.",
    "bank_details": {
        "Bank Name": "Kotak Mahindra Bank",
        "Account Number": "1146860541",
        "IFSC Code": "kkbk0000725",
        "Branch": "PUNE - CHINCHWAD"
    }
}

if the tag does not exist, return 0.
                
                    
                    """

    # user_prompt = """Show all the text visible in the image and make sure no word is missed. Create a json file such that key is the line number and value is the content of that line"""

    output = gemini_output(model, image_path, system_prompt, user_prompt)
    start_index = output.find('{')
    print(type(output))
    print(output)
    output = output.strip()
    if start_index != -1:
        output = output[start_index:]
        try:
            data_dict = json.loads(output)
            # Print the dictionary and its type
            print(data_dict)  # This will print the dictionary format
            print(type(data_dict))  # This will show <class 'dict'>
            return data_dict
        except json.JSONDecodeError as e:
            print(f"Failed to decode JSON: {e}")
    else:
        print("No valid JSON found.")
